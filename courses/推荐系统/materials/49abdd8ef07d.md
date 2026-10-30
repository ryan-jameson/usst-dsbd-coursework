# 推荐系统实验报告

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

上海理工大学光电信息与计算机工程学院
《推荐系统》实验报告

专　　业     数据科学与大数据技术                        
姓    名　　 Student                       
学　  号     0000000000                       
年　　级     2023级                  
指导教师     艾均                     
成    绩：
教师签字：

目录
 TOC \o "1-3" \h \z \u  HYPERLINK \l "_Toc114297723" 一、User-based Pearson-CF PAGEREF _Toc114297723 \h 3
 HYPERLINK \l "_Toc114297723" 二、度量指标6
 HYPERLINK \l "_Toc114297723" 三、User-based Slope One10
 HYPERLINK \l "_Toc114297723" 四、综合实验1 PAGEREF _Toc114297723 \h 3
 HYPERLINK \l "_Toc114297723" 五、心得体会19




















一、User-based Pearson-CF
实验理解
这里就是基于皮尔逊相似性的计算公式来筛选靠近目标用户的k个邻居然后再预测对于用户未评分物品的评分。
实验步骤与结果
选择MovieLens small 数据集；
ratings = pd.read_csv('/mnt/font_path/ratings.csv')#每行表示一个用户对某电影的评分
实现基于用户Pearson相似性的协同过滤（CF）个性化推荐算法；
def compute_user_similarity(user_item_matrix):#输入用户-电影评分矩阵
num_users = user_item_matrix.shape[0]#获取用户数量
similarity_matrix = np.zeros((num_users, num_users))#初始化n×n相似度矩阵
user_ids = user_item_matrix.index# 获取用户ID列表
for i in range(num_users):# 遍历所有用户对 (i, j)，只计算上三角部分以避免重复计算
    for j in range(i, num_users):
        user_i_ratings = user_item_matrix.iloc[i].dropna()# 获取用户 i 的电影及其评分
        user_j_ratings = user_item_matrix.iloc[j].dropna()# 获取用户 j的电影及其评分
        common_movies = list(set(user_i_ratings.index) & set(user_j_ratings.index))
        if len(common_movies) > 0:# 只有共同评分电影数大于0时才计算相似度
            ratings_i = user_i_ratings[common_movies]# 用户 i 共同电影的评分向量
            ratings_j = user_j_ratings[common_movies]# 用户 j共同电影的评分向量
            if np.all(ratings_i == ratings_i.iloc[0]) or np.all(ratings_j == ratings_j.iloc[0]):# 检查是否为常数数组
                r = 0# 如果是，则相似度设为0
            else:
                r, _ = pearsonr(ratings_i, ratings_j) # 计算 Pearson 相关系数
                if np.isnan(r):
                    r = 0# 如果计算结果由于常数数组导致的标准差为0，则设为 0
            similarity_matrix[i, j] = r# 填充相似度矩阵
            similarity_matrix[j, i] = r# 对称填充下三角部分
similarity_df = pd.DataFrame(similarity_matrix, index=user_ids, columns=user_ids)
return similarity_df# 返回用户ID作为行索引和列索引的相似度矩阵 DataFrame
读入Ratings数据并适当保存和索引； 
user_item_matrix=ratings.pivot(index='userId',columns='movieId',values='rating')
数据按折n验证分割成训练集和测试集；def split_data(ratings, n_splits):#随机打乱分为n折
kf = KFold(n_splits=n_splits, shuffle=True, random_state=42)#随机种子可复现
splits = []#创建评分记录划分用于存储的空集合
for train_index, test_index in kf.split(ratings):#交叉定位打乱后的评分数据
    train_data = ratings.iloc[train_index]#获取训练集相关数据
    test_data = ratings.iloc[test_index]#获取测试集相关数据
    splits.append((train_data, test_data))#以（训练、测试集）有序存储
