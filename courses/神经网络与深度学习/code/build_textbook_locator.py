from __future__ import annotations

import html
import shutil
from pathlib import Path

import pdfplumber
from PIL import ImageOps
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "dlbook_cn_v0.5-beta.pdf"
TMP = ROOT / "tmp" / "pdfs" / "dlbook_locator"
OUTPUT_DIR = ROOT / "output" / "pdf"
OUTPUT = OUTPUT_DIR / "教材划重点定位.pdf"
ROOT_COPY = ROOT / "教材划重点定位.pdf"

FONT_REGULAR = Path(r"C:\Windows\Fonts\Deng.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\Dengb.ttf")

INK = colors.HexColor("#172033")
BLUE = colors.HexColor("#165D8C")
PALE_BLUE = colors.HexColor("#EAF4FA")
PALE_YELLOW = colors.HexColor("#FFF7D8")
MUTED = colors.HexColor("#5A6475")
LINE = colors.HexColor("#D6DEE8")
RED = colors.HexColor("#B33A3A")


CROPS = {
    "supervised": (120, (55, 185, 465, 605)),
    "underfit": (126, (55, 270, 465, 455)),
    "universal": (199, (55, 180, 465, 585)),
    "receptive_start": (339, (55, 490, 465, 608)),
    "receptive_end": (340, (55, 45, 465, 100)),
    "conv_formula": (311, (55, 140, 465, 545)),
    "conv_example": (312, (55, 55, 465, 385)),
    "pgm_definition": (503, (55, 235, 465, 430)),
    "directed": (508, (55, 50, 465, 210)),
    "directed_graph": (508, (55, 280, 465, 510)),
    "undirected": (510, (55, 95, 465, 305)),
    "undirected_graph": (511, (55, 50, 465, 155)),
    "gradient": (105, (55, 165, 465, 385)),
    "gen_disc": (238, (55, 155, 465, 275)),
    "linear": (122, (55, 345, 465, 555)),
    "normal": (124, (45, 40, 465, 130)),
    "bias": (124, (55, 360, 465, 515)),
    "polynomial": (126, (55, 450, 465, 605)),
    "rbf": (198, (55, 105, 465, 195)),
    "least_squares": (113, (55, 230, 465, 560)),
}


