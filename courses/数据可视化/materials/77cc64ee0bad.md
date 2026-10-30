# 数据可视化实验

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

上海理工大学光电信息与计算机工程学院
《大数据可视化》实验报告

专　　业     数据科学与大数据技术                        
姓    名　　 Student                       
学　  号     0000000000                       
年　　级     2023级                  
指导教师     艾均                     
成    绩：
教师签字：

目录
 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 实验一、职业生涯收入差异可视化3
实验 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 二、人生幸福感量化与可视化7
实验 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 三、买房vs租房的临界点分析11
实验 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 四、LLM辅助的股票投资策略回测17
 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 综合总结22



















实验一、职业生涯收入差异可视化
实验概述
这是对不同城市居民人均收入在未来工作生涯中变化可视化的实验，我认为这样的实验可以让我明白不同城市下的人群在个人收入上有着巨大的差异，我是通过python记录不同城市的23年人均GDP作为起薪，模拟未来工作40年的累计收入与年薪，最终我发现在某一城市待得越久最终累计收入更高，但是在工作生涯前10年并没有显著差距，因此在前十年最好找到接近一线城市的工作岗位，最终定居乐业于此。
实验内容
实验名称： 不同城市职业生涯总收入潜力对比分析
实验目标：
理解不同城市起薪和薪资增长对个人职业生涯总收入的巨大影响。
学习使用Pandas进行时间序列数据模拟和累计计算。
通过Excel可视化，直观比较在不同城市工作的“赚钱”潜力。
实验背景与假设：
• 背景： 毕业后选择工作城市是人生的重要决策，它直接影响到个人的长期收入水平。
• 假设：
你于22岁大学毕业，开始工作，计划于65岁退休，共工作43年（按你本人实际年龄调整）。
你的起薪设定为目标城市2023年的人均GDP（这是一个简化模型，用于代表该城市的平均收入水平）。
你的年薪将以一个固定的年增长率 g 持续增长（例如，你可以设定 g = 5% 或 g = 8%）。
不考虑通货膨胀、税收等复杂因素，仅关注名义收入。
实验步骤与要求
选择城市： 选择3-5个你感兴趣的中国城市。建议覆盖不同级别，选择一线城市北京、上海；新一线城市杭州、成都；二线城市厦门cities = ["北京", "上海", "杭州", "成都", "厦门"]# 选择城市
数据搜集： 查找并记录你所选城市2023年的人均GDP数据，作为你的起薪。
# 各城市2023年人均GDP（单位：万元）。从各城市统计局官网查询数据为北京20.1万，上海19.1万，杭州16.0万，成都10.3万，厦门15.1万
gdp_2023 = [20.1, 19.1, 16.0, 10.3, 15.1] 
设定参数： 确定你的工作年限（如38年）和预设的年薪增长率 g（例如， g = 0.05）。
graduation_age = 22  # 毕业年龄
retirement_age = 65  # 退休年龄
work_years = retirement_age - graduation_age  # 总工作年限43
growth_rate = 0.05  #5%年增长率
数据计算： 使用Pandas计算在每个城市从工作第一年到退休的每一年年薪，以及累计总收入。
for i, city in enumerate(cities):
    start_salary = gdp_2023[i]  # 该城市起薪（2023年人均GDP）
    # 计算每年年薪：第1年=起薪，第2年=起薪*(1+g)，第3年=起薪*(1+g)^2...
    df[f"{city}_年薪(万元)"] = start_salary * (1 + growth_rate) ** (df["工作年份"] - 1)

for city in cities:
    df[f"{city}_累计收入(万元)"] = df[f"{city}_年薪(万元)"].cumsum()  # 累计求和