return splits#获取分为n折的训练集与测试集的有序集合
计算用户间相似性；similarity_df = compute_user_similarity(train_user_item_matrix)#训练集计算
用户邻居按照相似性进行排序；similar_users = similarity_df.loc[user_id].drop(user_id).sort_values(ascending=False)
针对测试集中预测目标，预测用户在k个邻居时的可能评分；def predict_rating(user_item_matrix, similarity_df, user_id, movie_id, k):
neighbors = get_neighbors(similarity_df, user_id, k)# 获取 K 个最相似邻居的 ID 列表
numerator = 0#分子：相似度 * 邻居评分
denominator = 0# 分母：相似度的绝对值之和
for neighbor_id in neighbors:# 检查邻居u是否对该电影评过分
    if movie_id in user_item_matrix.loc[neighbor_id].dropna().index:
        similarity = similarity_df.loc[user_id, neighbor_id]# 用户 u 和邻居 v 的相似度
        neighbor_rating = user_item_matrix.loc[neighbor_id, movie_id]#邻居对电影评分
        numerator += similarity * neighbor_rating
        denominator += abs(similarity)
if denominator == 0:# 如果k个邻居都没有评价过这部电影
return user_item_matrix.loc[user_id].mean()#则返回用户的平均评分作为预测值
return numerator / denominator # 返回总的预测评分
计算k个邻居时User-based Pearson-CF的平均绝对误差MAE并画出误差曲线(x轴为k用户数量，y轴为k对应的MAE值)，如图一所示：def calculate_mae(user_item_matrix, similarity_df, test_data, k):
errors = []#存储误差记录用来画图
for _, row in test_data.iterrows():#遍历测试集中的评分记录
    user_id = row['userId']#截取用户名一列
    movie_id = row['movieId']#截取电影名列
    true_rating = row['rating']#截取评分列
    predicted_rating = predict_rating(user_item_matrix, similarity_df, user_id, movie_id, k)#对每条记录预测评分
    error = abs(true_rating - predicted_rating)#计算MAE
    errors.append(error)#存储进入误差列表
return np.mean(errors)

图一 User-based Pearson-CF最终结果的MAE曲线
如图一所示，横轴为邻居数量k（范围 1~200），纵轴为 MAE 值。当k较小时，MAE 值较高且上升迅速；随着k增大，MAE 逐渐降低并趋于平缓。说明邻居数量要至少高于25，这时增加邻居数量能有效降低 Pearson-CF 的预测误差，当邻居数足够大时，误差会稳定在较低水平。
实验问题
报错 ：在计算皮尔逊相关系数时，传入的user_i_ratings[common_movies] 或者user_j_ratings[common_movies]数组中有一个是常数数组，在这种情况下皮尔逊相关系数是没有定义的，会出现相似度为NAN的问题。
报错：在计算皮尔逊相关系数pearsonr时，传入的 user_i_ratings[common_movies] 和 user_j_ratings[common_movies]的长度小于2。而pearsonr函数要求输入的两个数组长度至少为2才能进行有意义的相关系数计算。
编写双循环程序计算用户相似性时，发现运行时间过长，时间复杂度过高，导致程序卡死或无法在短时间内完成。
由于我是通过WSL虚拟机才实现的python notebook编写，因此在获取数据表格时出现FILENOTFOUNDERROR。
与LLM交流
在计算皮尔逊相关系数时，传入的用户i与j的共同评分电影数组中是常数数组怎么避免这种问题？
传入的用户i与j的共同评分电影数组的长度怎么增加限制条件？
计算用户相似度时双循环怎么减少时间复杂度？
原始评分矩阵出现大量缺失值，怎么避免？
在WSL环境如何正确导入数据表格？


二、度量指标
实验概括
我认为这主要是用cosine相似性来去选取距离目标用户的k个邻居用户，然后更多的意义是去使用不同的度量指标来科学评估模型调优与有效性。
实验步骤与结果
选择MovieLens small 数据集；
实现基于用户Cosine相似性的协同过滤（CF）个性化推荐算法；
读入Ratings数据并适当保存和索引； 
def create_user_item_matrix(ratings):# 构建 User-Item 评分矩阵
    user_item_matrix = ratings.pivot(index='userId', columns='movieId', values='rating') #index是行索引，columns是列索引，values是填充值
    return user_item_matrix #pivot数据透视