SECTIONS = [
    {
        "title": "1. 监督学习与无监督学习",
        "printed": "92",
        "pdf": "120",
        "where": "第5章 5.1.3“经验 E”，页面中下部",
        "hit": "教材直接给出两类学习的训练数据特征、学习目标和概率分布表述。",
        "mark": [
            "框出“无监督学习算法”整段：训练无标签特征数据，学习结构性质或 p(x)。",
            "框出“监督学习算法”整段：样本带标签/目标，由 x 预测 y，通常估计 p(y|x)。",
            "页边写：区别核心＝训练数据是否提供目标 y。",
        ],
        "study": [
            "监督学习：训练样本包含输入 x 和标签/目标 y，学习从 x 到 y 的预测关系。",
            "无监督学习：只观察 x，学习数据分布 p(x) 或其中有意义的结构，如密度估计、聚类。",
        ],
        "images": [("supervised", "原书截图：教材印刷第92页，监督/无监督的定义与概率表述")],
    },
    {
        "title": "2. 欠拟合、过拟合与模型容量",
        "printed": "98",
        "pdf": "126",
        "where": "第5章 5.2“容量、过拟合和欠拟合”，页面中部",
        "hit": "这是“机器学习常见问题”中最直接的两项，教材给出了可直接用于名词解释的定义。",
        "mark": [
            "横线标出：欠拟合＝模型不能在训练集上获得足够低的误差。",
            "横线标出：过拟合＝训练误差与测试误差之间的差距太大。",
            "圈出“容量”：模型拟合各种函数的能力；低容量易欠拟合，高容量易过拟合。",
        ],
        "study": [
            "判断顺序：先看训练误差是否足够低，再看训练误差与测试误差的差距。",
            "控制手段：选择合适的假设空间/模型容量，并结合正则化与验证集选模。",
        ],
        "images": [("underfit", "原书截图：教材印刷第98页，欠拟合、过拟合和容量")],
    },
    {
        "title": "3. 万能近似定理（考点中写作“通用近似定理”）",
        "printed": "171",
        "pdf": "199",
        "where": "第6章 6.4.1“万能近似性质和深度”，页面中下部",
        "hit": "教材术语为“万能近似定理”，与考点中的“通用近似定理”对应。",
        "mark": [
            "从“万能近似定理表明”开始，框到“任意连续函数……可以用神经网络来近似”。",
            "继续框出页面下部的限制：能表示不等于训练算法一定能学到。",
            "页边写：至少一层隐藏层＋合适激活＋足够隐藏单元＋任意精度近似。",
        ],
        "study": [
            "定理说明前馈网络具有强大的函数表示能力，不说明所需网络规模。",
            "定理也不保证训练成功；优化失败和过拟合都可能使学习失败。",
        ],
        "images": [("universal", "原书截图：教材印刷第171页，万能近似定理及其限制")],
    },
    {
        "title": "4. 感受野（卷积神经网络）",
        "printed": "311–312",
        "pdf": "339–340",
        "where": "第9章 9.10“卷积网络的神经科学基础”，跨页条目2",
        "hit": "教材用 V1 简单细胞解释感受野，并指出卷积检测器单元模拟这种局部响应。",
        "mark": [
            "印刷第311页底部从“V1包含许多简单细胞”开始划线。",
            "翻到印刷第312页，把“在一个小的空间位置感受野内的图像的线性函数”及下一句划完。",
            "页边写：某神经元/特征对输入空间中能够影响它的局部区域。",
        ],
        "study": [
            "浅层感受野较小；网络越深，组合多个局部运算后有效感受野通常越大。",
            "局部连接与权值共享使卷积网络能有效提取空间局部模式。",
        ],
        "images": [
            ("receptive_start", "原书截图1：教材印刷第311页，感受野句子的起始部分"),
            ("receptive_end", "原书截图2：教材印刷第312页，感受野句子的结尾"),
        ],
    },
    {
        "title": "5. 二维卷积运算",
        "printed": "283–284",
        "pdf": "311–312",
        "where": "第9章 9.1“卷积运算”，二维公式、互相关公式与图9.1",
        "hit": "教材同时给出二维数学卷积、机器学习常用互相关以及二维计算图。",
        "mark": [
            "框出式(9.4)：二维离散卷积的双重求和。",
            "框出式(9.6)和紧接其后的说明：很多机器学习库实现互相关但称为卷积。",
            "在图9.1旁写：CNN惯例通常不翻转卷积核。",
        ],
        "study": [
            "输出位置等于局部输入窗口与卷积核对应元素乘积之和。",
            "输出尺寸（无填充）：Hout=floor((H−Kh)/stride)+1，宽度同理；有填充时把 H 改为 H+2P。",
            "做题先确认：是否翻转核、步幅 stride、填充 padding。",
        ],
        "images": [
            ("conv_formula", "原书截图1：教材印刷第283页，二维卷积与互相关公式"),
            ("conv_example", "原书截图2：教材印刷第284页，图9.1二维卷积示例"),
        ],
    },
    {
        "title": "6. 概率图模型：有向图与无向图",
        "printed": "475、480、482–483",
        "pdf": "503、508、510–511",
        "where": "第16章开头；16.2.1“有向模型”；16.2.2“无向模型”",
        "hit": "“概率图（两个图）”最对应教材中的有向图模型和无向图模型。",
        "mark": [
            "印刷第475页框出：图模型用图描述随机变量之间的直接相互作用。",
            "印刷第480页圈出：有向图模型＝贝叶斯网络；边有方向；联合分布按父结点条件分布分解。",
            "印刷第482页圈出：无向图模型＝马尔可夫随机场；边无方向；不直接对应条件分布。",
            "重点看图16.2与图16.3，考试画图时结点表示随机变量、边表示直接相互作用。",
        ],
        "study": [
            "有向图：DAG；箭头表示依赖方向；p(x)=∏i p(xi|Pa(xi))。",
            "无向图：边无方向；用团上的非负因子描述变量间相容性，再通过归一化得到概率分布。",
        ],
        "images": [
            ("pgm_definition", "原书截图1：教材印刷第475页，结构化概率模型/图模型定义"),
            ("directed", "原书截图2：教材印刷第480页，有向图模型定义"),
            ("directed_graph", "原书截图3：教材印刷第480页，图16.2与有向分解式"),
            ("undirected", "原书截图4：教材印刷第482页，无向图模型定义"),
            ("undirected_graph", "原书截图5：教材印刷第483页，图16.3无向图示例"),
        ],
    },
    {
        "title": "7. 梯度下降：方向、更新式与停止条件",
        "printed": "77",
        "pdf": "105",
        "where": "第4章 4.3“基于梯度的优化方法”，页面上半部",
        "hit": "教材直接给出负梯度方向、更新式、学习率和收敛条件。",
        "mark": [
            "框出“梯度向量指向上坡，负梯度向量指向下坡”。",
            "重点标式(4.5)：x′=x−ε∇x f(x)，圈出 ε 是学习率。",
            "框出：梯度各元素为零（实践中接近零）时收敛。",
        ],
        "study": [
            "标准步骤：初始化参数→前向计算目标函数→求梯度→沿负梯度更新→检查停止条件并迭代。",
            "学习率太大可能振荡/发散，太小则收敛慢。",
        ],
        "images": [("gradient", "原书截图：教材印刷第77页，梯度下降定义、更新式和收敛条件")],
    },
    {
        "title": "8. 生成模型与判别模型",
        "printed": "210",
        "pdf": "238",
        "where": "第7章 7.6“半监督学习”，页面上部",
        "hit": "教材以概率建模目标给出两类模型最核心的区分。",
        "mark": [
            "圈出生成模型：P(x) 或 P(x,y)。",
            "圈出判别模型：P(y|x)。",
            "框出生成准则 −log P(x) 或 −log P(x,y)，以及判别准则 −log P(y|x)。",
        ],
        "study": [
            "生成模型学习数据分布或联合分布，可生成样本，也可由联合分布推断条件分布。",
            "判别模型直接学习条件分布或决策边界，重点服务于分类/回归预测。",
        ],
        "images": [("gen_disc", "原书截图：教材印刷第210页，生成与判别建模目标")],
    },
    {
        "title": "9. 线性回归模型与偏置项",
        "printed": "94、96",
        "pdf": "122、124",
        "where": "第5章 5.1.4“示例：线性回归”",
        "hit": "这是编程题的模型起点：预测、权重、偏置及增广特征写法。",
        "mark": [
            "印刷第94页框出式(5.3)：ŷ=wᵀx，并标出 w 是参数/权重向量。",
            "印刷第96页框出式(5.13)：ŷ=wᵀx+b。",
            "标出：给 x 增加一个恒为1的分量，可把偏置 b 并入权重向量。",
        ],
        "study": [
            "统一程序形式：构造设计矩阵 Φ，预测 ŷ=Φw；首列全1表示偏置。",
            "更换多项式或高斯基函数只是在更换 Φ 的列，最小二乘与梯度下降主体不变。",
        ],
        "images": [
            ("linear", "原书截图1：教材印刷第94页，线性回归模型"),
            ("bias", "原书截图2：教材印刷第96页，偏置项与增广特征"),
        ],
    },
    {
        "title": "10. 多项式基函数（教材表述：添加多项式特征）",
        "printed": "98",
        "pdf": "126",
        "where": "第5章 5.2“容量、过拟合和欠拟合”，页面下部",
        "hit": "书中没有使用“多项式基函数”这一短语，但明确给出把 x²、x 的更高次幂作为额外特征。",
        "mark": [
            "框出式(5.15)和式(5.16)：从一次模型扩展到二次模型。",
            "标出：模型对输入是二次函数，但对参数仍是线性的，因此可用正规方程。",
            "页边写设计矩阵一行：[1, x, x², …, xᴹ]。",
        ],
        "study": [
            "多项式阶数越高，模型容量越大；过高易过拟合，需用验证集选阶数或正则化。",
            "实现时用列堆叠构造 Φ，再调用同一套最小二乘或梯度下降求权重。",
        ],
        "images": [("polynomial", "原书截图：教材印刷第98页，多项式特征扩展及其线性参数性质")],
    },
    {
        "title": "11. 高斯基函数（教材对应：径向基函数 RBF）",
        "printed": "170",
        "pdf": "198",
        "where": "第6章 6.3.3后“其他常见隐藏单元类型”，页面上部",
        "hit": "教材没有“高斯基函数”原词；径向基函数的指数平方距离形式就是程序题所需的高斯/RBF形式。",
        "mark": [
            "框出“径向基函数（RBF）”及其指数平方距离公式。",
            "标出：输入 x 越接近中心/模板 W:,i，响应越大。",
            "页边写一维程序形式：φj(x)=exp(−(x−μj)²/(2σ²))。",
        ],
        "study": [
            "μj 是第 j 个基函数中心，σ 控制宽度；常在输入范围内均匀放置多个中心。",
            "设计矩阵列为各 RBF 的响应；可加首列1作为偏置，再用统一优化器求 w。",
        ],
        "images": [("rbf", "原书截图：教材印刷第170页，径向基函数及其局部响应性质")],
    },
    {
        "title": "12. 最小二乘：正规方程与梯度下降优化",
        "printed": "85、96",
        "pdf": "113、124",
        "where": "第4章 4.5“实例：线性最小二乘”；第5章线性回归正规方程",
        "hit": "两处正好对应编程题的两种优化：闭式最小二乘与迭代梯度下降。",
        "mark": [
            "印刷第85页框出目标 f(x)=1/2||Ax−b||² 和梯度 Aᵀ(Ax−b)。",
            "框出算法4.1的 while 循环和更新式。",
            "印刷第96页框出正规方程：w=(XᵀX)⁻¹Xᵀy。程序中优先用 solve 或 pinv，避免显式求逆。",
        ],
        "study": [
            "闭式法：w=pinv(Φ)y，代码短且无学习率；大规模问题可能代价高。",
            "梯度法：loss=(1/(2N))||Φw−y||²，grad=(1/N)Φᵀ(Φw−y)，循环 w←w−ηgrad。",
            "四项编程内容可统一为：选择基函数→构造 Φ→选择闭式法或梯度法→预测并计算 MSE。",
        ],
        "images": [
            ("least_squares", "原书截图1：教材印刷第85页，线性最小二乘目标、梯度和算法4.1"),
            ("normal", "原书截图2：教材印刷第96页，线性回归正规方程"),
        ],
    },
]


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Deng", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("DengBold", str(FONT_BOLD)))


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = []

    def showPage(self):
        self._states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._states)
        for state in self._states:
            self.__dict__.update(state)
            self._header_footer(total)
            super().showPage()
        super().save()

    def _header_footer(self, total: int) -> None:
        width, height = A4
        self.saveState()
        self.setTitle("深度学习教材划重点定位")
        self.setAuthor("依据 dlbook_cn_v0.5-beta.pdf 整理")
        if self._pageNumber > 1:
            self.setStrokeColor(LINE)
            self.line(16 * mm, height - 12 * mm, width - 16 * mm, height - 12 * mm)
            self.setFont("Deng", 8)
            self.setFillColor(MUTED)
            self.drawString(16 * mm, height - 9.5 * mm, "深度学习教材 · 考点划重点定位")
        self.setFont("Deng", 8)
        self.setFillColor(MUTED)
        self.drawCentredString(width / 2, 8 * mm, f"第 {self._pageNumber} / {total} 页")
        self.restoreState()


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle(
            "cover", parent=base["Title"], fontName="DengBold", fontSize=27,
            leading=38, alignment=TA_CENTER, textColor=INK, spaceAfter=12 * mm,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="Deng", fontSize=12,
            leading=20, alignment=TA_CENTER, textColor=MUTED,
        ),
        "h1": ParagraphStyle(
            "h1", parent=base["Heading1"], fontName="DengBold", fontSize=17,
            leading=24, textColor=INK, spaceAfter=4 * mm, keepWithNext=True,
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="DengBold", fontSize=11.5,
            leading=17, textColor=BLUE, spaceBefore=2 * mm, spaceAfter=1.5 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "body", parent=base["BodyText"], fontName="Deng", fontSize=9.6,
            leading=15.5, textColor=INK, spaceAfter=1.5 * mm, wordWrap="CJK",
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["BodyText"], fontName="Deng", fontSize=9.4,
            leading=15, leftIndent=5 * mm, firstLineIndent=-3.5 * mm,
            bulletIndent=1.5 * mm, textColor=INK, spaceAfter=1.2 * mm, wordWrap="CJK",
        ),
        "caption": ParagraphStyle(
            "caption", parent=base["Normal"], fontName="Deng", fontSize=8.2,
            leading=12, alignment=TA_CENTER, textColor=MUTED, spaceAfter=2.5 * mm,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontName="Deng", fontSize=8.5,
            leading=13, textColor=MUTED, wordWrap="CJK",
        ),
    }


