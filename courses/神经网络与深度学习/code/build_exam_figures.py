from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager


ROOT = Path(__file__).resolve().parent
TMP_DIR = ROOT / "tmp" / "pdfs"
FONT = Path(r"C:\Windows\Fonts\Deng.ttf")


def setup_font() -> None:
    prop = font_manager.FontProperties(fname=str(FONT))
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False


def draw_convolution(path: Path) -> None:
    x = np.array([[1, 2, 0, 1], [3, 1, 2, 2], [0, 1, 3, 1], [2, 2, 1, 0]])
    k = np.array([[1, 0], [-1, 1]])
    y = np.array([[-1, 3, 0], [4, 3, 0], [0, 0, 2]])
    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.7), gridspec_kw={"width_ratios": [1.2, 0.8, 1.0]})
    for ax, arr, title, cmap in zip(
        axes, [x, k, y], ["输入 X", "卷积核 K", "输出 Y"], ["Blues", "Oranges", "Greens"]
    ):
        ax.imshow(arr, cmap=cmap, vmin=float(arr.min()) - 0.5, vmax=float(arr.max()) + 0.5)
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                ax.text(j, i, str(arr[i, j]), ha="center", va="center", fontsize=14, color="#172033")
        ax.set_title(title, fontsize=14, pad=10)
        ax.set_xticks([]); ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#6B778A"); spine.set_linewidth(1.2)
    axes[0].add_patch(plt.Rectangle((-0.5, -0.5), 2, 2, fill=False, edgecolor="#D14D3F", linewidth=3))
    fig.suptitle("二维互相关示例（CNN 惯例：卷积核不翻转）", fontsize=16, fontweight="bold")
    fig.text(0.5, 0.02, "左上角：1×1 + 2×0 + 3×(-1) + 1×1 = -1", ha="center", fontsize=12)
    fig.tight_layout(rect=[0, 0.08, 1, 0.9])
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def node(ax, x: float, y: float, label: str, face: str = "#EAF4FC") -> None:
    circle = plt.Circle((x, y), 0.07, facecolor=face, edgecolor="#1F5F99", linewidth=1.7, zorder=3)
    ax.add_patch(circle)
    ax.text(x, y, label, ha="center", va="center", fontsize=10.5, fontweight="bold", zorder=4)


def arrow(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="->", color="#526170", lw=1.7))


def edge(ax, start: tuple[float, float], end: tuple[float, float]) -> None:
    ax.plot([start[0], end[0]], [start[1], end[1]], color="#526170", lw=1.7, zorder=1)


def draw_probability(path: Path) -> None:
    fig = plt.figure(figsize=(10.6, 6.3))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 0.9], hspace=0.42, wspace=0.25)
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_title("有向图：按‘节点 | 父节点’分解", fontsize=14, fontweight="bold")
    pos = {"A": (0.15, 0.5), "B": (0.42, 0.75), "C": (0.42, 0.25), "D": (0.72, 0.5)}
    for label, p in pos.items(): node(ax1, *p, label)
    for a, b in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]:
        sx, sy = pos[a]; ex, ey = pos[b]; dx, dy = ex - sx, ey - sy
        norm = (dx * dx + dy * dy) ** 0.5
        arrow(ax1, (sx + 0.075 * dx / norm, sy + 0.075 * dy / norm), (ex - 0.085 * dx / norm, ey - 0.085 * dy / norm))
    ax1.text(0.44, 0.02, "p(A,B,C,D)=p(A)p(B|A)p(C|A)p(D|B,C)", ha="center", fontsize=11)
    ax1.set_xlim(0, 0.9); ax1.set_ylim(-0.08, 1); ax1.axis("off")

    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_title("无向图：按最大团分解", fontsize=14, fontweight="bold")
    p2 = {"A": (0.2, 0.65), "B": (0.5, 0.65), "C": (0.5, 0.25), "D": (0.8, 0.25)}
    for label, p in p2.items(): node(ax2, *p, label, face="#FFF2DE")
    for a, b in [("A", "B"), ("B", "C"), ("C", "D")]: edge(ax2, p2[a], p2[b])
    ax2.text(0.5, 0.02, "p(x)=(1/Z)∏φ_c(x_c)", ha="center", fontsize=11)
    ax2.set_xlim(0, 1); ax2.set_ylim(-0.08, 1); ax2.axis("off")

    titles = ["链式 A→B→C", "共因 A←B→C", "共果 A→B←C"]
    dirs = [[("A", "B"), ("B", "C")], [("B", "A"), ("B", "C")], [("A", "B"), ("C", "B")]]
    notes = ["给 B 后：A、C 条件独立", "给 B 后：A、C 条件独立", "不给 B：A、C 独立；给 B 后相关"]
    for col in range(3):
        ax = fig.add_subplot(gs[1, col]); ax.set_title(titles[col], fontsize=12.5, fontweight="bold")
        p3 = {"A": (0.18, 0.55), "B": (0.5, 0.55), "C": (0.82, 0.55)}
        for label, p in p3.items(): node(ax, *p, label, face="#F5F7FA")
        for a, b in dirs[col]:
            sx, sy = p3[a]; ex, ey = p3[b]; sign = 1 if ex > sx else -1
            arrow(ax, (sx + 0.08 * sign, sy), (ex - 0.09 * sign, ey))
        ax.text(0.5, 0.12, notes[col], ha="center", fontsize=10.5)
        ax.set_xlim(0, 1); ax.set_ylim(0, 0.9); ax.axis("off")
    fig.suptitle("概率图读图与条件独立性", fontsize=17, fontweight="bold", y=0.98)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    setup_font()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    draw_convolution(TMP_DIR / "exam_convolution.png")
    draw_probability(TMP_DIR / "exam_probability.png")