数据按折n验证分割成训练集和测试集；
计算用户间相似性；
def compute_user_similarity(user_item_matrix):# 计算所有用户之间的余弦相似度矩阵   
    user_item_matrix_filled = user_item_matrix.fillna(0)# 缺失值补0，否则无法计算向量夹角，cosine_similarity 返回一个 n_users x n_users 的矩阵
    similarity_matrix = cosine_similarity(user_item_matrix_filled)
    similarity_df = pd.DataFrame(similarity_matrix, index=user_item_matrix.index, columns=user_item_matrix.index)
    return similarity_df  # 将其转回 DataFrame 格式
用户邻居按照相似性进行排序；
def get_neighbors(similarity_df, user_id, k):#获取该用户与其他人的相似度列
    # drop(user_id) 去掉自己，sort_values 降序排列
    similar_users = similarity_df.loc[user_id].drop(user_id).sort_values(ascending=False)
    return similar_users.head(k).index# 取前 k 个用户的 ID
针对测试集中预测目标，预测用户在k个邻居时的可能评分；
计算k个邻居时User-based Cosine-CF的MAE与RMSE并画出误差曲线；求出MAE最小时的k值k_min；如图二所示
def calculate_metrics(user_item_matrix, similarity_df, test_data, k):
    predicted_ratings = []# 计算特定 k 值下的 MAE 和 RMSE
    true_ratings = []
    for _, row in test_data.iterrows():# 遍历测试集中的每一个样本进行预测
        user_id = row['userId']
        movie_id = row['movieId']
        true_rating = row['rating']
        pred = predict_rating(user_item_matrix, similarity_df, user_id, movie_id, k)# 调用之前的预测函数
        predicted_ratings.append(pred)
        true_ratings.append(true_rating)
    
    
    mae = mean_absolute_error(true_ratings, predicted_ratings)
    rmse = np.sqrt(mean_squared_error(true_ratings, predicted_ratings))
return mae, rmse# 计算误差指标

图二 User-based Cosine-CF最终结果的MAE与RMSE曲线
如图二所示，同时展示了 MAE（蓝色）和 RMSE（橙色）两个指标，横轴为用户邻居数量k，我们发现MAE 与 RMSE 的变化趋势一致，随k增大先快速下降，后逐渐平稳；且 RMSE 始终高于 MAE，说明 Cosine-CF 的预测误差也会随邻居数量增加而降低，最终保持稳定，相对来说极大值要低于皮尔逊算法。
当预测评分大于等于用户平均评分时，将预测评分分类为喜欢，小于用户平均评分是分类为不喜欢，将预测评分进行分类后，再依据相同判别标准将真实评分进行分类，随后计算k=200（即k_min）时，F1、Precision、Recall、Accuracy这四个指标，绘制柱状图，如图三所示：
def calculate_classification_metrics(user_item_matrix, similarity_df, test_data, k):
    predicted_ratings = []
    true_ratings = []
    for _, row in test_data.iterrows():# 先预测所有分数
        user_id = row['userId']
        movie_id = row['movieId']
        predicted_rating = predict_rating(user_item_matrix, similarity_df, user_id, movie_id, k)
        predicted_ratings.append(predicted_rating)
        true_ratings.append(row['rating'])
    user_avg_ratings = user_item_matrix.mean(axis=1)#计算用户平均分作为阈值
    predicted_classes = [# 将连续的评分转化为 0/1 分类结果
        1 if pred >= user_avg_ratings[user_id] else 0 
        for user_id, pred in zip(test_data['userId'], predicted_ratings)
    ]# 逻辑：如果 预测分 >= 该用户的平均分，则标记为 1 (喜欢)，否则为 0
    true_classes = [ # 真实标签也是同样的逻辑
        1 if true >= user_avg_ratings[user_id] else 0 
        for user_id, true in zip(test_data['userId'], true_ratings)
    ]
    f1 = f1_score(true_classes, predicted_classes)#  计算四个分类指标
    precision = precision_score(true_classes, predicted_classes)
    recall = recall_score(true_classes, predicted_classes)
    accuracy = accuracy_score(true_classes, predicted_classes)
    return f1, precision, recall, accuracy