def safe(text: str) -> str:
    return html.escape(text).replace("\n", "<br/>")


def render_crops() -> dict[str, Path]:
    crop_dir = TMP / "crops"
    crop_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    with pdfplumber.open(SOURCE) as pdf:
        for key, (page_no, bbox) in CROPS.items():
            out = crop_dir / f"{key}_pdf{page_no}.png"
            image = pdf.pages[page_no - 1].crop(bbox).to_image(resolution=190).original.convert("RGB")
            image = ImageOps.expand(image, border=5, fill="#B33A3A")
            image.save(out, quality=95)
            paths[key] = out
    return paths


def fit_image(path: Path, max_width=177 * mm, max_height=150 * mm) -> Image:
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    return image


def location_table(section: dict, st) -> Table:
    data = [
        [Paragraph("教材印刷页", st["small"]), Paragraph("PDF阅读器页", st["small"]), Paragraph("章节/页面位置", st["small"])],
        [Paragraph(safe(section["printed"]), st["body"]), Paragraph(safe(section["pdf"]), st["body"]), Paragraph(safe(section["where"]), st["body"])],
    ]
    table = Table(data, colWidths=[32 * mm, 34 * mm, 111 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PALE_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 2 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2 * mm),
    ]))
    return table


def callout(text: str, st, color=PALE_YELLOW) -> Table:
    table = Table([[Paragraph(safe(text), st["body"])]], colWidths=[177 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), color),
        ("BOX", (0, 0), (-1, -1), 0.7, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 3 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3 * mm),
    ]))
    return table


