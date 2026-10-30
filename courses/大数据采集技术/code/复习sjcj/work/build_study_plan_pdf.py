from __future__ import annotations

from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Spacer

from build_review_pdfs import (
    ReviewDocTemplate,
    bullet,
    cover_story,
    make_styles,
    para,
    register_fonts,
    table_flow,
    toc_story,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "复习规划.pdf"
MARKDOWN = ROOT / "复习规划.md"


DAY1 = [
    ["09:00-09:30", "材料布置与诊断", "浏览《教材重点》2-8页；给教材贴5个章节页签；不看资料写出已知考点", "产出章节页签 + 10条初始薄弱点"],
    ["09:30-10:50", "第1章：概念框架", "《补充复习内容》4-5页；5V+1C、三层架构、5类关键技术、3类支撑技术、5种思维", "合上资料，3分钟口述完整框架"],
    ["11:00-12:00", "第1章：伦理、安全、战略", "典型伦理问题、治理对策、安全挑战；政策只记关键节点，不抄完整时间线", "完成一张“问题-对策”对照表"],
    ["14:00-16:10", "第2章：采集与分布式存储", "《补充复习内容》6-7页；采样/量化/编码，传统vs大数据，ETL，HDFS、HBase、Hive", "默写HDFS读写流程；完成3张比较表"],
    ["16:20-17:40", "第3章：日志采集", "《补充复习内容》8-9页；日志类型、应用场景、Flume、Scribe、两种分析工具", "60秒画出Flume Agent；说清Scribe容错"],
    ["19:30-20:20", "三章主动回忆", "不看资料写：5V+1C、HDFS组件、HBase组件、Flume三组件、Scribe流程", "正确率至少80%；错误写入错题/错概念表"],
    ["20:30-21:15", "开卷检索训练I", "随机抽5个关键词，在教材或两份讲义中定位；每题限时60秒", "5题中至少4题在60秒内找到"],
    ["21:20-22:00", "第6章预热计算", "习题卷P0题1、2、4、5、8；先做后对答案，不边做边看解析", "5题至少4题正确；标记错误原因"],
]


DAY2 = [
    ["09:00-10:50", "第5章：爬虫体系", "《补充复习内容》10-11页；抓取/更新策略、robots、爬虫类型、工具、requests/BeautifulSoup、反爬", "完成策略比较表 + robots语法卡"],
    ["11:00-12:00", "第5章主动回忆与检索", "闭卷画通用爬虫流程；比较通用/聚焦/深网/分布式；检索3个工具问题", "3分钟讲清爬虫体系；3次检索均低于60秒"],
    ["14:00-15:20", "第6章：公式与方法地图", "《补充复习内容》12-14页 + 公式汇总1-7页；统计、距离、清洗、集成、变换、规约", "一张A4公式选择表：题型 -> 公式 -> 条件"],
    ["15:30-16:30", "计算组A：相关与距离", "P0题9、11、12、14、15、16", "6题至少5题正确；单位和中间步骤完整"],
    ["16:40-17:40", "计算组B：规约与建模", "P0题17、19；有余力补18、20、23", "能解释Haar每一步和回归参数含义"],
    ["19:30-20:20", "计算组C：规范化与离散化", "P0题24、25、26、28、30", "5题至少4题正确；三种规范化不混淆"],
    ["20:30-21:20", "50分钟开卷模拟", "从18道P0题和10个检索题中混合抽题；全程按考试资料摆放", "记录每题耗时、定位路径、失分原因"],
    ["21:20-22:00", "最终修补与装包", "只处理红/黄项；复查页签、目录、公式、错题；停止扩展新内容", "五章均能3分钟口述；材料按使用顺序装好"],
]


CHAPTER_TARGETS = [
    ["第1章", "10%", "5V+1C；三层架构；关键/支撑技术；五种思维；伦理问题与治理", "补充4-5；教材重点4", "能列举、能分类、能做问题-对策匹配"],
    ["第2章", "25%", "采样/量化/编码；传统vs大数据；ETL；HDFS读写；HBase；Hive", "补充6-7；教材重点5", "能画流程、能比较、能说组件职责"],
    ["第3章", "15%", "日志分类与场景；Flume；Scribe；Event Log Analyzer；Log Parser", "补充8-9；教材重点6", "能画Agent与Scribe流程，能比较工具"],
    ["第5章", "20%", "抓取策略；robots；爬虫类型；四种工具；requests/BS；反爬", "补充10-11；教材重点7", "能选策略、解释流程、识别语法与工具"],
    ["第6章", "30%", "统计/距离；清洗；相关性；规范化；离散化；PCA/抽样/压缩", "补充12-14；教材重点8；公式1-7", "能选公式、写步骤、完成18道P0题"],
]


CALC_GROUPS = [
    ["数据清洗", "1、2、4、5、8", "均值/中位数填充、等频/等宽分箱、IQR", "第1天完成"],
    ["数据集成与距离", "9、11、12、14、15、16", "卡方、协方差、Pearson、Jaccard、数值距离、余弦", "第2天下午A"],
    ["规约与建模", "17、19", "Haar小波、线性回归", "第2天下午B"],
    ["变换", "24、25、26、28、30", "Min-Max、Z-score、小数定标、离散化、综合", "第2天晚上"],
    ["P1补充", "3、6、7、10、13、18、20、21、22、23、27、29", "同类题、综合题、直方图、属性选择、方法对比", "仅在P0正确率>=80%后"],
]


LOOKUP_DRILLS = [
    "HDFS读数据时，NameNode和DataNode分别负责什么？",
    "HBase与关系数据库在索引、存储和扩展上有什么区别？",
    "Flume的Source、Channel、Sink各自做什么？",
    "Scribe的Buffer Store如何实现故障恢复？",
    "robots.txt中User-agent、Disallow、Allow、*、$分别表示什么？",
    "深度优先、广度优先、OPIC和最佳优先如何选择？",
    "非对称二元属性为什么不计共同为0的t？",
    "Min-Max、Z-score、小数定标分别在什么条件下使用？",
    "数据质量六个维度是什么？",
    "大数据伦理问题与治理对策如何对应？",
]


def write_markdown() -> None:
    lines = [
        "# 两天复习规划",
        "",
        "> 默认每天约8-8.5小时有效复习；目标是核心概念能复述、流程比较能默写、公式能选用、资料能在60秒内定位。",
        "",
        "## 总原则",
        "",
        "- 每个知识块执行：20分钟理解 -> 5分钟合书回忆 -> 10分钟查漏并标页码。",
        "- 只抄结构、比较、公式和错因；不大段誊写教材或讲义。",
        "- 红色=不会，黄色=不稳定，绿色=能独立讲/做；每天结束只修红黄项。",
        "- 22:00停止学习，保证睡眠，不以熬夜换低质量阅读。",
        "",
        "## 第一天",
        "",
    ]
    lines.extend(md_table(["时间", "任务", "材料与重点", "验收"], DAY1))
    lines.extend(["", "## 第二天", ""])
    lines.extend(md_table(["时间", "任务", "材料与重点", "验收"], DAY2))
    lines.extend(["", "## 五章优先级", ""])
    lines.extend(md_table(["章节", "权重", "P0重点", "材料页码", "完成标准"], CHAPTER_TARGETS))
    lines.extend(["", "## 第六章计算安排", ""])
    lines.extend(md_table(["题组", "题号", "内容", "安排"], CALC_GROUPS))
    lines.extend(["", "## 60秒检索题", ""])
    lines.extend([f"{i}. {q}" for i, q in enumerate(LOOKUP_DRILLS, 1)])
    lines.extend(
        [
            "",
            "## 时间不足时的压缩方案",
            "",
            "- 每天只有4-5小时：保留第2章、第5章、第6章；第1/3章只做框架和工具比较。",
            "- 计算只做18道P0题；P1题全部取消。",
            "- 检索训练不能取消，至少完成10个关键词各一次。",
            "- 考前最后一小时只看公式选择表、比较表、错题和页签，不再读新内容。",
            "",
        ]
    )
    MARKDOWN.write_text("\n".join(lines), encoding="utf-8")


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|") for x in row) + " |")
    return out


def build_pdf() -> None:
    register_fonts()
    styles = make_styles()
    story = cover_story(
        "两天复习规划",
        "大数据采集技术｜开卷考试执行版",
        styles,
        [
            "默认强度：每天约8-8.5小时有效学习，09:00开始，22:00停止。",
            "最终目标：五章框架能复述；重点流程与比较能默写；18道P0计算题会做；关键词60秒内定位。",
            "材料组合：实体教材 + 教材重点.pdf + 补充复习内容.pdf + 第六章公式/习题/答案。",
            "使用方式：按时间块执行，每块必须留下可检查的产出，不以“看过”作为完成。",
        ],
    )

    story.append(para("执行规则与材料地图", styles, "ChapterTitle"))
    story.extend(
        [
            para("两天的关键不是把所有页再读一遍，而是把知识压缩为可回忆、可计算、可定位的结构。", styles, "CalloutCN"),
            bullet("学习循环：20分钟理解 -> 5分钟合书回忆 -> 10分钟查漏、标页码。", styles),
            bullet("完成标准分三层：闭卷能说；不看图能画流程/比较；开卷60秒内找到证据。", styles),
            bullet("红色标记不会，黄色标记不稳定，绿色表示能独立讲/做；每天结束只修红黄项。", styles),
            bullet("不值得做：大段抄讲义、精记全部政策日期、背工具宣传语、反复阅读已经会的内容。", styles),
        ]
    )
    story.append(
        table_flow(
            ["材料", "使用范围", "两天中的角色"],
            [
                ["教材重点.pdf", "2-8页索引；9-46页关键原页", "先定位，再回实体教材；索引必须打印/可快速打开"],
                ["补充复习内容.pdf", "第1/2/3/5/6章从4/6/8/10/12页开始", "替代打印全部PPT，是主要理论讲义"],
                ["公式汇总.pdf", "1-7页", "第6章公式选择与例题入口"],
                ["30题习题卷/答案", "习题1-5页；答案1-12页", "先独立计算，再按步骤纠错"],
                ["实体教材", "按教材重点中的印刷页码", "考试最终证据源；贴章节和P0页签"],
            ],
            styles,
        )
    )
    story.append(Spacer(1, 4 * mm))
    story.append(
        table_flow(
            ["日期", "主任务", "结束时必须拥有"],
            [
                ["第1天", "第1、2、3章 + 检索系统 + 5道基础计算", "章节框架、3张比较表、页签、第一版错题表"],
                ["第2天", "第5、6章 + 18道P0题 + 模拟 + 最终修补", "公式选择表、计算错题、60秒定位能力、装包清单"],
            ],
            styles,
        )
    )
    story.append(PageBreak())
    story.extend(toc_story(styles))

    story.append(para("第1天：搭建框架与检索系统", styles, "ChapterTitle"))
    story.append(para("重点顺序：第2章 > 第3章 > 第1章。当天不要深入第5、6章，只用5道计算题预热。", styles, "CalloutCN"))
    story.append(table_flow(["时间", "任务", "材料与重点", "验收"], DAY1, styles, widths=[25 * mm, 32 * mm, 72 * mm, 45 * mm], small=True))
    story.append(para("第1天结束检查", styles, "SectionTitle"))
    for item in [
        "不看资料说出5V+1C、三层架构、五种大数据思维。",
        "画出HDFS读/写的角色关系，写出HBase与关系数据库至少4项差异。",
        "画出Flume的Source-Channel-Sink，说明Scribe故障转储。",
        "5次开卷检索至少4次小于60秒；5道计算至少4题正确。",
        "把所有错误写成“错因 + 正确规则 + 对应页码”，不只抄答案。",
    ]:
        story.append(bullet(item, styles))
    story.append(PageBreak())

    story.append(para("第2天：完成重点、计算与模拟", styles, "ChapterTitle"))
    story.append(para("第6章必须留出整块时间。若前面延误，先取消P1练习，不压缩P0计算与模拟。", styles, "CalloutCN"))
    story.append(table_flow(["时间", "任务", "材料与重点", "验收"], DAY2, styles, widths=[25 * mm, 32 * mm, 72 * mm, 45 * mm], small=True))
    story.append(para("第2天结束检查", styles, "SectionTitle"))
    for item in [
        "能比较7种抓取策略，并解释robots.txt核心字段。",
        "能根据题目选择卡方、Pearson、协方差、Jaccard、距离或规范化公式。",
        "18道P0题全部做过，正确率至少80%；低于80%时只重做错题。",
        "五章各做一次3分钟口述，卡住即查页码并补到错概念表。",
        "资料按考试使用顺序摆放：规划 -> 补充讲义 -> 教材重点索引 -> 公式 -> 教材。",
    ]:
        story.append(bullet(item, styles))
    story.append(PageBreak())

    story.append(para("五章P0重点与完成标准", styles, "ChapterTitle"))
    story.append(table_flow(["章节", "权重", "P0重点", "材料页码", "完成标准"], CHAPTER_TARGETS, styles, widths=[16 * mm, 15 * mm, 70 * mm, 34 * mm, 39 * mm], small=True))
    story.append(para("复习取舍", styles, "SectionTitle"))
    story.append(bullet("P0必须掌握：定义、组成、流程、比较、公式、适用条件和教材位置。", styles))
    story.append(bullet("P1有时间再做：发展历史细节、工具的完整功能列表、重复案例、政策全文。", styles))
    story.append(bullet("任何知识点如果连续读两遍仍不能复述，停止阅读，改成写问题并主动回忆。", styles))
    story.append(PageBreak())

    story.append(para("第6章计算：18道必做 + 12道补充", styles, "ChapterTitle"))
    story.append(para("练习顺序固定为：独立列公式 -> 代入 -> 写结论 -> 对答案 -> 记录错因。答案解析只在完整尝试后打开。", styles, "CalloutCN"))
    story.append(table_flow(["题组", "题号", "内容", "安排"], CALC_GROUPS, styles, widths=[31 * mm, 38 * mm, 68 * mm, 37 * mm]))
    story.append(para("计算题四类失分检查", styles, "SectionTitle"))
    for item in [
        "选错公式：没有先判断数据类型、分布或题目目标。",
        "漏写条件：如非对称二元不计共同为0、Z-score需要均值和标准差。",
        "中间步骤缺失：卡方期望频数、协方差均值、规范化极值必须写清。",
        "结果无解释：最后补一句“相关/不相关、相似度大小、归一化区间、是否合并”。",
    ]:
        story.append(bullet(item, styles))
    story.append(PageBreak())

    story.append(para("开卷检索系统与60秒训练", styles, "ChapterTitle"))
    story.append(para("开卷考试最容易浪费的不是知识，而是翻找时间。两天内至少完成10次定时检索。", styles, "CalloutCN"))
    story.append(
        table_flow(
            ["标签", "放置位置", "内容"],
            [
                ["章标签", "教材第1、2、3、5、6章起始页；第7章HDFS/HBase/Hive", "共6-7个大页签"],
                ["公式标签", "第6章统计、距离、卡方/相关、规范化、规约", "只贴公式入口，不到处贴"],
                ["工具标签", "Flume/Scribe、爬虫、HBase/Hive", "用于简答和比较题"],
                ["错题标签", "公式汇总或答案解析对应页", "只保留仍会错的题型"],
            ],
            styles,
        )
    )
    story.append(para("10个定时检索问题", styles, "SectionTitle"))
    for index, question in enumerate(LOOKUP_DRILLS, 1):
        story.append(bullet(f"{index}. {question}", styles))
    story.append(para("计时标准：绿色 <= 60秒；黄色 61-120秒；红色 > 120秒或找错位置。红色问题必须重新设计页签。", styles, "CalloutCN"))
    story.append(PageBreak())

    story.append(para("时间不足、疲劳与最终装包", styles, "ChapterTitle"))
    story.append(para("如果每天只能学4-5小时", styles, "SectionTitle"))
    for item in [
        "保留第2、5、6章；第1章只记5V+1C/架构/伦理，第3章只记Flume/Scribe/工具比较。",
        "计算只做18道P0题，12道P1全部取消。",
        "保留10次60秒检索；检索训练比再读一遍讲义更有开卷收益。",
        "每章只留下一个产出：框架图、比较表、公式表或错题表。",
    ]:
        story.append(bullet(item, styles))
    story.append(para("防止第二天崩盘", styles, "SectionTitle"))
    for item in [
        "每50分钟离开座位10分钟；午间至少休息30分钟。",
        "连续两题卡住超过15分钟，先标红跳过，完成同组其他题后再回来。",
        "21:20后不新增内容，只修红黄项；22:00停止，保证睡眠。",
    ]:
        story.append(bullet(item, styles))
    story.append(para("考前最终清单", styles, "SectionTitle"))
    story.append(
        table_flow(
            ["检查项", "合格标准"],
            [
                ["五章口述", "每章3分钟内说出结构和P0点"],
                ["计算", "18道P0题做过且正确率>=80%"],
                ["检索", "10个关键词至少8个在60秒内定位"],
                ["材料", "规划、补充讲义、教材重点索引、公式、教材顺序固定"],
                ["工具", "页签、笔、计算器（若考试允许）、纸张准备完毕"],
                ["状态", "22:00停止复习，保证睡眠和第二天专注"],
            ],
            styles,
        )
    )

    doc = ReviewDocTemplate(
        str(OUTPUT),
        "复习规划｜两天开卷复习执行版",
        styles,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=17 * mm,
        title="复习规划",
        author="Codex Scholar",
    )
    doc.multiBuild(story)


def main() -> None:
    write_markdown()
    build_pdf()
    print(f"created: {MARKDOWN}")
    print(f"created: {OUTPUT}")


if __name__ == "__main__":
    main()