图三 k=k_min时四类指标结果柱状图
如图三所示，这里包含F1、Precision、Recall、Accuracy四个指标，纵轴为指标值。四个指标的数值均处于0.6左右，各指标间差异较小，说明在k=200时，Cosine-CF 对 “喜欢 / 不喜欢” 的分类性能处于中等水平，且各维度表现均衡。
实验问题
预测阶段所用时间过长，使用iterrows()遍历测试集的每一行，然后对每一行再去遍历neighbors，MovieLens Small有100000条评分。如果嵌套循环，Python处理起来极慢，可能跑一折需要半小时。
测试集中出现了训练集中完全没见过的用户 ID 或电影 ID，冷启动报错NaN。
在找Top-K邻居时，是否应该在遍历用户列表时排除“用户自己”，如果不排除预测算法会直接“抄袭”该用户在训练集里的行为，虽然算法本来就是用别人的数据预测已有的，但在逻辑上，邻居应该是“其他人”，怎么处理？
要求说道“当预测评分大于等于用户平均评分时分类为喜欢”，那我这里的用户平均评分选择每个用户不同的平均评分还是所有用户共同对项目们的平均评分，怎么选取更符合逻辑？
与LLM交流
预测函数使用iterrows()遍历测试集的每一行，然后对每一行再去遍历邻居，如何从数据结构角度来解决嵌套循环时间过久的问题？
测试集中要预测用户 U 对电影 M 的评分，但 U 的 K 个邻居里，没人看过 M。此时分母可能为0，怎么通过代码防御机制去解决这种问题？
在找Top-K邻居时，是否应该在遍历用户列表时排除“用户自己”，如果不排除后果会怎么样？如何在代码实际修改去规避这种问题？
用户平均评分选择动态平均作为阈值还是整体平均作为阈值？两者对于结果来说有什么不同影响？


三、User-based Slope One
实验理解
我认为这主要是用slope one算法来预测用户对于某物品的评分，它基于用户对其他物品的评分，计算用户共同对于物品i和j的评分计算偏差来预测目标用户对于未知物品的评分。
实验步骤与结果
选择MovieLens small 数据集；
实现基于用户Slope One距离模型的协同过滤（CF）个性化推荐算法；
class SlopeOne:
    def __init__(self):#初始化模型参数，包括偏差矩阵、频率矩阵和ID映射
        self.dev_matrix = None
        self.freq_matrix = None
        self.item_map = {}
        self.reverse_item_map = {}
        self.n_items = 0
        self.global_mean = 0
    def fit(self, train_data):#训练：计算物品间偏差矩阵和频率矩阵
   # (内部逻辑省略，负责计算物品 i 到物品 j 的平均评分偏差 Dev[i][j])
        mask = self.freq_matrix > 0# 核心步骤：计算平均偏差 (Sum / Count)
        self.dev_matrix[mask] /= self.freq_matrix[mask]
    def predict(self, user_id, item_id, user_ratings_dict):
        """ Slope One 预测：基于加权平均的偏差进行评分预测 """
   # ... (内部逻辑省略，负责根据公式(Rating_j + Dev_ij) * Freq_ij预测评分)
        if pred_denom == 0:# 防止最终分母为0
            return self.global_mean
        return pred_num / pred_denom
读入Ratings数据并适当保存和索引； 
数据按折n验证分割成训练集和测试集；
计算用户间相似性；
def fit(self, train_data):# 在 SlopeOne中，只是通过计算物品偏差矩阵完成了模型训练，不需要计算用户相似性，这里展示如何得到物品偏差矩阵
        # ... (初始化矩阵、分组等)
        # 核心循环优化：遍历用户，累加评分差
        for _, group in tqdm(user_groups, desc="Training Phase", leave=False):
            # ... (内部逻辑省略)
            self.dev_matrix[u_item, v_item] += (u_rating - v_rating)
            self.freq_matrix[u_item, v_item] += 1
        mask = self.freq_matrix > 0# 计算平均偏差 (Sum / Count)，完成训练
        self.dev_matrix[mask] /= self.freq_matrix[mask]