导出数据： 将计算结果（每年年薪、每年累计收入）导出到Excel文件。
excel_path = "城市职业生涯收入对比数据.xlsx"# 导出到Excel
df.to_excel(excel_path, index=False, engine="openpyxl")
数据可视化： 在Excel中创建图表，清晰地展示不同城市间的收入差异。图1 不同城市工作生涯年薪变化曲线图2 不同城市第43年累计收入比对柱状图
分析与回答：根据图表回答问题：选择不同城市工作，职业生涯收入有多大差异？这将如何影响你未来的选择？从累计收入和年薪增长曲线来看，城市间的收入差异主要体现在以下两点：
差距的 “时间放大效应”：工作年限越久，城市间收入差距越显著。例如工作 40 年左右，北京、上海的累计收入和年薪均远高于成都、厦门，杭州处于 “中间梯队”。
增长的 “斜率差异”：北京、上海的年薪增长曲线更陡峭，意味着随着工作年限增加，薪资涨幅更快；而成都、厦门的增长相对平缓，薪资水平处于较低梯队。这对于我这样即将踏入工作岗位的大学生来说，如果我在上海、北京这样的一线城市能够有工作机会，那从长远来看我最好能一直保持在一线城市长期工作，如果我在二三线城市工作的话可以慢慢争取在一线城市工作的机会，因为前期的薪资差别并不大，在工作第十年之后才逐渐有差距，这时候就需要安定在某一城市长期发展了。
思考与分析：
• 从你的可视化结果看，选择不同城市对生涯总收入的影响有多大？具体差异是多少万元？
城市选择对生涯总收入的影响具有 “量级差异”—— 长期来看，不同城市的累计收入差距可超千万元，即使是同梯队城市也存在上百万元的差异。这种差异会直接影响个人职业生涯的经济回报，进而对职业规划、生活选择产生深远影响。
北京（2874.17 万元）与成都（1472.83 万元）的累计收入差异约为 1401.34 万元。北京与上海（2731.17 万元）的差异约为 142.99 万元；上海与杭州（2287.89 万元）的差异约为 443.28 万元。杭州与厦门（2159.20 万元）的差异约为 128.70 万元；厦门与成都的差异约为 686.37 万元。
• 如果将年薪增长率 g 从5%调整到8%，重新计算并可视化，结果会有什么变化？这说明了什么？
各城市的累计收入较 5% 增长率时呈数倍增长，年薪变化趋势曲线的陡峭程度显著增加，尤其是工作后期，年薪增长进入 “快车道”，高增长率的复利效应在长期职业生涯中被极度放大，不同城市的年薪曲线分化更明显，这说明微小的年薪增长率变化对于个人职业选择有重要影响，所以在工作城市选择上不仅要考虑城市的初始机会，还要关注自身职业发展的行业涨幅、个人能力提升带来的加薪空间，因为高增长率在长期中能让收入差距呈几何级扩大。

图3 不同城市在8%增长率下的第43年累计收入比对图

图4 不同城市在8%增长率下的工作生涯年薪趋势比对图

与LLM交流
一般居民的工作岗位和退休年龄分别为多少？
统计逐年累计收入与工作年薪的可视化图像有什么excel图表推荐？
在wsl虚拟机环境下怎么将dataframe数据作为excel保存到固定路径？



