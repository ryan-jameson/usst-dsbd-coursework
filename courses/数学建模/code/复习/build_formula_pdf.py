from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Frame,
    FrameBreak,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "考试公式速查表.pdf"

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_REGULAR = FONT_DIR / "NotoSansSC-VF.ttf"
FONT_BOLD = FONT_DIR / "simhei.ttf"
FONT_MONO = FONT_DIR / "DejaVuSansMono_0.ttf"


def register_fonts():
    pdfmetrics.registerFont(TTFont("NotoSC", str(FONT_REGULAR)))
    pdfmetrics.registerFont(TTFont("NotoSC-Bold", str(FONT_BOLD)))
    pdfmetrics.registerFont(TTFont("MonoMath", str(FONT_MONO)))


def esc(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )


def make_doc():
    register_fonts()

    margin_x = 0.9 * cm
    margin_y = 0.75 * cm
    gap = 0.45 * cm
    page_w, page_h = A4
    col_w = (page_w - 2 * margin_x - gap) / 2
    frame_h = page_h - 2 * margin_y

    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=margin_y,
        bottomMargin=margin_y,
    )

    frames = [
        Frame(margin_x, margin_y, col_w, frame_h, id="left", showBoundary=0),
        Frame(margin_x + col_w + gap, margin_y, col_w, frame_h, id="right", showBoundary=0),
    ]

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("NotoSC", 7)
        canvas.setFillColor(colors.HexColor("#667085"))
        canvas.drawRightString(page_w - margin_x, 0.35 * cm, f"数学建模公式速查 · 第 {doc_.page} 页")
        canvas.restoreState()

    doc.addPageTemplates([PageTemplate(id="two_col", frames=frames, onPage=footer)])

    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "TitleCN",
            fontName="NotoSC-Bold",
            fontSize=17,
            leading=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#111827"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "Hint",
            fontName="NotoSC",
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#475467"),
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "Section",
            fontName="NotoSC-Bold",
            fontSize=10.5,
            leading=13,
            textColor=colors.white,
            backColor=colors.HexColor("#344054"),
            borderPadding=(3, 5, 3),
            spaceBefore=5,
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            "Body",
            fontName="NotoSC",
            fontSize=7.8,
            leading=10.2,
            textColor=colors.HexColor("#101828"),
            spaceAfter=1.5,
        )
    )
    styles.add(
        ParagraphStyle(
            "Formula",
            fontName="NotoSC",
            fontSize=7.2,
            leading=9.6,
            textColor=colors.HexColor("#0B4A6F"),
            spaceAfter=0,
        )
    )

    sections = [
        (
            "1 建模/优化/LP",
            [
                ("数学规划", "max/min f(x),  s.t. g_i(x) ≤ 0, h_j(x)=0, a_i ≤ x_i ≤ b_i"),
                ("多目标", "F(x)=w₁f₁(x)+w₂f₂(x)+...+wₖfₖ(x)"),
                ("LP", "max z=cᵀx,  s.t. Ax≤b, x≥0"),
                ("奶制品", "max z=72x₁+64x₂\nx₁+x₂≤50, 12x₁+8x₂≤480, 3x₁≤100, x≥0"),
                ("最优解", "x₁=20, x₂=30, z=3360"),
                ("影子价格", "shadow_i=Δz*/Δb_i；牛奶48，时间2，能力0"),
                ("0-1逻辑", "x⇒y: x≤y；x⇒¬y: x+y≤1；至多一: x+y≤1；至少一: x+y≥1；恰一: x+y=1"),
                ("指派/类别", "每任务: Σᵢxᵢⱼ=1；每人: Σⱼxᵢⱼ≤1；类别: Σ_{i∈C}xᵢ≥k"),
            ],
        ),
        (
            "2 初等/库存/救火",
            [
                ("匀加速", "v=at,  s=1/2·at²"),
                ("减速带", "s≈vmax²/(2a₁)+vmax²/(2|a₂|),  a=1/c；课件 s≈66.5m"),
                ("连续编号估计", "N≈(n+1)m/n−1；n=样本数，m=最大编号"),
                ("库存", "q(t)=Q−rt, Q=rT"),
                ("平均费用", "C(T)=c₁/T + c₂rT/2"),
                ("最优周期", "T*=√(2c₁/(c₂r)),  Q*=rT*"),
                ("敏感度", "S(T,c₁)=1/2, S(T,c₂)=−1/2, S(T,r)=−1/2"),
                ("森林救火", "min C(x)=c₁B(t₂)+c₂x(t₂−t₁)+c₃x；临界人数 β/λ"),
            ],
        ),
        (
            "3 Logistic/传染病/信息传播",
            [
                ("Logistic", "dx/dt = r x(1−x/N)"),
                ("捕捞", "dx/dt = r x(1−x/N) − Ex,  h(x)=Ex"),
                ("最大持续产量", "x*=N/2,  h_max≈rN/4"),
                ("SI", "s+i=1,  di/dt=λsi=λi(1−i)；i=1/2 时增长最快"),
                ("SIS", "di/dt=λsi−μi；λ>μ ⇒ i(∞)=1−μ/λ；λ<μ ⇒ i→0"),
                ("SIR", "ds/dt=−λsi,  di/dt=λsi−μi,  dr/dt=μi"),
                ("基本感染数", "σ=λ/μ=λ·(1/μ)；σs>1 增，σs<1 减"),
                ("信息传播", "pₖ₊₁−pₖ = c pₖ(N−pₖ),  c=Δpₖ/[pₖ(N−pₖ)]"),
            ],
        ),
        (
            "4 状态决策/遗传",
            [
                ("状态转移", "sᵢ₊₁=T(sᵢ,dᵢ)；商人过河: sᵢ₊₁=sᵢ+(−1)ⁱdᵢ"),
                ("商人状态", "s=(x,y),  d=(u,v),  1≤u+v≤2"),
                ("容许状态", "S={(3,y),(0,y), y=0..3} ∪ {(1,1),(2,2)}"),
                ("转移矩阵", "P=(pᵢⱼ),  pᵢⱼ=P(下一状态 j | 当前状态 i)"),
                ("遗传", "D=dd, H=dr, R=rr"),
                ("与H繁殖", "D-H=(1/2,1/2,0), H-H=(1/4,1/2,1/4), R-H=(0,1/2,1/2)"),
                ("条件概率", "P(D|DH)=1×1/2=1/2；P(R|HH)=1/2×1/2=1/4"),
            ],
        ),
        (
            "5 席位/投票/多属性",
            [
                ("Hamilton", "qᵢ=Npᵢ/P；先 floor(qᵢ)，余席按 rᵢ=qᵢ−floor(qᵢ) 补"),
                ("公平度", "每席代表人数 pᵢ/nᵢ 越接近越公平"),
                ("EP法", "Qᵢ=pᵢ/√[nᵢ(nᵢ+1)]；下一席给 Qᵢ 最大者"),
                ("Borda", "m个候选：第一名m分，最后1分，总分最高胜"),
                ("标准化", "最大化 rᵢⱼ=dᵢⱼ/maxᵢdᵢⱼ；归一化 rᵢⱼ=dᵢⱼ/Σᵢdᵢⱼ；模一化 rᵢⱼ=dᵢⱼ/√Σᵢdᵢⱼ²"),
                ("熵权", "Eⱼ=−kΣᵢrᵢⱼln rᵢⱼ, k=1/ln m；Fⱼ=1−Eⱼ；wⱼ=Fⱼ/ΣFⱼ"),
                ("SAW", "vᵢ=Σⱼwⱼrᵢⱼ"),
                ("WP", "vᵢ=∏ⱼdᵢⱼ^wⱼ；费用型权重取负"),
                ("TOPSIS", "vᵢⱼ=wⱼrᵢⱼ；Sᵢ⁺=√Σ(vᵢⱼ−vⱼ⁺)²；Sᵢ⁻=√Σ(vᵢⱼ−vⱼ⁻)²；Cᵢ=Sᵢ⁻/(Sᵢ⁺+Sᵢ⁻)"),
            ],
        ),
        (
            "6 AHP/超额售票",
            [
                ("AHP矩阵", "A=(aᵢⱼ), aᵢⱼ=wᵢ/wⱼ, aⱼᵢ=1/aᵢⱼ, aᵢᵢ=1"),
                ("AHP权重", "Aw=λ_max w；归一化 w"),
                ("一致性", "CI=(λ_max−n)/(n−1),  CR=CI/RI<0.1"),
                ("二项分布", "r~Bin(n+q,p),  f(r)=C(n+q,r)p^r(1−p)^(n+q−r)"),
                ("收益", "r≤q: S=s₁n−s₂(q−r)；r>q: S=s₁(n+q−r)"),
                ("期望收益", "E(q)=Σ_{r=0}^{n+q} S(r,q)f(r)"),
                ("最优q", "P(r≤q)=Σ_{r=0}^q C(n+q,r)p^r(1−p)^(n+q−r) ≥ s₁/(s₁+s₂)=1/(1+s)"),
                ("声誉约束", "P_j(q)=P(q−r>j)=Σ_{r=0}^{q−j−1}f(r) ≤ α"),
            ],
        ),
        (
            "7 概率/贝叶斯",
            [
                ("加法", "P(A∪B)=P(A)+P(B)−P(A∩B)；互斥: P(A∩B)=0"),
                ("乘法", "P(A∩B)=P(A)P(B|A)=P(B)P(A|B)"),
                ("独立", "P(B|A)=P(B),  P(A∩B)=P(A)P(B)"),
                ("全概率", "P(B)=ΣᵢP(Aᵢ)P(B|Aᵢ)"),
                ("贝叶斯", "P(Aᵢ|B)=P(Aᵢ)P(B|Aᵢ) / ΣₖP(Aₖ)P(B|Aₖ)"),
                ("朴素贝叶斯", "score(i)=P(Cᵢ)∏ⱼP(xⱼ|Cᵢ)；分数最大者为类别"),
                ("拉普拉斯", "P(x=是|C)=(次数+1)/(该类样本数+2)"),
                ("Warner", "P(C)=pP(A)+(1−p)(1−P(A));  p=[P(C)+P(A)−1]/[2P(A)−1]"),
                ("Simmons", "P(C)=pP(A)+p₀(1−P(A));  p=[P(C)−p₀(1−P(A))]/P(A)"),
            ],
        ),
        (
            "8 回归/PCA/博弈",
            [
                ("一元回归", "y=b₀+b₁x+ε,  ε~N(0,σ²)"),
                ("多元回归", "y=b₀+b₁x₁+...+bₖxₖ+ε"),
                ("交互项", "y=b₀+b₁x₁+b₂x₂+b₃x₁x₂+ε"),
                ("R²", "R²=1−SSR/SST=1−Σ(yᵢ−ŷᵢ)²/Σ(yᵢ−ȳ)²"),
                ("相关系数", "r_XY=Cov(X,Y)/√[Var(X)Var(Y)]"),
                ("假设检验", "p<α 或统计量落入拒绝域 W ⇒ 拒绝 H₀"),
                ("PCA", "Rᵢⱼ=Cov(Xᵢ,Xⱼ)/(σᵢσⱼ)；det(R−λI)=0；(R−λᵢI)vᵢ=0"),
                ("贡献率", "前k个主成分贡献率 = Σ_{i=1}^k λᵢ / Σᵢλᵢ"),
                ("博弈", "零和: u₂=−u₁；Nash: uᵢ(aᵢ*,a₋ᵢ*) ≥ uᵢ(aᵢ,a₋ᵢ*)"),
                ("报价博弈", "p_b≥p_s 时成交价 p=(p_b+p_s)/2；U_s=p−v_s, U_b=v_b−p"),
            ],
        ),
    ]

    story = []
    story.append(Paragraph("数学建模考试公式速查表", styles["TitleCN"]))
    story.append(Paragraph("按“看到题型 -> 想公式”排版；来自两份课程复习 PPT 的公式块。", styles["Hint"]))

    for title, items in sections:
        block = [Paragraph(title, styles["Section"])]
        rows = []
        for name, formula in items:
            rows.append(
                [
                    Paragraph(f"<b>{esc(name)}</b>", styles["Body"]),
                    Paragraph(esc(formula), styles["Formula"]),
                ]
            )
        table = Table(rows, colWidths=[2.2 * cm, col_w - 2.35 * cm], hAlign="LEFT")
        table.setStyle(
            TableStyle(
                [
                    ("FONTNAME", (0, 0), (-1, -1), "NotoSC"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2.6),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D5DD")),
                    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F2F4F7")),
                    ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#F8FBFF")),
                ]
            )
        )
        block.append(table)
        block.append(Spacer(1, 3))
        story.append(KeepTogether(block))

    doc.build(story)


if __name__ == "__main__":
    make_doc()
    print(OUT)