针对测试集中预测目标，预测用户对物品的评分；
# 批量预测测试集循环：
for i in tqdm(range(len(test_data)), desc="Prediction", leave=False):
    u_id = test_users[i]
    i_id = test_items[i]
    r_true = test_ratings[i]# 获取相关变量

    if u_id not in train_user_history:
        pred = model.global_mean # 如果用户在训练集中没有任何数据，无法预测 (冷启动用户)，预测值采用均值
    else:
        user_history = train_user_history[u_id]
        pred = model.predict(u_id, i_id, user_history) #调用模型的预测方法
    y_true.append(r_true)
    y_pred.append(pred)
画出k个邻居时User-based Slope One距离模型的平均绝对误差并画出误差直线（因为Slope One不选邻居，所以k邻居是Slope One结果为一条横线），如图四所示。

图四 slopeone 算法MAE随k变化图
如图四所示，Slope One算法的MAE 曲线呈水平直线（稳定在 0.6973 左右），这是因为 Slope One 是基于物品偏差的算法，不依赖邻居数量k，因此其预测误差不受k的影响，始终保持稳定。
实验问题
我的实验通过双重循环遍历电影项目，其中出现无限等待，因为需要做9000次平方的嵌套循环循环，而且每次循环内部还要去搜寻用户，复杂度爆炸。
在遍历过程中，我的代码出现了众多无效计算，其中大部分电影没有被第二个用户看过，出现空集，我的代码浪费大量时间去计算了空集。
在顺利模型训练结束后，在对数据进行预测时间过程，我发现train_data[train_data['userId'] == user_id]这个代码需要我遍历整个dataframe来找某用户的历史记录。
对于这个算法训练来说，我觉得时间太久了，需要有进度条来显示这个模型的训练进度。
MovieLens的电影ID是不连续的。我该怎么存这个偏差矩阵，用Python的 dict结构会非常“重”，存几百万个键值对会消耗大量内存，而且想做矩阵加减法或者批量运算时，字典不支持，只能写for循环一个个加。
引入ID映射解决存储问题后，稀疏矩阵shape定义未匹配编码后的实际用户 与物品数量，导致索引频繁超出矩阵边界，报错：axis 0 index 671 exceeds matrix dimension 671。
与LLM交流
Slope One 的物品对遍历复杂度是O(N2)，当物品很多时，怎么跳过那些没有人共同评分的物品对？
与其遍历‘物品’去找‘人’，我是不是可以遍历‘人’，只计算这个人看过的物品对？
Pandas的row遍历和条件查询太慢了，我能不能在预测开始前，把所有用户的历史记录预处理成一个哈希表？
如何避免在预测循环中访问DataFrame，只访问原生Python对象？
如何在我的Python循环中，不修改核心计算逻辑的前提下，添加一个平滑的进度条来显示当前的训练进度？
我的MovieID是不连续的整数，怎么把它们映射成0, 1, 2... 这样紧凑的矩阵索引，以便我使用numpy数组？
我使用了ID映射，但为什么在计算偏差矩阵时，索引671仍然超出了维度671？矩阵的shape应该如何精确定义，才能匹配我的编码ID？


四、综合实验
实验理解
我认为这个实验用来比较pearson CF、cosine CF和slope one三种算法在相同实验环境下的对比，以及在不同评价指标下的不同表现。
实验步骤与结果
在一次相同的折五交叉检验实验中，计算5次下面实验结果被求均值；
def run_comprehensive_experiment(): # 主实验 算法串联
    ratings = load_data()
    n_splits = 5 # 定义 K 的折数
    max_k = 200  # 定义 K 的最大范围，影响后续数组长度
    splits = split_data(ratings, n_splits) # 执行数据切分
    # 结果存储: results[算法][指标] = [fold1_arr, fold2_arr...]
    algos = ['Pearson', 'Cosine', 'Slope One']
    metrics_names = ['MAE', 'RMSE', 'F1', 'Precision', 'Recall', 'Accuracy']
    # 初始化嵌套字典，用于存储所有折的结果
    results = {alg: {m: [] for m in metrics_names} for alg in algos}
    print(f"开始综合实验 (Max K={max_k}, Folds={n_splits})...")
    for i, (train_df, test_df) in enumerate(splits):# 遍历 5 次交叉验证
        print(f"\n>>> 正在运行第 {i+1}/{n_splits} 折...")
        # 1. 基础构建（在循环内部，确保训练数据没有泄露）
        train_matrix = create_user_item_matrix(train_df)
        # ... (内部执行三个算法的训练和预测) ...
        # 将本折的结果存储到 results 字典中，等待求均值
        results['Slope One']['MAE'].append(s_res[0])
    # 在所有循环结束后，计算 5 折结果的平均值
    final_avg = np.mean(np.vstack(results[alg][m]), axis=0)