实验二、人生幸福感量化与可视化
实验概述
这是对不同城市幸福得分量化与可视化的实验，实验可以让我通过调整自己的主观幸福维度权重来对各城市的生活幸福指数打分，通过dataframe记录不同城市的各幸福维度评分以及相关权重并进行计算与排序；最终通过不断地权重调整与讨论我发现，权重调整的过程，正是“明确自己到底想要什么”的过程，从现阶段的我的角度来说，上海是最幸福的城市。
实验内容
实验名称： 基于多维价值取向的城市幸福感量化模型
实验目标：
探索将抽象的“幸福感”进行量化建模的方法。
理解个人价值取向（权重）在决策中的决定性作用。
通过可视化，找到最符合自己价值观的“理想城市”。
实验背景与假设：
• 背景： 人生决策不仅是经济决策，还包括家庭、健康、生活品质等非经济因素。量化这些因素有助于做出更全面的选择。
• 假设：
你的“幸福感”可以由几个关键维度构成，例如： 收入水平、家庭陪伴、工作压力、城市宜居、社交生活。
你可以为每个维度赋予一个 权重（0-1之间，总和为1），代表你对该维度的重视程度。
对于你考虑的每个城市，你可以为每个维度主观 打分（1-10分）。
**总幸福感得分 =Σ (维度权重 × 城市在该维度的得分)**。
实验步骤与要求
定义维度： 确定衡量你幸福感的5-6个关键维度。
分配权重： 根据你的个人价值观，为每个维度分配权重。例如，非常看重家庭的人可能会给“家庭陪伴”很高的权重。
weights = {
    '收入水平': 0.25,
    '家庭陪伴': 0.10,
    '工作机会': 0.10,
    '工作压力': 0.15,
    '城市宜居': 0.25,
    '社交生活': 0.15
}
weights_series = pd.Series(weights)
城市评分： 选择与实验一相同的3-5个城市，为你定义的每个维度进行主观评分（1-10分）。评分需要有你的理由（例如，北京的“收入水平”分高，但“工作压力”分低）。
data = {#北京 上海 杭州 成都 厦门
    '收入水平': [9, 8, 6, 3, 5],#根据上一个实验得到的结果
'家庭陪伴': [4, 9, 6, 4, 5],#目前在上海定居，上海有较高的家庭陪伴
'工作机会': [6, 8, 9, 9, 9],#目前大部分计算机行业都将就业岗位分配到了二三线城市
    '工作压力': [3, 4, 6, 7, 8],#上海北京具有较高的工作压力，但二三线城市就少一些
    '城市宜居': [8, 9, 9, 7, 8],#北京房价较高，上海、杭州从城市化和绿化程度来说较好
    '社交生活': [8, 9, 7, 8, 7]#在上海朋友比较多，交友圈集中于此
}
df_scores = pd.DataFrame(data, index=cities)
数据计算： 使用Pandas计算每个城市的加权总分。
# 将评分数据框 (df_scores) 与 权重系列 (weights_series) 相乘
df_weighted_scores = df_scores.mul(weights_series, axis=1)
# 计算每行的总和，即每个城市的加权总分
df_scores['加权总分'] = df_weighted_scores.sum(axis=1)
# 结果排序
df_scores['排名'] = df_scores['加权总分'].rank(ascending=False).astype(int)
导出数据： 将权重、各城市评分、以及最终总分导出到Excel。
# 将权重信息也加入到最终的输出文件或表格中
df_export = df_scores.copy()
# 为了导出更清晰，创建一个包含权重的 DataFrame
df_weights_row = pd.DataFrame([weights], index=['维度权重'])
df_export_final = pd.concat([df_weights_row, df_export])
# 导出到 Excel 文件
excel_filename = '城市幸福感量化模型_实验结果.xlsx'
df_export_final.to_excel(excel_filename, sheet_name='幸福感量化结果')
数据可视化： 使用Excel创建图表，对比各城市在不同维度的表现和总得分。图5 不同城市各幸福维度得分情况雷达图图6 不同城市最终加权幸福得分情况条形图
图7 不同城市最终加权幸福得分情况构成堆积图
思考与分析：
• 哪个城市是你的“最优选”？它的优势主要体现在哪些方面？上海是最优选，主要优势体现在家庭陪伴、社交生活分值比其他城市要高，因为我目前定居在上海，家庭和社交圈更加集中在上海这个城市，同时他的收入水平与城市宜居程度也较好，城市化水平高，有较多的工作机会。
• 如果调整权重，比如将“收入水平”的权重提高到0.5，将其他权重相应降低，最终排名会发生什么变化？这说明了什么？
北京从第三升到第二，杭州从第二降到第三，其他没有变化，这可以说明幸福评测的 “主观性” 本质是 “价值权重的量化”，第一次权重（收入 0.25 = 宜居 0.25）代表 “收入与生活质量并重” 的幸福观，此时上海、杭州的 “均衡 + 高生活质量”更占优；第二次权重（收入 0.5）代表 “收入优先于一切” 的幸福观，此时北京的 “收入极致优势” 得以凸显 ——评测结果不是 “城市本身的幸福度绝对高低”，而是 “城市特质与用户价值偏好的匹配度”。这种变化最核心的说明是：幸福是 “价值偏好的产物”，城市的 “幸福排名” 本质是 “城市特质与权重所代表的价值取向的匹配结果”。当你更看重收入时，收入突出的城市会脱颖而出；当你更看重均衡的生活质量时，均衡型城市会更占优 —— 权重调整的过程，正是 “明确自己到底想要什么”的过程。
• 这个量化模型有什么优点和缺点？你觉得如何改进它？
这个模型的优点在于可操作性与透明性，将抽象的幸福观量化且支持自由调整；但在科学性、完整性、适配性上仍有明显短板，因此我认为在权重确定上采取科学的层次分析法（AHP）替代纯主观设定：先明确 “幸福” 是核心目标，再将 6 个维度作为子目标，通过两两对比（比如 “收入水平” 和 “家庭陪伴” 哪个更重要），计算出逻辑自洽的权重。同时对于不同年龄段的人群，适时调整指标以及相关权重，比如对于青少年和老年人家庭陪伴与社交生活高权重，对于青少年设置教育水平作为高权重维度，中年则考虑收入水平与工作压力等。
与LLM交流
杭州、成都、厦门近几年的城市化水平如何？
北京、杭州、成都、厦门、上海这五座城市的就业岗位数量怎么样？
怎么将权重信息保存到dataframe中？
收入水平在幸福考核中权重提升有什么意义？
除了我认为的可以适时调整模型指标与权重外还有什么科学方法改进模型？

