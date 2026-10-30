import csv
import queue
import re
import statistics
import threading
import time
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from html.parser import HTMLParser
from tkinter import filedialog, messagebox, ttk
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen


BASE_URL = "https://webscraper.io/test-sites/e-commerce/static"
DEFAULT_TARGETS = {
    "全部分类": [
        f"{BASE_URL}/computers/laptops",
        f"{BASE_URL}/computers/tablets",
        f"{BASE_URL}/phones/touch",
    ],
    "Laptops": [f"{BASE_URL}/computers/laptops"],
    "Tablets": [f"{BASE_URL}/computers/tablets"],
    "Touch phones": [f"{BASE_URL}/phones/touch"],
}


@dataclass
class Product:
    category: str
    name: str
    price: float
    description: str
    reviews: int
    detail_url: str
    image_url: str


class ProductListParser(HTMLParser):
    """Parse product cards from WebScraper.io e-commerce test pages."""

    def __init__(self, page_url):
        super().__init__(convert_charrefs=True)
        self.page_url = page_url
        self.products = []
        self.pagination_links = set()
        self.current = None
        self.card_depth = 0
        self.capture = None
        self.text_parts = []
        self.link_for_title = None
        self.category = self._guess_category(page_url)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")

        if tag == "div" and self._has_class(classes, "thumbnail"):
            self.current = {
                "category": self.category,
                "name": "",
                "price": 0.0,
                "description": "",
                "reviews": 0,
                "detail_url": "",
                "image_url": "",
            }
            self.card_depth = 1
            return

        if self.current is not None:
            if tag in {"div", "h4", "p", "a"}:
                self.card_depth += 1

            if tag == "img" and not self.current["image_url"]:
                src = attrs.get("src", "")
                self.current["image_url"] = urljoin(self.page_url, src)

            if tag == "h4" and self._has_class(classes, "price"):
                self._begin_capture("price")
            elif tag == "a" and self._has_class(classes, "title"):
                self.link_for_title = urljoin(self.page_url, attrs.get("href", ""))
                self._begin_capture("name")
            elif tag == "p" and self._has_class(classes, "description"):
                self._begin_capture("description")
            elif tag == "p" and self._has_class(classes, "review-count"):
                self._begin_capture("reviews")
            return

        href = attrs.get("href", "")
        if href and self._looks_like_pagination(tag, attrs):
            self.pagination_links.add(urljoin(self.page_url, href))

    def handle_endtag(self, tag):
        if self.capture and tag in {"h4", "a", "p"}:
            value = " ".join("".join(self.text_parts).split())
            self._save_capture(value)
            self.capture = None
            self.text_parts = []

        if self.current is not None and tag in {"div", "h4", "p", "a"}:
            self.card_depth -= 1
            if self.card_depth <= 0:
                if self.current["name"]:
                    self.products.append(Product(**self.current))
                self.current = None
                self.link_for_title = None

    def handle_data(self, data):
        if self.capture:
            self.text_parts.append(data)

    def _begin_capture(self, field):
        self.capture = field
        self.text_parts = []

    def _save_capture(self, value):
        if self.capture == "price":
            self.current["price"] = parse_price(value)
        elif self.capture == "reviews":
            self.current["reviews"] = parse_int(value)
        else:
            self.current[self.capture] = value

        if self.capture == "name" and self.link_for_title:
            self.current["detail_url"] = self.link_for_title

    @staticmethod
    def _has_class(class_text, name):
        return name in class_text.split()

    @staticmethod
    def _looks_like_pagination(tag, attrs):
        classes = attrs.get("class", "")
        href = attrs.get("href", "")
        return tag == "a" and "page" in href and "disabled" not in classes

    @staticmethod
    def _guess_category(url):
        path = urlparse(url).path.strip("/").split("/")
        if len(path) >= 5:
            return path[-1].replace("-", " ").title()
        return "Unknown"


def parse_price(text):
    match = re.search(r"[\d.]+", text.replace(",", ""))
    return float(match.group(0)) if match else 0.0


def parse_int(text):
    match = re.search(r"\d+", text.replace(",", ""))
    return int(match.group(0)) if match else 0