分别绘制Pearson，Cosine，Slope One 三个算法在k邻居变化的情况下的MAE，RMSE两张图，如图五与图六（横轴是k邻居数量，纵轴是MAE和RMSE的值）；
# 在 KFold 循环内部，利用向量化方法，在每一折内并行计算三个算法的全部指标，先训练 Slope One (无 K)
        print("    [1/3] 训练 Slope One...")
        slope_model = SlopeOne()
        slope_model.fit(train_df)
        train_hist = train_df.groupby('userId').apply(lambda x: dict(zip(x.movieId, x.rating))).to_dict()
s_res = evaluate_slope_one(slope_model, test_df, train_hist, train_matrix, max_k) #计算Slope One的所有指标
        for idx, m_name in enumerate(metrics_names):
            results['Slope One'][m_name].append(s_res[idx])
        print("    [2/3] 计算 Cosine Metrics...")# 计算 Cosine (有 K)
        sim_cos = compute_cosine_sim(train_matrix) # Cosine 相似度
        #调用向量化函数，计算 k=1到 k=max_k的所有6个指标
        c_res = calculate_metrics_knn_vectorized(train_matrix, sim_cos, test_df, max_k)
        for idx, m_name in enumerate(metrics_names):
            results['Cosine'][m_name].append(c_res[idx])
        print("    [3/3] 计算 Pearson Metrics...")# 计算 Pearson (有 K)
        sim_pea = compute_pearson_sim(train_matrix) # Pearson 相似度
        p_res = calculate_metrics_knn_vectorized(train_matrix, sim_pea, test_df, max_k)
        for idx, m_name in enumerate(metrics_names):
            results['Pearson'][m_name].append(p_res[idx])

图五 三种算法MAE随k变化图

图六 三种算法RMSE随k变化图
如图五所示，这里对比了Pearson-CF（蓝色曲线）、Cosine-CF（橙色曲线）、Slope One（绿色虚线）三种算法的 MAE 表现。我发现Pearson、Cosine-CF二者均为 “基于用户的协同过滤算法”，他们的MAE 随K增大呈现“先快速下降、后趋于平稳”的趋势，K较小时误差较高，K增大后误差逐步降低并稳定在 0.76 左右；相对应Slope One作为 “基于物品偏差的算法”，其MAE不受K影响，始终保持在0.70左右的稳定水平，且MAE数值显著低于 Pearson/Cosine-CF 的最终稳定值，表现更优。
如图六所示，这里对比了三种算法的RMSE表现，其中Pearson/Cosine-CF与 MAE 趋势一致，RMSE 随K增大先快速下降、后趋于平稳，最终稳定在 0.975 左右；对应Slope One的RMSE 同样不受K影响，始终保持在较低的稳定水平（约 0.95），且RMSE 数值略低于 Pearson/Cosine-CF 的最终稳定值，进一步体现了其预测精度的优势。
分别绘制Pearson，Cosine，Slope One 三个算法在k邻居变化的情况下的F1、Precision、Recall、Accuracy 4张图，分别如图七、八、九、十所示；x轴为k值，y轴为Pearson 、Cosine、和Slope One在k时的四个指标值，上述散点图相连点绘制成对应折线图 注：Slope One因为不筛选邻居；

图七 三种算法F1值随k变化图
如图七所示，这里对比三种算法的 F1 表现，相对应的，Pearson/Cosine-CF在K较小时 F1 值较高，随K增大快速下降，最终趋于平稳，而Slope One的F1 值不受K影响，始终保持在 0.67 左右的稳定水平，且数值显著高于前两者的最终稳定值，分类的综合性能更优。

图八 三种算法Precision值随k变化图
如图八所示，这里对比三种算法的精确率表现，Pearson/Cosine-CF在K较小时精确率较低，随K增大逐步上升，最终趋于平稳（稳定在 0.64 左右），Slope One的精确率不受K影响，始终稳定在 0.68 左右，数值远高于前两者，对“喜欢”类别的预测精准度更优。