实验三、买房vs租房的临界点分析
实验概述
这是对买房租房决策临界点可视化的实验，实验可以让我通过调整房价年增长率，观察30年后买房还是租房资产更高；我认为这能让我理解到在不同投资能力、还款年限、银行贷款利率下对于决策会有不同的影响，最特别的结论在于，房价至少要上涨3.2%才是买房更划算，而对于高投资能力者，租房+合理的投资才能带来更大的收益。
实验内容
实验名称： 考虑房价增长的“买房-租房”决策平衡点分析
实验目标：
建立一个简化的财务模型，量化比较在一定年限后“买房”与“租房”两种选择的资产差异。
理解租售比、贷款利率和房价年增长率在决策中的关键作用。
通过计算和可视化，找到使“买房”决策优于“租房”的最低房价年增长率。
实验背景与假设：
• 背景： 买房还是租房是年轻人面临的重大财务决策。其核心是比较：买房的资产增值+居住效用 vs. 租房的财务灵活性+投资收益。
• 假设：
买房路径： 你支付首付后，剩余部分进行30年商业贷款。退休时（例如30年后），你拥有了一套无贷款的房子。
租房路径： 你将原本用于首付的钱进行投资（例如，年化收益率为 r 的理财）。同时，你将原本每月要还的月供，扣除租金后，剩余部分也投入该理财产品。
参数：
■ 房屋总价 P
■ 首付比例 d (如 30%)
■ 贷款年利率 i (如 4.0%)
■ 贷款年限 N (如 30年)
■ 租售比 R (年租金/房屋总价，如 2%)，用于计算租金。
■ 租房者投资年化收益率 r (如 5%)
■ 待求变量：房价年均增长率 g
实验步骤与要求
设定参数： 根据你心仪城市和房产情况，设定上述所有已知参数（ P, d, i, N, R, r）。
city = "上海"
house_price_per_sqm = 85000  # 元/平方米（上海中心区域均价）
house_area = 80  # 平方米（典型两居室）
P = house_price_per_sqm * house_area  # 房屋总价
d = 0.3  # 首付比例30%
i = 0.04  # 贷款年利率4.0%
N = 30  # 贷款年限30年
R = 0.018  # 租售比1.8%（上海实际情况，租售比较低）
r = 0.045  # 租房者投资年化收益率4.5%
simulation_years = 30 # 模拟年份
months = simulation_years * 12
计算月供： 分别计算“等额本息”和“等额本金”下的月供金额。
def calculate_monthly_payment(P, d, i, N, method='equal_principal_interest'):
    loan_amount = P * (1 - d)  # 贷款金额
    monthly_rate = i / 12  # 月利率
    total_months = N * 12  # 总月数
    if method == 'equal_principal_interest':
        M = loan_amount * monthly_rate * (1 + monthly_rate)**total_months / ((1 + monthly_rate)**total_months - 1)
        return M  # 等额本息公式：M = P*r*(1+r)^n / [(1+r)^n-1]
    elif method == 'equal_principal':
        # 等额本金：每月偿还相同本金 + 剩余本金的利息
        principal_per_month = loan_amount / total_months
        # 首月月供
        first_month_interest = loan_amount * monthly_rate
        first_month_payment = principal_per_month + first_month_interest
        # 末月月供
        last_month_interest = principal_per_month * monthly_rate
        last_month_payment = principal_per_month + last_month_interest
        return first_month_payment, last_month_payment, principal_per_month
monthly_payment_equal_principal_interest = calculate_monthly_payment(P, d, i, N, 'equal_principal_interest')# 计算等额本息月供
first_payment, last_payment, principal_per_month = calculate_monthly_payment(P, d, i, N, 'equal_principal')# 计算等额本金月供
等额本息月供：22,724.97元/月；等额本金首月月供：29,088.89元/月；等额本金末月月供：13,266.30元/月；等额本金月均还款：21,177.59元/月
模拟计算： 使用Pandas进行一个30年的逐月模拟。
◦ 买房者资产： 每年更新房屋价值 P * (1+g)^t。
◦ 租房者资产： 每年更新投资账户总额，包括首付款的复利增长和（月供-月租金）差额的持续投入和复利增长。
def simulate_housing_decision(g, P, d, i, N, R, r, simulation_years=30):
    """
    house_asset: 买房者30年后的净资产
    rent_asset: 租房者30年后的投资总额
    monthly_data: 逐月详细数据
    """
    months = simulation_years * 12
    monthly_rate_house = g / 12  # 房价月增长率
    monthly_rate_invest = r / 12  # 投资月收益率
    monthly_payment = calculate_monthly_payment(P, d, i, N, 'equal_principal_interest')
    monthly_rent = P * R / 12
    down_payment = P * d# 买房者：首付锁定，房屋价值增长
    # 租房者：首付用于投资 + 每月差额投资
    initial_investment = down_payment  # 首付金额作为初始投资额
    monthly_investment = monthly_payment - monthly_rent  # 每月可投资额
    monthly_data = pd.DataFrame({
        'month': range(1, months + 1),
        'house_value': np.zeros(months),  # 房屋价值
        'house_equity': np.zeros(months),  # 房产净资产（简化考虑）
        'investment_balance': np.zeros(months),  # 投资账户余额
        'monthly_investment': np.zeros(months)  # 每月投资额
    })
    investment_balance = initial_investment# 逐月模拟
    for month in range(months):
        # 买房者资产计算，房屋价值按月增长
        current_house_value = P * (1 + monthly_rate_house) ** (month + 1)
        # 假设30年后贷款还清，净资产=房屋价值
        house_equity = current_house_value if month == months - 1 else 0
        
        # 租房者资产计算，月初投资余额产生收益
        investment_balance = investment_balance * (1 + monthly_rate_invest)
        investment_balance += monthly_investment# 月末追加投资
        # 记录数据
        monthly_data.loc[month, 'house_value'] = current_house_value
        monthly_data.loc[month, 'house_equity'] = house_equity
        monthly_data.loc[month, 'investment_balance'] = investment_balance
        monthly_data.loc[month, 'monthly_investment'] = monthly_investment
    house_asset = monthly_data.iloc[-1]['house_value']  # 买房者净资产
    rent_asset = monthly_data.iloc[-1]['investment_balance']  # 租房者投资总额
    return house_asset, rent_asset, monthly_data# 30年后的最终资产