def fetch_html(url, timeout=15):
    request = Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 WebScraperExperiment/1.0"
            )
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def scrape_products(seed_urls, max_pages, delay, status_callback=None, stop_event=None):
    visited = set()
    queue_urls = list(seed_urls)
    products = []
    seen_products = set()

    while queue_urls and len(visited) < max_pages:
        if stop_event and stop_event.is_set():
            break

        url = queue_urls.pop(0)
        if url in visited:
            continue

        visited.add(url)
        if status_callback:
            status_callback(f"正在抓取第 {len(visited)} 页：{url}")

        html = fetch_html(url)
        parser = ProductListParser(url)
        parser.feed(html)

        for product in parser.products:
            key = product.detail_url or f"{product.category}:{product.name}:{product.price}"
            if key not in seen_products:
                seen_products.add(key)
                products.append(product)

        for link in sorted(parser.pagination_links):
            if is_allowed_page(link) and link not in visited and link not in queue_urls:
                queue_urls.append(link)

        if delay > 0:
            time.sleep(delay)

    return products, len(visited)


def is_allowed_page(url):
    parsed = urlparse(url)
    return (
        parsed.netloc == "webscraper.io"
        and parsed.path.startswith("/test-sites/e-commerce/static/")
    )


def compute_stats(products):
    if not products:
        return {
            "count": 0,
            "avg_price": 0,
            "min_price": 0,
            "max_price": 0,
            "total_reviews": 0,
            "top_review": "",
            "by_category": {},
            "avg_by_category": {},
        }

    prices = [item.price for item in products]
    by_category = {}
    prices_by_category = {}

    for item in products:
        by_category[item.category] = by_category.get(item.category, 0) + 1
        prices_by_category.setdefault(item.category, []).append(item.price)

    top_review_product = max(products, key=lambda item: item.reviews)
    return {
        "count": len(products),
        "avg_price": statistics.mean(prices),
        "min_price": min(prices),
        "max_price": max(prices),
        "total_reviews": sum(item.reviews for item in products),
        "top_review": f"{top_review_product.name} ({top_review_product.reviews} reviews)",
        "by_category": by_category,
        "avg_by_category": {
            category: statistics.mean(values)
            for category, values in prices_by_category.items()
        },
    }


class ScraperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WebScraper.io 商品数据采集与统计分析")
        self.geometry("1180x760")
        self.minsize(980, 640)

        self.products = []
        self.filtered_indexes = []
        self.worker = None
        self.stop_event = threading.Event()
        self.ui_queue = queue.Queue()

        self.category_var = tk.StringVar(value="全部分类")
        self.max_pages_var = tk.IntVar(value=25)
        self.delay_var = tk.DoubleVar(value=0.2)
        self.search_var = tk.StringVar(value="")
        self.search_field_var = tk.StringVar(value="全部字段")
        self.status_var = tk.StringVar(value="准备就绪")

        self._configure_style()
        self._build_layout()
        self.after(100, self._poll_worker_messages)

    def _configure_style(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TButton", padding=(10, 6))
        style.configure("Header.TLabel", font=("Microsoft YaHei UI", 16, "bold"))
        style.configure("Metric.TLabel", font=("Microsoft YaHei UI", 11))
        style.configure("Treeview", rowheight=28)
        style.configure("Treeview.Heading", font=("Microsoft YaHei UI", 10, "bold"))

    def _build_layout(self):
        root = ttk.Frame(self, padding=14)
        root.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(root)
        header.pack(fill=tk.X)

        ttk.Label(header, text="WebScraper.io 商品采集实验系统", style="Header.TLabel").pack(
            side=tk.LEFT
        )
        ttk.Label(header, textvariable=self.status_var).pack(side=tk.RIGHT)

        controls = ttk.LabelFrame(root, text="采集设置", padding=12)
        controls.pack(fill=tk.X, pady=(12, 10))

        ttk.Label(controls, text="分类").grid(row=0, column=0, sticky=tk.W, padx=(0, 6))
        ttk.Combobox(
            controls,
            textvariable=self.category_var,
            values=list(DEFAULT_TARGETS.keys()),
            state="readonly",
            width=16,
        ).grid(row=0, column=1, sticky=tk.W, padx=(0, 14))

        ttk.Label(controls, text="最大页面数").grid(row=0, column=2, sticky=tk.W, padx=(0, 6))
        ttk.Spinbox(
            controls,
            from_=1,
            to=200,
            textvariable=self.max_pages_var,
            width=8,
        ).grid(row=0, column=3, sticky=tk.W, padx=(0, 14))

        ttk.Label(controls, text="间隔秒").grid(row=0, column=4, sticky=tk.W, padx=(0, 6))
        ttk.Spinbox(
            controls,
            from_=0,
            to=5,
            increment=0.1,
            textvariable=self.delay_var,
            width=8,
        ).grid(row=0, column=5, sticky=tk.W, padx=(0, 14))

        ttk.Label(controls, text="搜索数据").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        search_entry = ttk.Entry(controls, textvariable=self.search_var)
        search_entry.grid(
            row=1, column=1, columnspan=3, sticky=tk.EW, pady=(10, 0), padx=(0, 8)
        )
        search_entry.bind("<Return>", lambda event: self.apply_search())
        search_entry.bind("<KeyRelease>", lambda event: self.apply_search())

        search_field_box = ttk.Combobox(
            controls,
            textvariable=self.search_field_var,
            values=("全部字段", "商品名", "分类", "描述", "价格", "评论数"),
            state="readonly",
            width=10,
        )
        search_field_box.grid(row=1, column=4, sticky=tk.W, pady=(10, 0), padx=(0, 8))
        search_field_box.bind("<<ComboboxSelected>>", lambda event: self.apply_search())

        ttk.Button(controls, text="清空搜索", command=self.clear_search).grid(
            row=1, column=5, sticky=tk.W, pady=(10, 0), padx=(0, 14)
        )

        button_box = ttk.Frame(controls)
        button_box.grid(row=0, column=6, rowspan=2, sticky=tk.E)
        ttk.Button(button_box, text="开始采集", command=self.start_scrape).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(button_box, text="停止", command=self.stop_scrape).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_box, text="打开网页", command=self.open_selected_product).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        ttk.Button(button_box, text="导出 CSV", command=self.export_csv).pack(side=tk.LEFT)

        controls.columnconfigure(5, weight=1)

        content = ttk.PanedWindow(root, orient=tk.VERTICAL)
        content.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(content)
        stats_frame = ttk.Frame(content)
        content.add(table_frame, weight=3)
        content.add(stats_frame, weight=2)

        columns = ("category", "name", "price", "description", "reviews", "detail_url")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "category": "分类",
            "name": "商品名",
            "price": "价格",
            "description": "描述",
            "reviews": "评论数",
            "detail_url": "详情页",
        }
        widths = {
            "category": 110,
            "name": 180,
            "price": 80,
            "description": 360,
            "reviews": 80,
            "detail_url": 310,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor=tk.W)

        y_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.bind("<Double-1>", lambda event: self.open_selected_product())
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scroll.grid(row=0, column=1, sticky=tk.NS)
        x_scroll.grid(row=1, column=0, sticky=tk.EW)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        metrics = ttk.LabelFrame(stats_frame, text="统计结果", padding=12)
        metrics.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.metric_vars = {
            "count": tk.StringVar(value="商品数量：0"),
            "avg_price": tk.StringVar(value="平均价格：$0.00"),
            "minmax_price": tk.StringVar(value="价格范围：$0.00 - $0.00"),
            "reviews": tk.StringVar(value="评论总数：0"),
            "top_review": tk.StringVar(value="评论最多：-"),
        }
        for var in self.metric_vars.values():
            ttk.Label(metrics, textvariable=var, style="Metric.TLabel").pack(
                anchor=tk.W, pady=4
            )

        self.category_text = tk.Text(metrics, height=7, wrap=tk.WORD)
        self.category_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.category_text.insert(tk.END, "分类统计将在采集后显示。")
        self.category_text.configure(state=tk.DISABLED)

        chart_panel = ttk.LabelFrame(stats_frame, text="分类商品数量柱状图", padding=12)
        chart_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.chart = tk.Canvas(chart_panel, bg="white", highlightthickness=1, highlightbackground="#d8dee9")
        self.chart.pack(fill=tk.BOTH, expand=True)
        self.chart.bind("<Configure>", lambda event: self.draw_chart())

    def start_scrape(self):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("提示", "采集任务正在运行。")
            return

        self.products = []
        self.filtered_indexes = []
        self._refresh_table()
        self._refresh_stats()

        self.stop_event.clear()
        self.status_var.set("采集中...")

        seed_urls = self._get_seed_urls()
        if not seed_urls:
            messagebox.showwarning("缺少分类", "请选择一个 WebScraper.io 测试站商品分类。")
            self.status_var.set("准备就绪")
            return

        self.worker = threading.Thread(
            target=self._run_scraper,
            args=(seed_urls, self.max_pages_var.get(), self.delay_var.get()),
            daemon=True,
        )
        self.worker.start()

    def stop_scrape(self):
        self.stop_event.set()
        self.status_var.set("正在停止...")

    def export_csv(self):
        visible_products = self._visible_products()
        if not visible_products:
            if self.products:
                messagebox.showinfo("没有数据", "当前搜索结果为空，没有可导出的数据。")
            else:
                messagebox.showinfo("没有数据", "请先完成采集。")
            return

        path = filedialog.asksaveasfilename(
            title="导出 CSV",
            defaultextension=".csv",
            filetypes=[("CSV 文件", "*.csv"), ("所有文件", "*.*")],
            initialfile="webscraper_products.csv",
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file)
            writer.writerow(
                ["category", "name", "price", "description", "reviews", "detail_url", "image_url"]
            )
            for item in visible_products:
                writer.writerow(
                    [
                        item.category,
                        item.name,
                        f"{item.price:.2f}",
                        item.description,
                        item.reviews,
                        item.detail_url,
                        item.image_url,
                    ]
                )

        messagebox.showinfo("导出成功", f"已导出 {len(visible_products)} 条数据。")

    def _get_seed_urls(self):
        return DEFAULT_TARGETS.get(self.category_var.get(), [])

    def apply_search(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.filtered_indexes = list(range(len(self.products)))
        else:
            self.filtered_indexes = [
                index
                for index, product in enumerate(self.products)
                if self._matches_product(product, keyword)
            ]

        self._refresh_table()
        self._refresh_stats()
        if self.products:
            self.status_var.set(
                f"搜索结果：{len(self.filtered_indexes)} / {len(self.products)} 条"
            )

    def clear_search(self):
        self.search_var.set("")
        self.filtered_indexes = list(range(len(self.products)))
        self._refresh_table()
        self._refresh_stats()
        if self.products:
            self.status_var.set(f"已显示全部 {len(self.products)} 条商品")

    def open_selected_product(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("请选择商品", "请先在表格中选择一条商品数据。")
            return

        index = int(selection[0])
        product = self.products[index]
        if not product.detail_url:
            messagebox.showwarning("缺少链接", "当前商品没有可打开的详情页链接。")
            return

        webbrowser.open_new_tab(product.detail_url)
        self.status_var.set(f"已打开：{product.name}")

    def _matches_product(self, product, keyword):
        field = self.search_field_var.get()
        values = {
            "商品名": product.name,
            "分类": product.category,
            "描述": product.description,
            "价格": f"{product.price:.2f}",
            "评论数": str(product.reviews),
        }

        if field == "全部字段":
            search_text = " ".join(values.values())
        else:
            search_text = values.get(field, "")
        return keyword in search_text.lower()

    def _visible_products(self):
        return [self.products[index] for index in self.filtered_indexes]

    def _run_scraper(self, seed_urls, max_pages, delay):
        try:
            products, visited_count = scrape_products(
                seed_urls,
                max_pages=max_pages,
                delay=delay,
                status_callback=lambda text: self.ui_queue.put(("status", text)),
                stop_event=self.stop_event,
            )
            self.ui_queue.put(("done", products, visited_count))
        except (HTTPError, URLError, TimeoutError) as exc:
            self.ui_queue.put(("error", f"网络请求失败：{exc}"))
        except Exception as exc:
            self.ui_queue.put(("error", f"采集失败：{exc}"))

    def _poll_worker_messages(self):
        while True:
            try:
                message = self.ui_queue.get_nowait()
            except queue.Empty:
                break

            kind = message[0]
            if kind == "status":
                self.status_var.set(message[1])
            elif kind == "done":
                self.products = message[1]
                self.filtered_indexes = list(range(len(self.products)))
                if self.search_var.get().strip():
                    self.apply_search()
                    self.status_var.set(
                        f"完成：抓取 {message[2]} 页，匹配 {len(self.filtered_indexes)} / {len(self.products)} 条"
                    )
                else:
                    self._refresh_table()
                    self._refresh_stats()
                    self.status_var.set(
                        f"完成：抓取 {message[2]} 页，得到 {len(self.products)} 条商品"
                    )
            elif kind == "error":
                self.status_var.set("采集失败")
                messagebox.showerror("错误", message[1])

        self.after(100, self._poll_worker_messages)

    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        for index in self.filtered_indexes:
            item = self.products[index]
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    item.category,
                    item.name,
                    f"${item.price:.2f}",
                    item.description,
                    item.reviews,
                    item.detail_url,
                ),
            )

    def _refresh_stats(self):
        stats = compute_stats(self._visible_products())
        self.metric_vars["count"].set(f"商品数量：{stats['count']}")
        self.metric_vars["avg_price"].set(f"平均价格：${stats['avg_price']:.2f}")
        self.metric_vars["minmax_price"].set(
            f"价格范围：${stats['min_price']:.2f} - ${stats['max_price']:.2f}"
        )
        self.metric_vars["reviews"].set(f"评论总数：{stats['total_reviews']}")
        self.metric_vars["top_review"].set(f"评论最多：{stats['top_review'] or '-'}")

        lines = []
        for category, count in sorted(stats["by_category"].items()):
            avg_price = stats["avg_by_category"].get(category, 0)
            lines.append(f"{category}: {count} 件，平均价格 ${avg_price:.2f}")
        self.category_text.configure(state=tk.NORMAL)
        self.category_text.delete("1.0", tk.END)
        self.category_text.insert(tk.END, "\n".join(lines) if lines else "暂无分类统计。")
        self.category_text.configure(state=tk.DISABLED)
        self.draw_chart()

    def draw_chart(self):
        if not hasattr(self, "chart"):
            return

        self.chart.delete("all")
        stats = compute_stats(self.products)
        data = stats["by_category"]
        width = max(self.chart.winfo_width(), 300)
        height = max(self.chart.winfo_height(), 180)
        pad_left = 48
        pad_right = 24
        pad_top = 24
        pad_bottom = 48

        self.chart.create_line(pad_left, height - pad_bottom, width - pad_right, height - pad_bottom, fill="#4b5563")
        self.chart.create_line(pad_left, pad_top, pad_left, height - pad_bottom, fill="#4b5563")

        if not data:
            self.chart.create_text(width / 2, height / 2, text="暂无数据", fill="#6b7280")
            return

        max_value = max(data.values())
        bar_area_width = width - pad_left - pad_right
        bar_width = max(28, min(80, bar_area_width / max(len(data), 1) * 0.55))
        gap = bar_area_width / max(len(data), 1)
        colors = ["#2563eb", "#059669", "#d97706", "#7c3aed", "#dc2626"]

        for index, (category, count) in enumerate(sorted(data.items())):
            center_x = pad_left + gap * index + gap / 2
            bar_height = (height - pad_top - pad_bottom - 18) * count / max_value
            x1 = center_x - bar_width / 2
            y1 = height - pad_bottom - bar_height
            x2 = center_x + bar_width / 2
            y2 = height - pad_bottom
            color = colors[index % len(colors)]
            self.chart.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
            self.chart.create_text(center_x, y1 - 10, text=str(count), fill="#111827")
            self.chart.create_text(
                center_x,
                height - pad_bottom + 18,
                text=category,
                fill="#374151",
                width=gap - 6,
            )


if __name__ == "__main__":
    app = ScraperApp()
    app.mainloop()