图九 三种算法Recall值随k变化图
如图九所示，这里对比三种算法的召回率表现，Pearson/Cosine-CF在K较小时召回率较高，随K增大快速下降，最终趋于平稳（稳定在 0.65 左右），Slope One的召回率不受K影响，始终稳定在 0.68 左右，数值高于前两者的最终稳定值，对用户“喜欢”类别的覆盖能力更优。

图十 三种算法Accuracy值随k变化图
如图十所示，这里对比三种算法的分类准确率表现。其中Pearson/Cosine-CF在K较小时准确率较低，随K增大逐步上升，最终趋于平稳（稳定在 0.62 左右）而Slope One准确率不受K影响，始终稳定在 0.64 左右，数值高于前两者，整体分类正确性更优。
实验问题
我的实验写了三个独立的循环。先跑 Pearson 的 5 折，算出结果；再跑 Cosine 的 5 折；最后跑 Slope One，最终发现 Pearson 跑第一折时用的测试集，和 Cosine 跑第一折时的测试集不一样，似乎因为 shuffle=True 每次产生随机数。导致对比不公平。
在遍历过程中，时间太久，我发现K=1时模型训练了一次，算了一遍相似度；K=2时，模型又重新训练了一次，又算了一遍相似度……一直到 K=200。
我的相似度矩阵（Pearson/Cosine）和偏差矩阵（Slope One）其实只跟训练集有关，跟K无关。但我重复计算了200*5次矩阵，程序要跑好几天。
Slope One算出来是一个单一的数值，Pearson和cosine算出来是一个长度 200 的数组（对应 K=1 到 200），当我尝试 plt.plot(x, y) 时，Python 会报错 x and y must have same first dimension，似乎因为x轴有 200 个点，但 Slope One 的 y只有1个点。
我想求5折的平均值，但Pearson是列表套列表，Slope One是标量，数据结构不统一，写不出通用的 np.mean 代码，均值计算困难。
与LLM交流
我如何确保三个算法在每一折（Fold）中面对的是完全一模一样的训练集和测试集？
我是应该把算法套在 KFold 外面，还是把 KFold 套在算法外面？怎么写代码结构才能让数据切分只发生一次，然后分发给三个模型？
为什么我的程序越跑越慢？K=1和K=100用的相似度矩阵不是同一个吗？为什么我要重复算它？
能不能把‘模型训练’中算矩阵和‘预测评估’中选 TopK彻底拆开？训练只做一次，预测循环 200 次？
能不能连预测都不循环？能不能一次算出所有K的结果？
为了代码的统一性，我是不是应该把 Slope One 的结果人为地广播成一个长度为 200 的数组，里面全是同一个数？



心得体会
我认为这次的推荐系统实验中，我从理论认识、参数调优、工程实现都有了深刻收获。实验结果直观展示Slope One算法在稀疏数据集上的优越性，它本身在算法设计上就有极强鲁棒性，而其中对于k大小的探索也让我理解了算法的权衡之法，对于User-based算法来说也并不是k越大越好，而且随着k的增加，精确值提升，但是召回率却下降。这揭示了推荐系统中存在追求高准确率往往以牺牲高泛化程度为代价，实际应用则需要寻找到其中的平衡点。在代码设计中，我从公式复现到工程优化，初期我多次遭遇双重循环导致的计算爆炸、索引越界等难题，通过与LLM的讨论，我学会了向量化计算、矩阵广播等机制，这让我明白一个优秀的算法工程师，不仅要掌握数学原理，还要懂得高效的数据结构与计算范式，才能跨越从实验室代码到工业应用的鸿沟。
最后再多写一点，我是艾老师两门专业课的学生，在课程的设计中，我最大的收获是“大胆犯错”，这也是艾老师在私信中告诉我的，作为一个致力于保研的学生，我尝尝害怕自己的一点错误导致错失资格，但经过两门课的学习与感悟，我发现其实人生并没有很标准的答案，只要活出自我，每一步都是深刻的收获，感谢老师在专业性极强的教学中也能让我们思考到更多深刻的人生内涵。