寻找平衡点： 尝试不同的房价年增长率 g，找到一个临界值，使得30年后买房者的净资产（房屋价值）约等于租房者的净资产（投资账户总额）。
def find_balance_point(P, d, i, N, R, r, simulation_years=30):    
    def equation(g):
        house_asset, rent_asset, _ = simulate_housing_decision(
            g[0], P, d, i, N, R, r, simulation_years
        )
        return house_asset - rent_asset
    
    initial_guess = [0.03]# 初始猜测：3%
    try:
        solution = fsolve(equation, initial_guess, xtol=1e-6)
        balance_g = solution[0]
        house_asset, rent_asset, _ = simulate_housing_decision(
            balance_g, P, d, i, N, R, r, simulation_years
        ) # 验证结果
        return balance_g
    except Exception as e:
        print(f"平衡点计算失败：{e}")
        # 使用二分法作为备选
        low, high = 0.01, 0.10  # 1%到10%
        for _ in range(100):  # 最多100次迭代
            mid = (low + high) / 2
            house_asset, rent_asset, _ = simulate_housing_decision(
                mid, P, d, i, N, R, r, simulation_years
            )
            if abs(house_asset - rent_asset) < 10000:  # 误差小于1万元
                return mid
            if house_asset > rent_asset:
                high = mid
            else:
                low = mid
        return (low + high) / 2
导出数据： 将在不同 g 值下的两种路径资产对比结果导出到Excel。
数据可视化： 在Excel中清晰展示两种路径下的资产增长情况。图8 不同房价年增长率下30年后买房者与租房者资产差额趋势图

图9 不同房价年增长率下30年后买房者与租房者最终资产对比
思考与分析：
• 根据你的计算，房价每年至少要上涨百分之多少，买房才比租房更划算？房价至少要上涨3.2%才是买房更划算。如果租金随着房价固定增长，房价则至少要上涨2.6%，相关可视化结果如图10所示。

图10 修正条件下不同房价年增长率下30年后买房者与租房者最终资产对比
• 如果银行贷款利率上升或下降，这个临界点会如何移动？为什么？随着贷款利率变化临界点移动趋势如图11所示，基本呈现正相关，因为当利率上升时，买房者月供增加，现金流压力增大，相应租房者每月可投资额显著增加，租房者投资账户积累加速，30年后资产更高，因此为平衡这种优势，房价需要更高的增长率。

图10 贷款利率低于买房-租房决策平衡点的影响
• 如果你的个人投资能力很强（例如 r 提高到10%），这个临界点又会如何移动？
高投资能力下平衡点为8.02%，平衡点上升幅度达到4.85个百分点，说明投资能力对平衡点影响巨大，意味着高能力投资者租房更优，因此对于普通投资者来说，在大多数市场环境下，买房策略更优
，对于专业投资者来说，租房+投资策略在财务上通常更优，具体临界点移动趋势如下图11。