def add_bullets(story, items, st):
    for item in items:
        story.append(Paragraph("• " + safe(item), st["bullet"]))


def build_pdf(crops: dict[str, Path]) -> None:
    register_fonts()
    st = styles()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT), pagesize=A4,
        leftMargin=16 * mm, rightMargin=16 * mm,
        topMargin=17 * mm, bottomMargin=14 * mm,
        title="深度学习教材划重点定位",
        author="依据 dlbook_cn_v0.5-beta.pdf 整理",
    )
    story = []

    story.append(Spacer(1, 32 * mm))
    story.append(Paragraph("深度学习教材<br/>考试考点划重点定位", st["cover"]))
    story.append(Paragraph("逐考点页码 · 章节位置 · 划线建议 · 原书截图", st["subtitle"]))
    story.append(Spacer(1, 18 * mm))
    story.append(callout(
        "来源：dlbook_cn_v0.5-beta.pdf（738页）\n"
        "页码规则：本书正文“教材印刷页”＝“PDF阅读器页”−28。报告同时列出两种页码。\n"
        "使用方法：先按教材印刷页翻书，再按“书上怎么划”处理；红边图片为对应原书截取。",
        st, PALE_BLUE,
    ))
    story.append(Spacer(1, 13 * mm))
    story.append(Paragraph("收录原则", st["h2"]))
    add_bullets(story, [
        "只收录在这本教材中能够直接定位或有明确等价表述的考点。",
        "“通用近似定理”按教材术语“万能近似定理”定位。",
        "“多项式基函数”按教材的“添加多项式特征”定位；“高斯基函数”按“径向基函数（RBF）”定位。",
        "原书未找到完整“单层感知机训练算法/权重更新计算”，因此不放入正文。",
    ], st)
    story.append(PageBreak())

    story.append(Paragraph("快速索引", st["h1"]))
    index_rows = [[
        Paragraph("考点", st["small"]), Paragraph("教材印刷页", st["small"]),
        Paragraph("PDF页", st["small"]), Paragraph("最值得划的位置", st["small"]),
    ]]
    for sec in SECTIONS:
        index_rows.append([
            Paragraph(safe(sec["title"].split(". ", 1)[-1]), st["small"]),
            Paragraph(safe(sec["printed"]), st["small"]),
            Paragraph(safe(sec["pdf"]), st["small"]),
            Paragraph(safe(sec["where"]), st["small"]),
        ])
    table = Table(index_rows, colWidths=[48 * mm, 28 * mm, 25 * mm, 76 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8 * mm),
    ]))
    story.append(table)
    story.append(Spacer(1, 5 * mm))
    story.append(callout(
        "编程题统一主线：选择基函数（原始/多项式/RBF）→构造设计矩阵 Φ→用正规方程或梯度下降求 w→预测并计算 MSE。",
        st,
    ))

    for section in SECTIONS:
        story.append(PageBreak())
        story.append(Paragraph(safe(section["title"]), st["h1"]))
        story.append(location_table(section, st))
        story.append(Spacer(1, 3 * mm))
        story.append(Paragraph("定位结论", st["h2"]))
        story.append(callout(section["hit"], st))
        story.append(Paragraph("书上怎么划", st["h2"]))
        add_bullets(story, section["mark"], st)
        story.append(Paragraph("复习卡", st["h2"]))
        add_bullets(story, section["study"], st)
        story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=2 * mm, spaceAfter=3 * mm))
        for key, caption in section["images"]:
            story.append(fit_image(crops[key]))
            story.append(Paragraph(safe(caption), st["caption"]))

    doc.build(story, canvasmaker=NumberedCanvas)
    shutil.copy2(OUTPUT, ROOT_COPY)


if __name__ == "__main__":
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    crop_paths = render_crops()
    build_pdf(crop_paths)
    print(OUTPUT)
    print(ROOT_COPY)