图11 贷款利率低于买房-租房决策平衡点的影响
• “等额本息”还款计划，按照50年， 100年， 1000年计划还款，每月还款额度多少？
50年每月还款18,359.65元，100年每月还款16,164.71元，1000年每月还款15,866.67元，超过50年后，延长贷款期限对降低月供的效果微乎其微，数学层面上来说，1000年贷款完美验证了数学极限理论，而等额本息公式在超长期限下快速收敛到利息极限，虽说50年贷款表面上月供降低19.2%，但总利息增加34.7%，而100年+贷款已失去实际财务意义，成为了接近"永久债券"的概念，可以说20-30年是月供压力与总成本的最佳平衡区间。
与LLM交流
如何将买房资产与租房资产算法结合在一个python函数？
如果我的房价平衡点无法直接根据我的初试平衡点得出，该怎么去进行补充运算？
我这样的租金固定算法并不合理，怎么优化？
如何可视化贷款利率变化下平衡点与相应月供金额的变化？
如何用多样的可视化方法来直观展示投资年化收益对房价增长率平衡点的影响？
不同的投资年化收益率说明了什么？怎么根据这个指标分类投资者的投资能力？
帮我撰写不同还款年限下每月还款额度变化的数学计算代码
这样不同还款年限下每月还款金额的变化有什么启发意义？

实验四、LLM辅助的股票投资策略回测
实验概述
这是对LLM辅助的股票投资策略回测的实验，实验可以让我通过与现有AI大模型进行沟通设计投资策略并回测这一策略的有效性，我通过和Google Gemini对话并在其帮助与指导下完成的代码的编写；我发现现在的人工智能大模型完全可以作为一个较为专业的指导者指导股市新手来进行简单的投资策略设计，并可以在投资过程中与大模型对话交流学习到股市投资的财经素养。
实验内容
实验名称： 基于LLM建议的A股投资策略有效性回测
实验目标：
学习如何与大型语言模型（LLM）协作，设计一个可执行、可量化的投资策略。
利用真实的股票历史数据，对设计的策略进行回测，评估其有效性。
通过可视化分析策略表现，理解收益率、波动性和夏普比率等关键指标。
实验背景与假设：
• 背景： LLM在信息整合与模式识别方面具有潜力，可以作为投资策略设计的辅助工具。通过历史数据回测，可以检验这些策略在过去市场环境中的表现。
• 假设：
你从开始工作的第一年（或选择一个历史时间段，如2010-2023年）开始投资。
你有一笔初始投资资金，并且每年会追加一部分新的投资（模拟工资结余）。
交易成本（手续费、印花税）暂时忽略，以简化模型。
LLM提供的策略是基于公开信息，回测结果不代表未来收益。
实验步骤与要求
与LLM设计策略：
◦ 向LLM提问，例如： “请为我设计一个适合长期投资者的、简单的A股价值投资策略。请明确选股标准（如低市盈率、高股息率、稳定增长的ROE）和调仓规则（如每年调整一次）。 ”
◦ 记录LLM给出的具体策略。
这是一种稳健龙头价值投资策略，旨在通过持有 A 股市场中具有强大“护城河”的行业龙头，并采用低频度调仓（每年一次）的方式，获取超越市场基准的稳定超额收益。
选股标准中，选股风格为行业龙头/“护城河”,贵州茅台、招商银行、中国平安；在估值安全上，选择招商银行这样的低市盈率 (P/E <20)；在高股息率上,选择过去三年平均股息率>2%的招商银行、中国平安，在盈利稳定上,选择过去三年平均 ROE >15%的贵州茅台。
在调仓规则中，调仓频率为每年调整一次，调仓时间是每年第一个交易日，资金分配是将当时的总资产（包含前一年的收益和当年的追加投资）等权分配到选定的股票池中，持有期为买入后全年持有，直到下一个调仓日。
数据获取：
◦ 根据策略，选择几只符合条件的代表性股票（例如，贵州茅台、格力电器、招商银行等）。
◦ 使用tushare, akshare等Python库获取这些股票在你设定的回测期间（如2010年1月1日至今）的后复权日度或月度收盘价数据。
def get_stock_data(stock_code, start_date, end_date):#获取单只股票的历史数据
    try:# AKShare获取A股历史数据
        df = ak.stock_zh_a_hist(symbol=stock_code, period="daily", 
                               start_date=start_date, end_date=end_date,
                               adjust="hfq")  # 后复权
        df['date'] = pd.to_datetime(df['日期'])
        df.set_index('date', inplace=True)
        return df[['收盘']]
    except Exception as e:
        print(f"获取股票 {stock_code} 数据失败: {e}")
        return None
def get_index_data(index_code, start_date, end_date):#获取指数历史数据
    try:# AKShare获取指数数据
        df = ak.index_zh_a_hist(symbol=index_code, period="daily",
                               start_date=start_date, end_date=end_date)
        df['date'] = pd.to_datetime(df['日期'])
        df.set_index('date', inplace=True)
        return df[['收盘']]
    except Exception as e:
        print(f"获取指数 {index_code} 数据失败: {e}")
        return None
start_date = "20100101"#  回测参数设置
end_date = datetime.datetime.now().strftime("%Y%m%d")
initial_capital = 100000  # 初始资金10万元
annual_investment = 20000  # 每年追加2万元
tickers = {
    '600519': '贵州茅台',
    '600036': '招商银行', 
    '601318': '中国平安'
}
benchmark_code = "000300"  # 沪深300
data_dict = {}
for code, name in tickers.items():
    print(f"获取 {name}({code}) 数据...")
    stock_data = get_stock_data(code, start_date, end_date)
    if stock_data is not None:
        data_dict[code] = stock_data['收盘']
        print(f"{name} 数据获取成功，共 {len(stock_data)} 条记录")

print("正在获取基准指数数据...")
benchmark_data = get_index_data(benchmark_code, start_date, end_date)
if benchmark_data is not None:
    data_dict[benchmark_code] = benchmark_data['收盘']
    print(f"沪深300 数据获取成功，共 {len(benchmark_data)} 条记录")
price_data = pd.DataFrame(data_dict)# 合并数据
price_data.columns = list(tickers.values()) + ['沪深300']
price_data = price_data.dropna()
输出结果如下：贵州茅台 数据获取成功，共 3852 条记录；招商银行 数据获取成功，共 3837 条记录；中国平安 数据获取成功，共 3804 条记录；沪深300 数据获取成功，共 3858 条记录；数据时间范围: 2010-01-04 00:00:00 到 2025-11-21 00:00:00；可用数据点: 3777
策略回测计算：
◦ 使用Pandas模拟投资过程。假设每年年初，你将资金平均分配到选中的股票池中。
◦ 计算每年组合的年度收益率。
◦ 计算到退休时（或回测期末），你的总资产增长了多少。
◦ 同时，计算一个基准（如沪深300指数）在同期的表现，用于对比。
for i in range(len(years)):# 循环模拟每年的投资和调仓
    current_year = years[i]
    rebalance_date = yearly_prices.index[i]# 获取当年年初的调仓日价格
    current_prices = yearly_prices.loc[rebalance_date]
    if i > 0:# 年初追加投资 (除第一年外)
        current_strategy_capital += annual_investment
        current_benchmark_capital += annual_investment
    # 策略组合 - 等权分配资金 (调仓)
    # 计算当前每只股票可分配的资金
    capital_per_stock = current_strategy_capital / len(ticker_codes)
    # 计算新的持股数
    shares = (capital_per_stock / current_prices[ticker_codes])
    #基准组合 - 购买沪深300 (调仓)
    benchmark_shares = current_benchmark_capital / current_prices[benchmark_name]
    if i < len(years) - 1:# 计算年末资产净值 (使用下一年的调仓日价格作为年末价格)
        next_year = years[i+1]
        next_rebalance_date = yearly_prices.index[i+1]
        next_prices = yearly_prices.loc[next_rebalance_date]
        end_of_year_strategy_value = (shares * next_prices[ticker_codes]).sum()
        current_strategy_capital = end_of_year_strategy_value
        portfolio_metrics.loc[current_year,'Strategy_Capital']= end_of_year_strategy_value# 策略净值：持有股份 * 下一年年初价格
        end_of_year_benchmark_value = benchmark_shares * next_prices[benchmark_name]# 基准净值：持有股份 * 下一年年初价格
        current_benchmark_capital = end_of_year_benchmark_value
        portfolio_metrics.loc[current_year, 'Benchmark_Capital'] = end_of_year_benchmark_value
    else:# 回测期末的净值 (使用数据中最后一天价格)
        final_prices = price_data.iloc[-1]
# 策略最终净值
        final_strategy_value = (shares * final_prices[ticker_codes]).sum()
        portfolio_metrics.loc[current_year, 'Strategy_Capital'] = final_strategy_value
        # 基准最终净值
        final_benchmark_value = benchmark_shares * final_prices[benchmark_name]
        portfolio_metrics.loc[current_year, 'Benchmark_Capital'] = final_benchmark_value
initial_df = pd.DataFrame({# 创建一个包含初始资金的 DataFrame 用于计算收益率
    'Strategy_Capital': [initial_capital],
    'Benchmark_Capital': [initial_capital]
}, index=[years[0]-1])
portfolio_final = pd.concat([initial_df, portfolio_metrics[['Strategy_Capital', 'Benchmark_Capital']]])
portfolio_final.index.name = 'Year'# 合并初始资金和每年的年末净值
# 计算年度收益率 (与上一年年末净值对比)
portfolio_metrics['Strategy_Annual_Return'] = portfolio_final['Strategy_Capital'].pct_change().shift(-1).loc[years]
portfolio_metrics['Benchmark_Annual_Return'] = portfolio_final['Benchmark_Capital'].pct_change().shift(-1).loc[years]
导出数据： 将每年的资产净值、年度收益率、与基准的对比等数据导出到Excel。
数据可视化： 在Excel中绘制图表，展示策略的长期表现。

图12 资产净值增长曲线折线图


图13 资产净值增长曲线折线图
思考与分析：
• 你的策略在回测期内的总收益率是多少？相比基准指数，是超额收益还是跑输了？
总收益率为287.24%，属于超额收益。
• 在哪些年份你的策略表现特别好或特别差？你认为可能的原因是什么？
我的策略在2016年表现特别好，在经历了 2015 年股灾和 2016 年初的熔断后，市场整体表现低迷（沪深300下跌）。但是，市场风格发生巨大变化，资金开始抱团转向业绩稳定、低估值、高分红的 “白马股” 或 “价值股”。可以说2016 年策略表现优异主要得益于策略选股（行业龙头白马股）与当时的结构性牛市（价值股行情）高度匹配。
• 和LLM讨论你的回测结果，问它： “基于这个回测结果，你会如何优化这个策略？ ” 看看它能否提出改进建议。
动态选股,当前策略是固定三只股票。基于过去表现，可以根据当年的 P/E 或股息率在整个 A 股中重新选择 3-5 只股票,解决未来行业轮动风险，确保策略能适应不断变化的市场。
分散行业,目前策略集中在消费、银行、保险。如果未来市场风格转向科技或周期股，及时调整选股标准，以确保至少包含 4 个不同的大行业,降低单一行业周期性风险，提高策略稳健性。
调仓权重,目前是等权分配。根据股息率或低波动率（Low Volatility）指标，实行加权调仓（例如，股息率最高的股票分配 40% 资金）,提高资金利用效率，将资金集中于当前最符合价值标准的股票。
引入止损,鉴于策略在 2021-2023 年经历了较大回撤，增加一个简单的年度止损规则（例如，如果某只股票在一年内跌幅超过 30%，立即卖出并持有现金）,控制极端风险，避免深度回撤。
• 这个回测模型有哪些简化和局限性？（例如，未考虑交易成本、股息再投资、幸存者偏差等）
未考虑交易佣金和印花税。由于每年调仓一次，实际交易成本较低，但仍会略微降低收益率。
未考虑现金分红的再投资（策略仅考虑调仓日的资产总额）。如果将股息立即用于购买更多股票，实际的复利效应会更强，回测结果可能低估了实际收益。
未考虑大额资金买卖是否会影响股票价格。对于贵州茅台这类流动性好的大盘股影响小，但对中小盘股影响大。
幸存者偏差,股票池是事先选定的，它们都是在回测期内“幸存”且表现优异的公司。这可能高估了该策略在历史上的通用表现。
指数差异,基准 (沪深300) 通常指的是指数点位，而您的策略对比的是包含定投的资产净值，但市场中追踪指数的 ETF 同样有管理费和交易费用，模型中均未考虑。
与LLM交流
设计适合长期投资者的、简单的A股价值投资策略及选股标准与调仓规则
对于最终的策略来说，我怎么计算总收益率？
基于回测结果如何优化策略？以及这个回测模型有哪些局限性？
我的策略在2016年表现较好？有什么原因
如何通过akshare库获取所选择的代表股票数据并进行数据整合？
夏普比率是什么？Python中怎么计算？
为什么会存在数据抓取超时的问题？
我的数据列名出现问题，如何对他进行直接修改但不改正数据结构？

综合总结
通过这组连贯的财经探索实验，我有较大的收获。从实验一：城市收入差异中，我看清了长期工作的 “时间放大效应”，明白职业选择需兼顾短期机会与长期增值，在前期尽量选择大城市进行择业，然后再30岁之后长期定居于某一城市进行财富积累；实验二：幸福感量化实验则让我顿悟，所谓 “理想生活” 本质是价值偏好的量化匹配，权重调整的过程就是明确自我需求的过程，幸福感源自于我的价值选择，幸福不依靠外物，而是自身的选择与态度，更重要的是我发现现在的我更觉得目前的上海是最具有幸福感的城市。实验三：买房租房的临界点分析打破了 “买房必赚” 的固有认知，让我学会用财务模型权衡决策，也让我认识到如果具有较强的投资能力，那选择在上海这一城市租房投资更具有经济价值；LLM 辅助股票投资回测，不仅掌握了策略设计与回测方法，更体会到 AI 在财经领域的实用价值，可以很好带领财经新手进行投资实战。整个过程中，我从凭直觉判断转向用数据量化决策，深刻认识到财经素养的核心正是这种理性分析与自我认知的结合，同时这四个实验也让我更好地打破固有传统观念，学会使用新科技与理科思维更理性地看待生活财经问题。
