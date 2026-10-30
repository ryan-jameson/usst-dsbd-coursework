# 程序

整理：ryan-jameson。上海理工大学（经管实验班—数据科学与大数据技术专业）。

本文为脱敏文字版。原文中的图片、截图、批注、演讲者备注及嵌入对象未随公开版提供；图示、公式或表格的文字抽取可能不完整。

## 分节 1

1.导入numpy库：
import numpy as np 

2.建立一个一维数组 a 初始化为[4,5,6], (1)输出a 的类型（type）(2)输出a的各维度的大小（shape）(3)输出 a的第一个元素（值为4）：
a = np.array([4, 5, 6])
print(type(a))
print(a.shape)
print(a[0])
RESULT:
<class 'numpy.ndarray'>
(3,)
4

建立一个二维数组 b,初始化为 [ [4, 5, 6],[1, 2, 3]] (1)输出各维度的大小（shape）(2)输出 b(0,0)，b(0,1),b(1,1) 这三个元素（对应值分别为4,5,2）：
b = np.array([[4, 5, 6], [1, 2, 3]])
print(b.shape)
print(b[0, 0], b[0, 1], b[1, 1])
RESULT:
(2, 3)
4 5 2

4. (1)建立一个全0矩阵 a, 大小为 3x3; 类型为整型（提示: dtype = int）(2)建立一个全1矩阵b,大小为4x5;  (3)建立一个单位矩阵c ,大小为4x4; (4)生成一个随机数矩阵d,大小为 3x2.：
a = np.zeros((3, 3), dtype=int)
b = np.ones((4, 5))
c = np.eye(4)
d = np.random.random((3, 2))
print("a:", a)
print("b:", b)
print("c:", c)
print("d:", d)
RESULT:
a: [[0 0 0]
 [0 0 0]
 [0 0 0]]
b: [[1. 1. 1. 1. 1.]
 [1. 1. 1. 1. 1.]
 [1. 1. 1. 1. 1.]
 [1. 1. 1. 1. 1.]]
c: [[1. 0. 0. 0.]
 [0. 1. 0. 0.]
 [0. 0. 1. 0.]
 [0. 0. 0. 1.]]
d: [[0.30474088 0.0563447 ]
 [0.91247037 0.30607498]
 [0.91180364 0.97269153]]

5.建立一个数组 a,(值为[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]] ) ,(1)打印a; (2)输出  下标为(2,3),(0,0) 这两个数组元素的值：
a = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print(a)
print(a[2, 3], a[0, 0])
RESULT:
[[ 1  2  3  4]
 [ 5  6  7  8]
 [ 9 10 11 12]]
12 1

6.把上一题的 a数组的 0到1行 2到3列，放到b里面去，（此处不需要从新建立a,直接调用即可）(1),输出b;(2) 输出b 的（0,0）这个元素的值：
b = a[0:2, 2:4]
print(b)
print(b[0, 0])
RESULT:
[[3 4]
 [7 8]]
3

7.把第5题中数组a的最后两行所有元素放到 c中，（提示： a[1:2, :]）(1)输出 c ; (2) 输出 c 中第一行的最后一个元素（提示，使用 -1 表示最后一个元素）：
c = a[-2:, :]
print(c)
print(c[0, -1])
RESULT:
[[ 5  6  7  8]
 [ 9 10 11 12]]
8

8.建立数组a,初始化a为[[1, 2], [3, 4], [5, 6]]，输出 （0,0）（1,1）（2,0）这三个元素（提示： 使用 print(a[[0, 1, 2], [0, 1, 0]]) ）：
a = np.array([[1, 2], [3, 4], [5, 6]])
print(a[[0, 1, 2], [0, 1, 0]])
RESULT:
[1 4 5]

9.建立矩阵a ,初始化为[[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]，输出(0,0),(1,2),(2,0),(3,1) (提示使用 b = np.array([0, 2, 0, 1])   print(a[np.arange(4), b]))：
a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
b = np.array([0, 2, 0, 1])
print(a[np.arange(4), b])
RESULT:
[ 1  6  7 11]

10.对9 中输出的那四个元素，每个都加上10，然后重新输出矩阵a.(提示： a[np.arange(4), b] += 10 ）：
a[np.arange(4), b] += 10
print(a)
RESULT:
[[11  2  3]
 [ 4  5 16]
 [17  8  9]
 [10 21 12]]

11.执行 x = np.array([1, 2])，然后输出 x 的数据类型：
x = np.array([1, 2])
print(x.dtype)
RESULT:
int32

12.执行 x = np.array([1.0, 2.0]) ，然后输出 x 的数据类类型：
x = np.array([1.0, 2.0])
print(x.dtype)
RESULT:
float64

13.执行 x = np.array([[1, 2], [3, 4]], dtype=np.float64) ，y = np.array([[5, 6], [7, 8]], dtype=np.float64)，然后输出 x+y ,和 np.add(x,y)：
x = np.array([[1, 2], [3, 4]], dtype=np.float64)
y = np.array([[5, 6], [7, 8]], dtype=np.float64)
print(x + y)
print(np.add(x, y))
RESULT:
[[ 6.  8.]
 [10. 12.]]
[[ 6.  8.]
 [10. 12.]]

14.利用 13题目中的x,y 输出 x-y 和 np.subtract(x,y)：
print(x - y)
print(np.subtract(x, y))
RESULT:
[[-4. -4.]
 [-4. -4.]]
[[-4. -4.]
 [-4. -4.]]

15.利用13题目中的x，y 输出 x*y ,和 np.multiply(x, y) 还有  np.dot(x,y),比较差异。然后自己换一个不是方阵的试试：
print(x * y)
print(np.multiply(x, y))
print(np.dot(x, y))

# 测试不是方阵的情况
x2 = np.array([[1, 2, 3], [4, 5, 6]])
y2 = np.array([[1, 2], [3, 4], [5, 6]])
print("非方阵点乘结果:\n", np.dot(x2, y2))
RESULT:
[[ 5. 12.]
 [21. 32.]]
[[ 5. 12.]
 [21. 32.]]
[[19. 22.]
 [43. 50.]]
非方阵点乘结果:
 [[22 28]
 [49 64]]

16.利用13题目中的x,y,输出 x / y .(提示 ： 使用函数 np.divide())：
print(x / y)
print(np.divide(x, y))
RESULT:
[[0.2        0.33333333]
 [0.42857143 0.5       ]]
[[0.2        0.33333333]
 [0.42857143 0.5       ]]

17.利用13题目中的x,输出 x的 开方。(提示： 使用函数 np.sqrt() )：
print(np.sqrt(x))
RESULT:
[[1.         1.41421356]
 [1.73205081 2.        ]]

18.利用13题目中的x,y ,执行 print(x.dot(y)) 和 print(np.dot(x,y))：
print(x.dot(y))
print(np.dot(x, y))
RESULT:
[[19. 22.]
 [43. 50.]]
[[19. 22.]
 [43. 50.]]

19.利用13题目中的 x,进行求和。提示：输出三种求和 (1)print(np.sum(x)):  (2)print(np.sum(x，axis =0 ));  (3)print(np.sum(x,axis = 1))：
a = np.array([4, 5, 6])
print(type(a))
print(a.shape)
print(a[0])
RESULT:
10.0
[4. 6.]
[3. 7.]

20.利用13题目中的 x,进行求平均数（提示：输出三种平均数(1)print(np.mean(x))(2)print(np.mean(x,axis=0))(3)print(np.mean(x,axis =1))）：
print(np.mean(x))
print(np.mean(x, axis=0))
print(np.mean(x, axis=1))
RESULT:
2.5
[2. 3.]
[1.5 3.5]

21.利用13题目中的x，对x 进行矩阵转置，然后输出转置后的结果，（提示： x.T 表示对 x 的转置）：
print(x.T)
RESULT:
[[1. 3.]
 [2. 4.]]

22.利用13题目中的x,求e的指数（提示： 函数 np.exp()）：
print(np.exp(x))
RESULT:
[[ 2.71828183  7.3890561 ]
 [20.08553692 54.59815003]]

23.利用13题目中的 x,求值最大的下标（提示(1)print(np.argmax(x)) ,(2) print(np.argmax(x, axis =0))(3)print(np.argmax(x),axis =1))：
print(np.argmax(x))
print(np.argmax(x, axis=0))
print(np.argmax(x, axis=1))
RESULT:
3
[1 1]
[1 1]

24.画图，y=x*x 其中 x = np.arange(0, 100, 0.1) （提示这里用到  matplotlib.pyplot 库）：
import matplotlib.pyplot as plt

x_plt = np.arange(0, 100, 0.1)
y_plt = x_plt * x_plt
plt.plot(x_plt, y_plt)
plt.show()

25.画图。画正弦函数和余弦函数， x = np.arange(0, 3 * np.pi, 0.1)(提示：这里用到 np.sin() np.cos() 函数和 matplotlib.pyplot 库)：
x_trig = np.arange(0, 3 * np.pi, 0.1)
y_sin = np.sin(x_trig)
y_cos = np.cos(x_trig)

plt.plot(x_trig, y_sin, label='sin')
plt.plot(x_trig, y_cos, label='cos')
plt.legend()
plt.show() 
高斯函数与多项式奇函数以及最小二乘法：
1.完成 `exercise-linear_regression.ipynb`基函数实现：
def multinomial_basis(x, feature_num=10):
    '''多项式基函数'''
    x = np.expand_dims(x, axis=1) # shape(N, 1)
    powers = np.arange(1, feature_num + 1, dtype=np.float32).reshape(1, -1)
    ret = x ** powers
    return ret

def gaussian_basis(x, feature_num=10):
    '''高斯基函数'''
    x = np.expand_dims(x, axis=1)
    # 使用均匀分布的中心, 训练集 x 范围大约在 [0, 25]
    mus = np.linspace(0.0, 25.0, feature_num, dtype=np.float32).reshape(1, -1)
    if feature_num > 1:
        sigma = (25.0 - 0.0) / (feature_num - 1)
    else:
        sigma = 1.0
    ret = np.exp(-0.5 * ((x - mus) / sigma) ** 2)
    return ret

2.完成 `exercise-linear_regression.ipynb`最小二乘法优化：
 w = np.linalg.pinv(phi) @ y_train

3.完成 `exercise-linear_regression.ipynb`梯度下降优化：
use_gd = False
if use_gd:
    w = np.zeros(phi.shape[1], dtype=np.float32)
    lr = 1e-4
    for _ in range(20000):
        grad = 2.0 * (phi.T @ (phi @ w - y_train))
        w = w - lr * grad

1.Sigmoid 函数：
def compute_loss(pred, label):
    label = tf.convert_to_tensor(label, dtype=tf.float32)
    pred = tf.squeeze(pred, axis=1)
    # 输入label shape(N,), pred shape(N,)
    # 输出 losses shape(N,) 每一个样本一个loss
    # 这里实现了二分类交叉熵损失：- [ y * log(p) + (1 - y) * log(1 - p) ]
    # 加上 epsilon 是为了防止 log(0) 导致数值不稳定产生 NaN
    losses = -(label * tf.math.log(pred + epsilon) + (1.0 - label) * tf.math.log(1.0 - pred + epsilon))    
    loss = tf.reduce_mean(losses)
    
    pred = tf.where(pred>0.5, tf.ones_like(pred), tf.zeros_like(pred))
    accuracy = tf.reduce_mean(tf.cast(tf.equal(label, pred), dtype=tf.float32))
    return loss, accuracy

2.在__init__构造函数中建立模型所需的参数：
def __init__(self):
        self.W = tf.Variable(
            shape=[2, 3],
            dtype=tf.float32,
            initial_value=tf.random.uniform(shape=[2, 3], minval=-0.1, maxval=0.1),
        )
        self.b = tf.Variable(shape=[3], dtype=tf.float32, initial_value=tf.zeros(shape=[3]))
        self.trainable_variables = [self.W, self.b]

3.实现softmax的交叉熵损失函数(不使用tf内置的loss 函数)：
def compute_loss(pred, label):
    label = tf.one_hot(tf.cast(label, dtype=tf.int32), dtype=tf.float32, depth=3)
    #输入label shape(N, 3), pred shape(N, 3)
    #输出 losses shape(N,) 每一个样本一个loss
    losses = -tf.reduce_sum(label * tf.math.log(pred + epsilon), axis=1)
    loss = tf.reduce_mean(losses)
    
    accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(label,axis=1), tf.argmax(pred, axis=1)), dtype=tf.float32))
return loss, accuracy


1.补充SVM逻辑：
class SVM():
    """
    SVM模型。
    """
    def __init__(self, lr=1e-3, lambda_=1e-2, n_iters=20000):
        self.lr = float(lr)
        self.lambda_ = float(lambda_)
        self.n_iters = int(n_iters)
        # Model parameters: y = sign(w^T x + b)
        self.w = None
        self.b = 0.0

    def train(self, data_train):
        """
        训练模型。
        """
        # data_train: [x1, x2, t]
        x = data_train[:, :2].astype(np.float64)
        t = data_train[:, 2].astype(np.int64)
        # Ensure labels are in {-1, +1}
        t = np.where(t > 0, 1, -1)
        n_samples, n_features = x.shape
        self.w = np.zeros(n_features, dtype=np.float64)
        self.b = 0.0
        # Subgradient descent on primal objective:
        # 0.5*lambda*||w||^2 + mean(max(0, 1 - t*(w^T x + b)))
        for _ in range(self.n_iters):
            margins = t * (x @ self.w + self.b)
            mis = margins < 1.0
            if np.any(mis):
                grad_w = self.lambda_ * self.w - (t[mis, None] * x[mis]).mean(axis=0)
                grad_b = -(t[mis]).mean()
            else:
                grad_w = self.lambda_ * self.w
                grad_b = 0.0
            self.w -= self.lr * grad_w
            self.b -= self.lr * grad_b

    def predict(self, x):
        """
        预测标签。
        """
        x = np.asarray(x, dtype=np.float64)
        scores = x @ self.w + self.b
        pred = np.where(scores >= 0.0, 1, -1)
        return pred

2.补充数据载入：
here = os.path.dirname(os.path.abspath(__file__))
train_file = os.path.join(here, 'data', 'train_linear.txt')
test_file = os.path.join(here, 'data', 'test_linear.txt')
data_train = load_data(train_file)  # 数据格式[x1, x2, t]
data_test = load_data(test_file)


1.Softmax 函数：
def softmax(x):
    '''实现 softmax 函数，只要求对最后一维归一化。'''
    # 将输入转换为 TensorFlow 张量，保证后续运算类型统一
    x = tf.convert_to_tensor(x)
    # 为了提升数值稳定性，先减去最后一维上的最大值
    # 这样做不会改变 softmax 的结果，但可以避免 exp 溢出
    x = x - tf.reduce_max(x, axis=-1, keepdims=True)
    # 对平移后的结果逐元素取指数
    exp_x = tf.exp(x)
    # 对最后一维求和并归一化，得到每一类的概率
    prob_x = exp_x / tf.reduce_sum(exp_x, axis=-1, keepdims=True)
    # 返回 softmax 概率结果
    return prob_x

2.Sigmoid 函数：
def sigmoid(x):
    '''实现 sigmoid 函数。'''
    # 将输入转换为 TensorFlow 张量
    x = tf.convert_to_tensor(x)
    # 按照 sigmoid 公式进行计算：1 / (1 + e^(-x))
    prob_x = 1.0 / (1.0 + tf.exp(-x))
    # 返回 sigmoid 输出结果
    return prob_x

3.实现softmax的交叉熵损失函数：
def softmax_ce(x, label):
    '''实现 softmax 交叉熵 loss（输入 x 为 softmax 概率）。'''
    # 将输入概率转换为张量
    x = tf.convert_to_tensor(x)
    # 将标签转成与 x 相同的数据类型，避免计算时类型不一致
    label = tf.cast(label, x.dtype)
    # 设置一个很小的常数，防止 log(0) 导致数值错误
    eps = tf.constant(1e-12, dtype=x.dtype)
    # 先按类别维度求和，再对 batch 维度求平均
    loss = -tf.reduce_mean(tf.reduce_sum(label * tf.math.log(x + eps), axis=-1))
    # 返回平均损失
    return loss

4.实现sigmoid的交叉熵损失函数：
def sigmoid_ce(x, label):
    '''实现 sigmoid 交叉熵 loss（输入 x 为 sigmoid 概率）。'''
    # 将输入概率转换为张量
    x = tf.convert_to_tensor(x)
    # 将标签数据类型转换为与输入一致
    label = tf.cast(label, x.dtype)
    # 加入极小值，防止 log(0)
    eps = tf.constant(1e-12, dtype=x.dtype)
    # 二分类交叉熵公式：
    # loss = - [ y*log(x) + (1-y)*log(1-x) ]
    # 最后对整个 batch 求平均
    loss = -tf.reduce_mean(
        label * tf.math.log(x + eps) +
        (1.0 - label) * tf.math.log(1.0 - x + eps)
    )
    # 返回平均损失
    return loss

5.Numpy手写算子定义（Matmul 类）：
class Matmul:
    def __init__(self):
        # mem 用来缓存前向传播中的输入，供反向传播使用
        self.mem = {}
    def forward(self, x, W):
        # 执行矩阵乘法：h = xW
        h = np.matmul(x, W)
        # 将输入 x 和权重 W 保存下来，方便 backward 求导
        self.mem = {'x': x, 'W': W}
        # 返回线性变换结果
        return h
    
    def backward(self, grad_y):
        '''
        x: shape(N, d)
        W: shape(d, d')
        grad_y: shape(N, d')
        '''
        # 取出前向传播时缓存的输入与权重
        x = self.mem['x']
        W = self.mem['W']
        '''计算矩阵乘法的对应的梯度'''
        # 对输入 x 的梯度
        grad_x = np.matmul(grad_y, W.T)
        # 对权重 W 的梯度
        grad_W = np.matmul(x.T, grad_y)
        # 返回输入梯度和参数梯度
        return grad_x, grad_W

6.Numpy手写算子定义（ReLu 类）：
class Relu:
    def __init__(self):
        # 缓存输入，便于反向传播时判断哪些位置大于 0
        self.mem = {}
    def forward(self, x):
        # 保存输入 x
        self.mem['x'] = x
        # ReLU 激活：大于 0 的部分保持不变，小于等于 0 的部分变成 0
        return np.where(x > 0, x, np.zeros_like(x))
    def backward(self, grad_y):
        '''grad_y: same shape as x'''
        '''计算relu 激活函数对应的梯度'''
        # 取出前向传播时保存的输入
        x = self.mem['x']
        # ReLU 的导数：
        # 当 x > 0 时导数为 1
        # 否则导数为 0
        grad_x = grad_y * (x > 0).astype(x.dtype)
        # 返回对输入 x 的梯度
        return grad_x

7.Numpy手写算子定义（Softmax 类）：
class Softmax:
    '''softmax over last dimention'''
    def __init__(self):
        # 防止分母为 0 的极小值
        self.epsilon = 1e-12
        # 保存前向传播中间结果，供反向传播使用
        self.mem = {}
    def forward(self, x):
        '''x: shape(N, c)'''
        # 对输入逐元素取指数
        x_exp = np.exp(x)
        # 按类别维度求和，作为 softmax 分母
        partition = np.sum(x_exp, axis=1, keepdims=True)
        # 计算 softmax 输出概率
        out = x_exp / (partition + self.epsilon)
        # 保存输出和指数结果，供 backward 使用
        self.mem['out'] = out
        self.mem['x_exp'] = x_exp
        # 返回 softmax 概率
        return out
    
    def backward(self, grad_y):
        '''grad_y: same shape as x'''
        # 取出 softmax 输出
        s = self.mem['out']
        # 构造 softmax Jacobian 矩阵中的 s_i * s_j 项
        sisj = np.matmul(
            np.expand_dims(s, axis=2),
            np.expand_dims(s, axis=1)
        )  # shape: (N, c, c)
        # 将上游梯度扩展维度，便于矩阵乘法
        g_y_exp = np.expand_dims(grad_y, axis=1)
        # 计算梯度传播过程中的中间项
        tmp = np.matmul(g_y_exp, sisj)  # shape: (N, 1, c)
        # 去掉多余维度
        tmp = np.squeeze(tmp, axis=1)
        # softmax 反向传播公式
        tmp = -tmp + grad_y * s
        # 返回对输入 x 的梯度
        return tmp

6.Numpy手写算子定义（Log 类）：
class Log:
    '''softmax over last dimention'''
    def __init__(self):
        # 防止出现 log(0)
        self.epsilon = 1e-12
        # 缓存前向传播输入
        self.mem = {}
        
    def forward(self, x):
        '''x: shape(N, c)'''
        # 计算对数，加入 epsilon 保证数值稳定
        out = np.log(x + self.epsilon)
        # 保存输入 x，供反向传播使用
        self.mem['x'] = x
        # 返回 log 结果
        return out
    
    def backward(self, grad_y):
        '''grad_y: same shape as x'''
        # 取出前向传播输入
        x = self.mem['x']
        # log(x) 的导数为 1/x
        # 再乘以上游梯度 grad_y
        return 1. / (x + 1e-12) * grad_y
三 数据采集：
1. 数据来源：程序使用了MNIST 手写数字数据集，该数据集通过 TensorFlow Keras 内置的数据集接口直接下载和加载：keras.datasets.mnist.load_data()。这会自动从官方网络源下载数据集，并将其直接读入内存。
2. 数据结构：加载后的数据被划分为了两部分：训练集(train_data) 和测试集(test_data)。
x（图像特征）：形状为(N, 28, 28)的二维矩阵数组，表示N张28×28像素的灰度图片。
y（类别标签）：形状为(N,)的一维数组，代表图片的正确分类，即0∼9的整数。
3. 数据预处理（归一化与类型转换）
归一化处理：刚加载进来的图片像素值的范围是0∼255。为了使神经网络模型能够更稳定、快速地通过梯度下降收敛，程序将所有像素点数值除以255.0，把取值范围线性映射归一化到了[0,1]之间。
数据类型转换：在进行除法时，程序通过.astype(np.float32)显式地将输入的图像矩阵转换为了单精度浮点型float32，这符合 TensorFlow 在底层进行张量计算时的默认类型标准；而类标y保持为适合索引的整型 (int64 / int32)。
def mnist_dataset():
    """Load MNIST and normalize images to [0, 1].

    Returns:
        (x, y), (x_test, y_test)
        x/x_test: float32, shape (N, 28, 28)
        y/y_test: int64, shape (N,)
    """
    # 通过 Keras 内置接口加载 MNIST 数据集
    # x, y 为训练集；x_test, y_test 为测试集
    (x, y), (x_test, y_test) = datasets.mnist.load_data()
    # 将训练集图像从 uint8 转为 float32，并归一化到 [0,1]
    x = x.astype(np.float32) / 255.0
    # 将测试集图像从 uint8 转为 float32，并归一化到 [0,1]
    x_test = x_test.astype(np.float32) / 255.0
    # 返回处理后的训练集和测试集
    return (x, y), (x_test, y_test)

四 模型描述：
1.Tensorflow模型：
class myModel:
    def __init__(self):
        """Two-layer fully-connected network for MNIST.

        - 输入 x: shape (N, 28, 28), dtype float32, 值域 [0, 1]
        - 输出 logits: shape (N, 10), 未经过 softmax 的分类分数
        """
        # 设置隐藏层神经元个数
        hidden_dim = 100
        # 初始化第一层权重 W1
        # 输入维度为 28*28，输出到 hidden_dim
        # 使用标准差较小的随机初始化，便于训练稳定
        self.W1 = tf.Variable(
            tf.random.normal([28 * 28, hidden_dim], stddev=0.1),
            name='W1'
        )
        # 初始化第一层偏置 b1，初始为 0
        self.b1 = tf.Variable(tf.zeros([hidden_dim]), name='b1')
        # 初始化第二层权重 W2
        # 输入维度为 hidden_dim，输出维度为 10 类
        self.W2 = tf.Variable(
            tf.random.normal([hidden_dim, 10], stddev=0.1),
            name='W2'
        )
        # 初始化第二层偏置 b2
        self.b2 = tf.Variable(tf.zeros([10]), name='b2')

    def __call__(self, x):
        """前向计算，返回未归一化 logits。
        x: (N, 28, 28)
        return: logits (N, 10)
        """
        # 将输入转换为 float32 类型
        x = tf.cast(x, tf.float32)
        # 将 28×28 的图像展平成 784 维向量
        x = tf.reshape(x, [-1, 28 * 28])
        # 第一层全连接：h1 = xW1 + b1
        h1 = tf.matmul(x, self.W1) + self.b1
        # 经过 ReLU 激活函数
        h1 = tf.nn.relu(h1)
        # 第二层全连接，输出 10 个类别的 logits
        logits = tf.matmul(h1, self.W2) + self.b2
        # 返回最终输出
        return logits

2.Numpy模型：
class myModel:
    def __init__(self):
        # 初始化第一层权重矩阵 W1
        # 输入维度为 28*28，再额外加 1 维作为 bias 输入
        # 输出维度为 100
        self.W1 = np.random.normal(size=[28 * 28 + 1, 100])
        # 初始化第二层权重矩阵 W2
        # 输入维度为 100，输出维度为 10
        self.W2 = np.random.normal(size=[100, 10])
        # 定义前向传播和反向传播中需要用到的各类算子
        self.mul_h1 = Matmul()
        self.mul_h2 = Matmul()
        self.relu = Relu()
        self.softmax = Softmax()
        self.log = Log()
        
    def forward(self, x):
        """前向传播：从输入图片得到 log(prob)。
        x: (N, 28, 28)
        产生的中间量会保存在 self.*，供 backward 使用。
        """
        # 将输入图片展平为二维矩阵，每张图像变成 784 维向量
        x = x.reshape(-1, 28 * 28)
        # 构造 bias 列，全部填 1
        bias = np.ones(shape=[x.shape[0], 1])
        # 将 bias 拼接到输入最后一维，实现“带偏置的输入”
        x = np.concatenate([x, bias], axis=1)
        # 第一层线性变换
        self.h1 = self.mul_h1.forward(x, self.W1)
        # 第一层经过 ReLU 激活
        self.h1_relu = self.relu.forward(self.h1)
        # 第二层线性变换
        self.h2 = self.mul_h2.forward(self.h1_relu, self.W2)
        # 通过 softmax 得到类别概率
        self.h2_soft = self.softmax.forward(self.h2)
        # 对概率取对数，后续便于计算交叉熵损失
        self.h2_log = self.log.forward(self.h2_soft)
            
    def backward(self, label):
        """反向传播：从 label 得到各层参数梯度。
        label: one-hot, shape (N, 10)
        损失：L = - mean(sum(label * log(prob)))
        对 log(prob) 的梯度：dL/dlogp = -label / N。这里把 1/N 的系数合并到学习率中处理。
        """
        # 从损失函数对 log(prob) 的梯度开始反向传播
        self.h2_log_grad = self.log.backward(-label)
        # 继续通过 softmax 层反向传播
        self.h2_soft_grad = self.softmax.backward(self.h2_log_grad)
        # 第二层线性层反向传播，得到 h1_relu 的梯度和 W2 的梯度
        self.h2_grad, self.W2_grad = self.mul_h2.backward(self.h2_soft_grad)
        # ReLU 层反向传播
        self.h1_relu_grad = self.relu.backward(self.h2_grad)
        # 第一层线性层反向传播，得到输入梯度和 W1 的梯度
        self.h1_grad, self.W1_grad = self.mul_h1.backward(self.h1_relu_grad)

1.Pytorch版CNN补全：
class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(
                in_channels=1,
                out_channels=32,
                kernel_size=7,
                stride=1,
                padding=3,
            ),
            nn.ReLU(),        # activation function
            nn.MaxPool2d(2),  # pooling operation
        )
        self.conv2 = nn.Sequential(
            nn.Conv2d(
                in_channels=32,
                out_channels=64,
                kernel_size=5,
                stride=1,
                padding=2,
            ),
            nn.ReLU(),
            nn.MaxPool2d(2),

        )
        self.out1 = nn.Linear( 7*7*64 , 1024 , bias= True)   

        self.dropout = nn.Dropout(p=1 - keep_prob_rate)
        self.out2 = nn.Linear(1024,10,bias=True)

    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = x.view(x.size(0), -1)  # flatten to (batch_size, 7 * 7 * 64)
        out1 = self.out1(x)
        out1 = F.relu(out1)
        out1 = self.dropout(out1)
        out2 = self.out2(out1)
        return out2

2.Tensorflow卷积参数补充：
def conv2d(x, W):
    # 每一维度  滑动步长全部是 1， padding 方式 选择 same
    return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

def max_pool_2x2(x):
# 滑动步长 是 2步; 池化窗口的尺度 高和宽度都是2; padding 方式 请选择 same
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

#  卷积层 1
## conv1 layer ##
W_conv1 = weight_variable([7, 7, 1, 32])  # patch 7x7, in size 1, out size 32
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
h_pool1 = max_pool_2x2(h_conv1)

# 卷积层 2
W_conv2 = weight_variable([5, 5, 32, 64])  # patch 5x5, in size 32, out size 64
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

1.Tensorflow版本RNN模型补全（加法进位）：
def call(self, num1, num2):
        emb1 = self.embed_layer(num1)
        emb2 = self.embed_layer(num2)
        x = tf.concat([emb1, emb2], axis=-1)
        h = self.rnn_layer(x)
        logits = self.dense(h)
        return logits

2.Tensorflow版本RNN模型补全（诗歌生成）：
def call(self, inp_ids):
        inp_emb = self.embed_layer(inp_ids)
        rnn_out = self.rnn_layer(inp_emb)
        logits = self.dense(rnn_out)
        return logits

3.诗歌生成一步优化过程补全：
def train_one_step(model, optimizer, x, y, seqlen):
    with tf.GradientTape() as tape:
        logits = model(x)
        loss = compute_loss(logits, y, seqlen)
    grads = tape.gradient(loss, model.trainable_variables)
    optimizer.apply_gradients(zip(grads, model.trainable_variables))
    return loss
三 实验优化：
1.Pytorch版本RNN模型补全：
class RNN_model(nn.Module):
    def __init__(self, batch_sz ,vocab_len ,word_embedding,embedding_dim, lstm_hidden_dim):
        super(RNN_model,self).__init__()

        self.word_embedding_lookup = word_embedding
        self.batch_size = batch_sz
        self.vocab_length = vocab_len
        self.word_embedding_dim = embedding_dim
        self.lstm_dim = lstm_hidden_dim

        self.rnn_lstm = nn.LSTM(
            input_size=embedding_dim,
            hidden_size=lstm_hidden_dim,
            num_layers=2,
            batch_first=True,
        )

        self.fc = nn.Linear(lstm_hidden_dim, vocab_len )
        self.apply(weights_init) # call the weights initial function.

        self.softmax = nn.LogSoftmax() # the activation function.
        # self.tanh = nn.Tanh()
    def forward(self,sentence,is_test = False):
        batch_input = self.word_embedding_lookup(sentence).view(1,-1,self.word_embedding_dim)

        h0 = torch.zeros(2, batch_input.size(0), self.lstm_dim, dtype=batch_input.dtype, device=batch_input.device)
        c0 = torch.zeros(2, batch_input.size(0), self.lstm_dim, dtype=batch_input.dtype, device=batch_input.device)
        output, _ = self.rnn_lstm(batch_input, (h0, c0))

        out = output.contiguous().view(-1,self.lstm_dim)
        out =  F.relu(self.fc(out))
        out = self.softmax(out)
        if is_test:
            prediction = out[ -1, : ].view(1,-1)
            output = prediction
        else:
           output = out
        return output

2.Tensorflow版本RNN模型优化：
#第一次训练输出会出现全是标点符号的情况
def get_next_token(self, x, state, temperature=1.0):
        '''
        shape(x) = [b_sz,] 
        '''
        #由于标点符号等高频词在数据集中非常普遍，采用温度采样对实际词采样用概率分布进行，这样可以避免一直采样到标点符号这样的高频词语
        inp_emb = self.embed_layer(x) #shape(b_sz, emb_sz)
        h, state = self.rnncell.call(inp_emb, state) # shape(b_sz, h_sz)
        logits = self.dense(h) # shape(b_sz, v_sz)
        # 引入温度采样，替代原来的 out = tf.argmax(logits, axis=-1)
        logits = logits / temperature
        out = tf.random.categorical(logits, num_samples=1)
        out = tf.squeeze(out, axis=-1)
        out = tf.cast(out, tf.int32)
        return out, state

3.诗歌生成输出优化：
#保持对于诗歌七言律诗的约束，同时约束它只有在最后一处才能使用标点符号
def gen_sentence(start_word=None, temperature=1.0):
    state = [tf.zeros((1, 128), dtype=tf.float32)]
    if start_word is None:
        cur_token = tf.constant([word2id['bos']], dtype=tf.int32)
    else:
        cur_token = tf.constant([word2id.get(start_word, word2id['UNK'])], dtype=tf.int32)
    collect = []
    punctuations = set(['，', '。', '？', '！', ',', '.'])
    # 加上给定的 start_word，我们只需再连续生成6个非标点汉字，凑齐七言
    for _ in range(6):
        for _ in range(50):  # 失败重试机制，避免死循环
            next_token, next_state = model.get_next_token(cur_token, state, temperature=tf.constant(temperature, dtype=tf.float32))
            t = int(next_token.numpy()[0])
            w = id2word.get(t, 'UNK')
            # 如果预测出的是标点或特殊字符则拒绝，并直接进行下一次采样尝试
            # 只有预测出汉字才会更新 cur_token 和状态 state
            if w not in punctuations and w not in ('PAD', 'UNK', start_token, end_token):
                cur_token = next_token
                state = next_state
                collect.append(w)
                break
                
    return collect

def gen_acrostic(head_chars, temperature=1.0):
    lines = []
    for i, ch in enumerate(head_chars):
        # 每次固定生成一句包含7个中文字符的句子
        words = gen_sentence(start_word=ch, temperature=temperature)
        # 在句子末尾加上规范的标点符号，奇数行逗号，偶数行句号
        punc = '，' if i % 2 == 0 else '。'
        lines.append(ch + ''.join(words) + punc)
    return '\n'.join(lines)

# 测试生成一首严格限制格式的七言藏头诗
print(gen_acrostic('日红山夜湖海月', temperature=1.0))
1.完成sequence2sequence 模型的搭建：
def call(self, enc_ids, dec_ids):
        '''
        模块已经在`__init__`函数中定义好
        '''
        enc_emb = self.embed_layer(enc_ids)
        _, enc_state = self.encoder(enc_emb)

        dec_emb = self.embed_layer(dec_ids)
        dec_out, _ = self.decoder(dec_emb, initial_state=enc_state)
        logits = self.dense(dec_out)
        return logits

2.完成带attention机制的 sequence2sequence 模型的搭建：
def call(self, enc_ids, dec_ids):
        '''
        模块已经在`__init__`函数中定义好，
        用双线性attention，或者自己改一下`__init__`函数做加性attention
        '''
        # Encoder
        enc_emb = self.embed_layer(enc_ids)  # (b, enc_len, emb)
        enc_out, enc_state = self.encoder(enc_emb)  # (b, enc_len, h), (b, h)
        # Decoder (teacher forcing)
        dec_emb = self.embed_layer(dec_ids)  # (b, dec_len, emb)
        dec_out, _ = self.decoder(dec_emb, initial_state=enc_state)  # (b, dec_len, h)
        # Bilinear attention (Luong-style): score = <Wq * q, k>
        q = self.dense_attn(dec_out)  # (b, dec_len, h)
        scores = tf.matmul(q, enc_out, transpose_b=True)  # (b, dec_len, enc_len)
        weights = tf.nn.softmax(scores, axis=-1)
        context = tf.matmul(weights, enc_out)  # (b, dec_len, h)
        fused = tf.concat([dec_out, context], axis=-1)  # (b, dec_len, 2h)
        logits = self.dense(fused)  # (b, dec_len, v_sz)
        return logits

3.构建单步解码逻辑：
def get_next_token(self, x, state, enc_out):
        '''
        shape(x) = [b_sz,] 
        '''
        inp_emb = self.embed_layer(x)  # (b, emb)
        h, state = self.decoder_cell.call(inp_emb, state)  # (b, h)

        # Attention for a single timestep
        q = self.dense_attn(h)  # (b, h)
        scores = tf.matmul(tf.expand_dims(q, axis=1), enc_out, transpose_b=True)  # (b,1,enc_len)
        weights = tf.nn.softmax(scores, axis=-1)
        context = tf.matmul(weights, enc_out)  # (b,1,h)
        context = tf.squeeze(context, axis=1)  # (b,h)

        fused = tf.concat([h, context], axis=-1)  # (b,2h)
        logits = self.dense(fused)  # (b,v_sz)
        out = tf.argmax(logits, axis=-1)
        return out, state
一 实验要求：
混合高斯模型问题描述：生成一组不带标签的聚类数据，使用高斯混合模型（Gaussian Mixture Models）进行无监督聚类。
数据集: 本次作业不提供数据，请自己生成数据。
题目要求：推荐使用python 及numpy 编写代码，不建议使用框架。
二 代码实现：
import math
from dataclasses import dataclass
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import multivariate_normal

def _logsumexp(a: np.ndarray, axis: int = -1, keepdims: bool = False) -> np.ndarray:
    # 数值稳定的 log(sum(exp(a)))计算。
    a_max = np.max(a, axis=axis, keepdims=True)
    out = a_max + np.log(np.sum(np.exp(a - a_max), axis=axis, keepdims=True))
    if keepdims:
        return out
    return np.squeeze(out, axis=axis)

def _log_gaussian(x: np.ndarray, mean: np.ndarray, cov: np.ndarray) -> np.ndarray:
    """计算形状为 (N, D) 的 x 的对数正态分布概率 Log N(x | mean, cov)。"""
    x = np.asarray(x)
    mean = np.asarray(mean)
    cov = np.asarray(cov)
    n, d = x.shape
    # 为了稳定性使用 Cholesky 分解；调用者应确保协方差矩阵是正定的 (PD)。
    L = np.linalg.cholesky(cov)
    diff = x - mean
    # 求解等式 L * y = diff^T => y^T = diff * L^{-T}
    # 使用 solve 求解比使用逆矩阵 (inv) 具有更好的数值稳定性。
    y = np.linalg.solve(L, diff.T)  # (D, N)
    maha = np.sum(y * y, axis=0)  # (N,)
    log_det = 2.0 * np.sum(np.log(np.diag(L)))
    return -0.5 * (d * math.log(2.0 * math.pi) + log_det + maha)

@dataclass
class GMMParams:
    weights: np.ndarray  # (K,)
    means: np.ndarray  # (K, D)
    covs: np.ndarray  # (K, D, D)

def fit_gmm_em(
    x: np.ndarray,
    n_components: int,
    *,
    max_iters: int = 200,
    tol: float = 1e-5,
    reg_covar: float = 1e-6,
    seed: int = 0,
) -> tuple[GMMParams, np.ndarray, list[float]]:
    """使用 EM 算法拟合全协方差的高斯混合模型。
    返回 (模型参数, 责任矩阵, 对数似然历史记录)。
    """
    x = np.asarray(x, dtype=np.float64)
    if x.ndim != 2:
        raise ValueError(f"x must be 2D (N, D), got shape {x.shape}")
    n, d = x.shape
    k = int(n_components)
    if k <= 0:
        raise ValueError("n_components must be positive")
    if n < k:
        raise ValueError("Need at least as many samples as components")
    rng = np.random.default_rng(seed)
    # 从随机样本中初始化均值。
    means = x[rng.choice(n, size=k, replace=False)].copy()
    # 将协方差初始化为全局协方差。
    centered = x - np.mean(x, axis=0, keepdims=True)
    cov_global = (centered.T @ centered) / max(n - 1, 1)
    cov_global = cov_global + reg_covar * np.eye(d)
    covs = np.repeat(cov_global[None, :, :], k, axis=0)
    weights = np.full((k,), 1.0 / k, dtype=np.float64)
    ll_hist: list[float] = []
    resp = np.empty((n, k), dtype=np.float64)
    for it in range(max_iters):
        # E步 (期望步)：计算责任矩阵。
        log_prob = np.empty((n, k), dtype=np.float64)
        for j in range(k):
            # 为权重添加一个极小的下界，以防止在某个簇退化时出现 log(0)。
            log_prob[:, j] = math.log(max(weights[j], 1e-300)) + _log_gaussian(x, means[j], covs[j])
        log_norm = _logsumexp(log_prob, axis=1, keepdims=True)  # (N, 1)
        resp[:] = np.exp(log_prob - log_norm)
        ll = float(np.sum(log_norm))
        ll_hist.append(ll)
        if it > 0 and abs(ll_hist[-1] - ll_hist[-2]) < tol:
            break
        # M步 (最大化步)：更新 权重/均值/协方差矩阵。
        nk = np.sum(resp, axis=0)  # (K,)
        # 如果某个簇的责任几乎为0，则将其重新初始化为随机点。
        dead = nk < 1e-8
        if np.any(dead):
            for j in np.where(dead)[0]:
                means[j] = x[rng.integers(0, n)]
                covs[j] = cov_global
                nk[j] = 1.0
            # 重新归一化责任矩阵以保证数值合理性。
            resp /= np.sum(resp, axis=1, keepdims=True)
            nk = np.sum(resp, axis=0)
        weights = nk / n
        means = (resp.T @ x) / nk[:, None]
        covs_new = np.empty((k, d, d), dtype=np.float64)
        for j in range(k):
            diff = x - means[j]
            cov_j = (resp[:, j][:, None] * diff).T @ diff
            cov_j = cov_j / nk[j]
            cov_j = cov_j + reg_covar * np.eye(d)
            covs_new[j] = cov_j
        covs = covs_new
    params = GMMParams(weights=weights, means=means, covs=covs)
    return params, resp, ll_hist

def predict(params: GMMParams, x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, dtype=np.float64)
    n, _ = x.shape
    k = params.weights.shape[0]
    log_prob = np.empty((n, k), dtype=np.float64)
    for j in range(k):
        log_prob[:, j] = math.log(max(float(params.weights[j]), 1e-300)) + _log_gaussian(
            x, params.means[j], params.covs[j]
        )
    return np.argmax(log_prob, axis=1)

def make_synthetic_data(*, n: int = 900, seed: int = 0) -> tuple[np.ndarray, np.ndarray]:
    """生成无标签的二维混合数据集。
    返回 (x, y_true)，其中 y_true 仅用于结果校验。
    """
    rng = np.random.default_rng(seed)
    weights = np.array([0.35, 0.40, 0.25])
    means = np.array([
        [-2.5, 0.0],
        [2.5, 0.5],
        [0.0, 3.0],
    ])
    covs = np.array(
        [
            [[0.35, 0.10], [0.10, 0.55]],
            [[0.55, -0.15], [-0.15, 0.35]],
            [[0.30, 0.00], [0.00, 0.30]],
        ],
        dtype=np.float64,
    )
    k = len(weights)
    z = rng.choice(k, size=n, p=weights)
    x = np.empty((n, 2), dtype=np.float64)
    for j in range(k):
        idx = np.where(z == j)[0]
        if idx.size == 0:
            continue
        x[idx] = rng.multivariate_normal(mean=means[j], cov=covs[j], size=idx.size)
    return x, z


def plot_gmm(x: np.ndarray, y_pred: np.ndarray, params: GMMParams, save_path: str = 'gmm_clustering.png'):
    """绘制聚类结果散点图和高斯混合模型的椭圆等高线。"""
    plt.figure(figsize=(8, 6))

    # 绘制数据点
    colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
    k = params.weights.shape[0]
    for j in range(k):
        idx = (y_pred == j)
        plt.scatter(x[idx, 0], x[idx, 1], s=10, c=colors[j % len(colors)], label=f'Cluster {j}', alpha=0.6)
        plt.scatter(params.means[j, 0], params.means[j, 1], marker='X', s=150, c='black', edgecolors='white', zorder=10)
    # 绘制等高线
    xmin, xmax = x[:, 0].min() - 1, x[:, 0].max() + 1
    ymin, ymax = x[:, 1].min() - 1, x[:, 1].max() + 1
    xx, yy = np.meshgrid(np.linspace(xmin, xmax, 100), np.linspace(ymin, ymax, 100))
    pos = np.dstack((xx, yy))

    for j in range(k):
        try:
            rv = multivariate_normal(params.means[j], params.covs[j])
            plt.contour(xx, yy, rv.pdf(pos), levels=3, colors='k', alpha=0.5, linewidths=1)
        except Exception as e:
            pass # 绘制等高线时忽略奇异矩阵
    plt.title('GMM Clustering Result')
    plt.xlabel('X1')
    plt.ylabel('X2')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.savefig(save_path, dpi=300)
    print(f"Visualization saved to {save_path}")
    plt.close()

if __name__ == '__main__':
    x, y_true = make_synthetic_data(n=1200, seed=42)
    params, resp, ll_hist = fit_gmm_em(x, n_components=3, seed=42)
    y_pred = predict(params, x)

    print("EM finished")
    print(f"iters: {len(ll_hist)}")
    print(f"final log-likelihood: {ll_hist[-1]:.3f}")
    print("weights:", np.round(params.weights, 4))
    print("means:\n", np.round(params.means, 4))
    # 无监督学习：y_true 仅供快速调试对比使用。
    agreement = float(np.mean(y_pred == y_true))
    print(f"naive label agreement (not permuted): {agreement:.3f}")
    # 绘制并保存图像
    plot_gmm(x, y_pred, params, save_path='...')

使用受限玻尔兹曼机（Restricted Boltzmann Machine, RBM），对MNIST 数据集建模。其中，每个像素点（值为0 或1）作为可观测变量，同时自定义一组隐变量（隐变量的个数为超参），完成以下任务：
1. 使用不带标签的MNIST 样本数据，训练RBM 参数。
2. 根据第1 步训练出的RBM，使用Gibbs 采样的方法，生成一组服从分布的样本。
MNIST数据集包括60000张训练图片和10000张测试图片。图片样本的数量已经足够训练一个很复杂的模型（例如 CNN的深层神经网络）。它经常被用来作为一个新 的模式识别模型的测试用例。而且它也是一个方便学生和研究者们执行用例的数据集。除此之外，MNIST数据集是一个相对较小的数据集，可以在你的笔记本CPUs上面直接执行
题目要求： 
- [ ] 请使用代码模板rbm.py，补全缺失部分，尽量不改动主体部分。
- [ ] 推荐使用python 及numpy 编写主要逻辑代码，适度使用框架。
二 实现函数：
class RBM:
    def __init__(self, n_hidden=2, n_observe=784):
        """
        初始化RBM模型参数
        
        参数:
            n_hidden: 隐藏层神经元数量
            n_observe: 可见层神经元数量（例如MNIST图像为784=28x28）
        """
        self.n_hidden = int(n_hidden)
        self.n_observe = int(n_observe)
        # 固定随机种子保证可复现性
        rng = np.random.default_rng(0)
        # 权重矩阵小随机初始化（有助于避免训练初期的饱和问题）
        self.W = (rng.normal(loc=0.0, scale=0.01, size=(self.n_observe, self.n_hidden))).astype(np.float32)
        # 可见层偏置
        self.b_v = np.zeros((self.n_observe,), dtype=np.float32)
        # 隐藏层偏置
        self.b_h = np.zeros((self.n_hidden,), dtype=np.float32)

        # 训练超参数（为简化示例保持固定）
        self.lr = 0.1          # 学习率
        self.batch_size = 100  # 批次大小
        self.n_epochs = 5      # 训练轮数
        self.cd_k = 1          # 对比散度（CD）的采样步数
        self.rng = rng

    @staticmethod
    def _sigmoid(x):
        """
        计算sigmoid激活函数值
        
        参数:
            x: 输入张量
        返回:
            sigmoid(x)，数值限制在[-30, 30]防止溢出
        """
        x = np.clip(x, -30.0, 30.0)  # 裁剪输入避免exp溢出
        return 1.0 / (1.0 + np.exp(-x))

    def _sample_bernoulli(self, p):
        """
        根据概率p从伯努利分布中采样0/1值
        
        参数:
            p: 采样概率张量（每个元素对应一个神经元的激活概率）
        返回:
            与p形状相同的0/1张量
        """
        return (self.rng.random(p.shape) < p).astype(np.float32)

    def train(self, data):
        """
        使用对比散度（CD-k）算法训练RBM模型
        参数:
            data: 训练数据，形状为(N, D)或(N, H, W)（会自动展平）
        返回:
            训练过程中每个epoch的重构误差历史
        """
        x = np.asarray(data)
        # 如果输入是图像格式(N, H, W)，展平为(N, D)
        if x.ndim == 3:
            x = x.reshape(x.shape[0], -1)
        # 数据形状校验
        if x.ndim != 2:
            raise ValueError(f"期望数据形状为 (N, D) 或 (N, H, W)，实际得到 {x.shape}")
        if x.shape[1] != self.n_observe:
            raise ValueError(f"期望可见层维度为 {self.n_observe}，实际得到 {x.shape[1]}")

        x = x.astype(np.float32)
        # 如果输入不是二值数据，通过阈值127.0进行二值化（适用于0-255的灰度图像）
        if x.max() > 1.0:
            x = (x > 127.0).astype(np.float32)

        n = x.shape[0]
        history = []
        for epoch in range(self.n_epochs):
            # 每个epoch随机打乱数据顺序
            perm = self.rng.permutation(n)
            x_shuf = x[perm]
            epoch_err = 0.0
            n_batches = 0
            # 分批次训练
            for start in range(0, n, self.batch_size):
                v0 = x_shuf[start : start + self.batch_size]
                if v0.size == 0:
                    continue
                bs = v0.shape[0]  # 当前批次实际大小
                # === 正相（Positive Phase）：从数据驱动的隐藏层采样 ===
                h0_prob = self._sigmoid(v0 @ self.W + self.b_h)  # 计算隐藏层激活概率
                h_state = self._sample_bernoulli(h0_prob)          # 采样隐藏层状态
                # === 负相（Negative Phase）：使用CD-k进行吉布斯采样 ===
                v_state = v0  # 初始可见层状态设为输入数据
                hk_prob = h0_prob
                for _ in range(self.cd_k):
                    # 从隐藏层重构可见层
                    v_prob = self._sigmoid(h_state @ self.W.T + self.b_v)
                    v_state = self._sample_bernoulli(v_prob)
                    # 从重构的可见层再次计算隐藏层
                    hk_prob = self._sigmoid(v_state @ self.W + self.b_h)
                    h_state = self._sample_bernoulli(hk_prob)
                # === 参数更新（基于对比散度的梯度上升） ===
                self.W += (self.lr / bs) * ((v0.T @ h0_prob) - (v_state.T @ hk_prob))
                self.b_v += (self.lr / bs) * np.sum(v0 - v_state, axis=0)
                self.b_h += (self.lr / bs) * np.sum(h0_prob - hk_prob, axis=0)
                # 记录重构误差（用于监控训练进度）
                epoch_err += float(np.mean((v0 - v_prob) ** 2))
                n_batches += 1
            # 计算并打印当前epoch的平均重构误差
            if n_batches:
                epoch_err /= n_batches
            print(f"epoch {epoch + 1}/{self.n_epochs}  recon_mse={epoch_err:.6f}")
            history.append(epoch_err)
        return history

    def sample(self):
        """
        从训练好的RBM模型中采样生成新样本
        返回:生成的样本。如果可见层维度是完全平方数，则返回(side, side)的图像格式；否则返回一维向量"""
        # 初始化可见层为随机概率0.5的伯努利分布
        v = self._sample_bernoulli(np.full((1, self.n_observe), 0.5, dtype=np.float32))
        h = np.zeros((1, self.n_hidden), dtype=np.float32)
        # 进行200步吉布斯采样（让马尔可夫链收敛）
        for _ in range(200):
            h_prob = self._sigmoid(v @ self.W + self.b_h)
            h = self._sample_bernoulli(h_prob)
            v_prob = self._sigmoid(h @ self.W.T + self.b_v)
            v = self._sample_bernoulli(v_prob)
        side = int(round(np.sqrt(self.n_observe)))
        if side * side == self.n_observe:
            return v.reshape(side, side)
        return v.reshape(-1)

一 实验要求：
黑白棋游戏，问题描述：本次作业要实现的是 利用强化学习等知识 玩atari 游戏中的 黑白棋游戏。具体任务是补全RL_QG_agent.py 文件.
配置环境安装办法：
1. pip install gym[all] # 安装 gym
2. 找到 安装的包的目录，然后复制 github 上面的reversi 文件夹， 到gym/envs/ 中
  （windows中的目录路径是
  C:\Program Files\Anaconda3\Lib\site-packages\gym\envs）
3. 在envs文件夹中 有__init__.py 文件，在文件 末尾，添加注册信息。
  （参考 github 上面 __init__.py 文件末尾的注册信息（即id='Reversi8x8-v0', 的注册信息））
Github 中reversi_main.py 是一个demo程序，主要为了规范后期判作业时候的接口.本作业后面会运行大家的程序，因此需要统一接口，并且注意保证自己的代码没有错误，可以运行。训练程序的时候 黑白双方可以自己规定，环境中没有对弈对象。因此训练程序的时候时自己设置对弈对象，比如与随机进行对弈，其次可以和一些搜索算法对弈。
参考文献：
1. Learning to Play Othello with Deep Neural Networks
2. Reinforcement Learning in the Game of Othello: Learning Against a Fixed Opponent and Learning from Self-Play
二 实现函数：
class RL_QG_agent:
    def __init__(self):
        # 模型保存目录，位于当前文件所在目录下的 "Reversi" 文件夹中
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reversi")
        os.makedirs(self.model_dir, exist_ok=True)
        self.rng = np.random.default_rng(0)
        self.model = None
        self.ckpt_manager = None
        if tf is not None:
            self.init_model()

    def init_model(self):
        # 定义一个小型策略/价值网络
        # 输入状态：(3, 8, 8) -> 输出 64 个棋盘位置的 logits
        self.model = tf.keras.Sequential(
            [
                tf.keras.layers.Input(shape=(3, 8, 8)),
                tf.keras.layers.Flatten(),
                tf.keras.layers.Dense(128, activation='relu'),
                tf.keras.layers.Dense(64, activation='relu'),
                tf.keras.layers.Dense(64),
            ]
        )
        # 用于保存/加载模型的检查点
        ckpt = tf.train.Checkpoint(model=self.model)
        self.ckpt_manager = tf.train.CheckpointManager(ckpt, self.model_dir, max_to_keep=1)

    def place(self, state, enables):
        # 该函数主要用于测试，返回的 action 是 0-63 之间的一个数值
        # action 表示要落子的位置
        # 只保留棋盘位置 (0..63)。环境可能单独处理 Pass/认输
        enables = [int(a) for a in enables if 0 <= int(a) < 64]
        # 健壮的默认行为：如果没有模型，则从合法动作中随机选择一个
        if not enables:
            # 调用方应处理 Pass 情况，这里返回一个无害的默认值
            return 0
        if self.model is None:
            return int(self.rng.choice(enables))
        s = np.asarray(state, dtype=np.float32)
        if s.shape != (3, 8, 8):
            # 允许形状为 (8,8,3) 或展平的变体
            s = s.reshape(3, 8, 8)
        logits = self.model(s[None, ...], training=False).numpy().reshape(-1)  # (64,)

        # 屏蔽非法动作，并在合法动作中选择最佳的一个
        mask = np.full((64,), -1e9, dtype=np.float32)
        mask[np.asarray(enables, dtype=np.int64)] = 0.0
        action = int(np.argmax(logits + mask))

        return action

    def save_model(self):  # 保存模型
        if self.ckpt_manager is None:
            return
        self.ckpt_manager.save()

    def load_model(self):  # 重新导入模型
        if self.ckpt_manager is None:
            return
        latest = self.ckpt_manager.latest_checkpoint
        if latest:
            # 使用 expect_partial 避免因缺少优化器状态而出现警告
self.ckpt_manager.checkpoint.restore(latest).expect_partial()使用受限玻尔兹曼机（Restricted Boltzmann Machine, RBM），对MNIST 数据集建模。其中，每个像素点（值为0 或1）作为可观测变量，同时自定义一组隐变量（隐变量的个数为超参），完成以下任务：
1. 使用不带标签的MNIST 样本数据，训练RBM 参数。
2. 根据第1 步训练出的RBM，使用Gibbs 采样的方法，生成一组服从分布的样本。
MNIST数据集包括60000张训练图片和10000张测试图片。图片样本的数量已经足够训练一个很复杂的模型（例如 CNN的深层神经网络）。它经常被用来作为一个新 的模式识别模型的测试用例。而且它也是一个方便学生和研究者们执行用例的数据集。除此之外，MNIST数据集是一个相对较小的数据集，可以在你的笔记本CPUs上面直接执行
题目要求： 
- [ ] 请使用代码模板rbm.py，补全缺失部分，尽量不改动主体部分。
- [ ] 推荐使用python 及numpy 编写主要逻辑代码，适度使用框架。
二 实现函数：
class RBM:
    def __init__(self, n_hidden=2, n_observe=784):
        """
        初始化RBM模型参数
        
        参数:
            n_hidden: 隐藏层神经元数量
            n_observe: 可见层神经元数量（例如MNIST图像为784=28x28）
        """
        self.n_hidden = int(n_hidden)
        self.n_observe = int(n_observe)
        # 固定随机种子保证可复现性
        rng = np.random.default_rng(0)
        # 权重矩阵小随机初始化（有助于避免训练初期的饱和问题）
        self.W = (rng.normal(loc=0.0, scale=0.01, size=(self.n_observe, self.n_hidden))).astype(np.float32)
        # 可见层偏置
        self.b_v = np.zeros((self.n_observe,), dtype=np.float32)
        # 隐藏层偏置
        self.b_h = np.zeros((self.n_hidden,), dtype=np.float32)

        # 训练超参数（为简化示例保持固定）
        self.lr = 0.1          # 学习率
        self.batch_size = 100  # 批次大小
        self.n_epochs = 5      # 训练轮数
        self.cd_k = 1          # 对比散度（CD）的采样步数
        self.rng = rng

    @staticmethod
    def _sigmoid(x):
        """
        计算sigmoid激活函数值
        
        参数:
            x: 输入张量
        返回:
            sigmoid(x)，数值限制在[-30, 30]防止溢出
        """
        x = np.clip(x, -30.0, 30.0)  # 裁剪输入避免exp溢出
        return 1.0 / (1.0 + np.exp(-x))

    def _sample_bernoulli(self, p):
        """
        根据概率p从伯努利分布中采样0/1值
        
        参数:
            p: 采样概率张量（每个元素对应一个神经元的激活概率）
        返回:
            与p形状相同的0/1张量
        """
        return (self.rng.random(p.shape) < p).astype(np.float32)

    def train(self, data):
        """
        使用对比散度（CD-k）算法训练RBM模型
        参数:
            data: 训练数据，形状为(N, D)或(N, H, W)（会自动展平）
        返回:
            训练过程中每个epoch的重构误差历史
        """
        x = np.asarray(data)
        # 如果输入是图像格式(N, H, W)，展平为(N, D)
        if x.ndim == 3:
            x = x.reshape(x.shape[0], -1)
        # 数据形状校验
        if x.ndim != 2:
            raise ValueError(f"期望数据形状为 (N, D) 或 (N, H, W)，实际得到 {x.shape}")
        if x.shape[1] != self.n_observe:
            raise ValueError(f"期望可见层维度为 {self.n_observe}，实际得到 {x.shape[1]}")

        x = x.astype(np.float32)
        # 如果输入不是二值数据，通过阈值127.0进行二值化（适用于0-255的灰度图像）
        if x.max() > 1.0:
            x = (x > 127.0).astype(np.float32)

        n = x.shape[0]
        history = []
        for epoch in range(self.n_epochs):
            # 每个epoch随机打乱数据顺序
            perm = self.rng.permutation(n)
            x_shuf = x[perm]
            epoch_err = 0.0
            n_batches = 0
            # 分批次训练
            for start in range(0, n, self.batch_size):
                v0 = x_shuf[start : start + self.batch_size]
                if v0.size == 0:
                    continue
                bs = v0.shape[0]  # 当前批次实际大小
                # === 正相（Positive Phase）：从数据驱动的隐藏层采样 ===
                h0_prob = self._sigmoid(v0 @ self.W + self.b_h)  # 计算隐藏层激活概率
                h_state = self._sample_bernoulli(h0_prob)          # 采样隐藏层状态
                # === 负相（Negative Phase）：使用CD-k进行吉布斯采样 ===
                v_state = v0  # 初始可见层状态设为输入数据
                hk_prob = h0_prob
                for _ in range(self.cd_k):
                    # 从隐藏层重构可见层
                    v_prob = self._sigmoid(h_state @ self.W.T + self.b_v)
                    v_state = self._sample_bernoulli(v_prob)
                    # 从重构的可见层再次计算隐藏层
                    hk_prob = self._sigmoid(v_state @ self.W + self.b_h)
                    h_state = self._sample_bernoulli(hk_prob)
                # === 参数更新（基于对比散度的梯度上升） ===
                self.W += (self.lr / bs) * ((v0.T @ h0_prob) - (v_state.T @ hk_prob))
                self.b_v += (self.lr / bs) * np.sum(v0 - v_state, axis=0)
                self.b_h += (self.lr / bs) * np.sum(h0_prob - hk_prob, axis=0)
                # 记录重构误差（用于监控训练进度）
                epoch_err += float(np.mean((v0 - v_prob) ** 2))
                n_batches += 1
            # 计算并打印当前epoch的平均重构误差
            if n_batches:
                epoch_err /= n_batches
            print(f"epoch {epoch + 1}/{self.n_epochs}  recon_mse={epoch_err:.6f}")
            history.append(epoch_err)
        return history

    def sample(self):
        """
        从训练好的RBM模型中采样生成新样本
        返回:生成的样本。如果可见层维度是完全平方数，则返回(side, side)的图像格式；否则返回一维向量"""
        # 初始化可见层为随机概率0.5的伯努利分布
        v = self._sample_bernoulli(np.full((1, self.n_observe), 0.5, dtype=np.float32))
        h = np.zeros((1, self.n_hidden), dtype=np.float32)
        # 进行200步吉布斯采样（让马尔可夫链收敛）
        for _ in range(200):
            h_prob = self._sigmoid(v @ self.W + self.b_h)
            h = self._sample_bernoulli(h_prob)
            v_prob = self._sigmoid(h @ self.W.T + self.b_v)
            v = self._sample_bernoulli(v_prob)
        side = int(round(np.sqrt(self.n_observe)))
        if side * side == self.n_observe:
            return v.reshape(side, side)
        return v.reshape(-1)



最核心的理解是：
Phi_poly_train = polynomial_basis(x_train, degree)Phi_gaussian_train = gaussian_basis(x_train, centers, sigma)
这两行是在构造不同的 设计矩阵 Φ\PhiΦ。
然后这两种优化方法：
w = least_squares_fit(Phi, y)
是直接用公式一次性算出参数。
w, loss = gradient_descent_fit(Phi, y)
是从零开始，一步一步迭代更新参数。
。
二 实现函数：
import numpy as np
import matplotlib.pyplot as plt

# =========================================================
# 0. 构造模拟数据
# =========================================================

def generate_data(n=30, noise_std=0.15, seed=42):
    """
    生成一组带噪声的一维数据
    真实函数：y = sin(2πx)
    """
    np.random.seed(seed)

    x = np.sort(np.random.rand(n))
    y_true = np.sin(2 * np.pi * x)

    noise = np.random.normal(0, noise_std, size=n)
    y = y_true + noise

    return x, y


# =========================================================
# 1. 多项式基函数
# =========================================================

def polynomial_basis(x, degree):
    """
    多项式基函数：

    phi(x) = [1, x, x^2, x^3, ..., x^degree]

    例如 degree = 3：
    y = w0 + w1*x + w2*x^2 + w3*x^3
    """
    x = np.asarray(x).reshape(-1)

    Phi = np.ones((len(x), degree + 1))

    for j in range(1, degree + 1):
        Phi[:, j] = x ** j

    return Phi


# =========================================================
# 2. 高斯基函数
# =========================================================

def gaussian_basis(x, centers, sigma):
    """
    高斯基函数：

    phi_j(x) = exp(-(x - c_j)^2 / (2*sigma^2))

    centers：高斯函数中心点
    sigma：控制高斯函数宽度

    最终形式：
    y = w0 + w1*g1(x) + w2*g2(x) + ... + wm*gm(x)
    """
    x = np.asarray(x).reshape(-1, 1)
    centers = np.asarray(centers).reshape(1, -1)

    Phi_gaussian = np.exp(-((x - centers) ** 2) / (2 * sigma ** 2))

    # 加上偏置项 w0
    Phi = np.hstack([
        np.ones((len(x), 1)),
        Phi_gaussian
    ])

    return Phi


# =========================================================
# 3. 最小二乘法闭式解
# =========================================================

def least_squares_fit(Phi, y, l2=1e-8):
    """
    最小二乘法优化：

    目标函数：
    L(w) = ||Phi*w - y||^2

    闭式解：
    w = (Phi^T Phi)^(-1) Phi^T y

    为了防止矩阵不可逆，这里加了一个很小的 L2 正则项。
    """
    n_features = Phi.shape[1]

    I = np.eye(n_features)

    # 不惩罚偏置项 w0
    I[0, 0] = 0

    w = np.linalg.solve(
        Phi.T @ Phi + l2 * I,
        Phi.T @ y
    )

    return w


# =========================================================
# 4. 梯度下降优化
# =========================================================

def gradient_descent_fit(Phi, y, lr=0.05, epochs=5000, l2=0.0):
    """
    梯度下降优化：

    目标函数：
    L(w) = 1/n * sum((y_pred - y)^2)

    预测：
    y_pred = Phi*w

    梯度：
    grad = 2/n * Phi^T(Phi*w - y)

    参数更新：
    w = w - lr * grad
    """
    n_samples, n_features = Phi.shape

    # 初始化参数
    w = np.zeros(n_features)

    loss_history = []

    for epoch in range(epochs):
        # 预测
        y_pred = Phi @ w

        # 误差
        error = y_pred - y

        # MSE 梯度
        grad = (2 / n_samples) * Phi.T @ error

        # L2 正则梯度
        reg_grad = 2 * l2 * w
        reg_grad[0] = 0

        grad = grad + reg_grad

        # 参数更新
        w = w - lr * grad

        # 记录损失
        loss = np.mean(error ** 2) + l2 * np.sum(w[1:] ** 2)
        loss_history.append(loss)

    return w, np.array(loss_history)


# =========================================================
# 5. 预测函数与误差函数
# =========================================================

def predict(Phi, w):
    return Phi @ w


def mse(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)


# =========================================================
# 6. 主程序：四种情况完整比较
# =========================================================

def main():
    # 生成训练数据
    x_train, y_train = generate_data(n=30, noise_std=0.15)

    # 测试点，用来画平滑曲线
    x_test = np.linspace(0, 1, 300)
    y_real = np.sin(2 * np.pi * x_test)

    # -----------------------------------------------------
    # 情况一：多项式基函数 + 最小二乘法
    # -----------------------------------------------------

    degree = 5

    Phi_poly_train = polynomial_basis(x_train, degree)
    Phi_poly_test = polynomial_basis(x_test, degree)

    w_poly_ls = least_squares_fit(Phi_poly_train, y_train)

    y_poly_ls = predict(Phi_poly_test, w_poly_ls)

    # -----------------------------------------------------
    # 情况二：高斯基函数 + 最小二乘法
    # -----------------------------------------------------

    centers = np.linspace(0, 1, 10)
    sigma = 0.1

    Phi_gaussian_train = gaussian_basis(x_train, centers, sigma)
    Phi_gaussian_test = gaussian_basis(x_test, centers, sigma)

    w_gaussian_ls = least_squares_fit(Phi_gaussian_train, y_train)

    y_gaussian_ls = predict(Phi_gaussian_test, w_gaussian_ls)

    # -----------------------------------------------------
    # 情况三：多项式基函数 + 梯度下降
    # -----------------------------------------------------

    w_poly_gd, loss_poly_gd = gradient_descent_fit(
        Phi_poly_train,
        y_train,
        lr=0.05,
        epochs=5000,
        l2=0.0
    )

    y_poly_gd = predict(Phi_poly_test, w_poly_gd)

    # -----------------------------------------------------
    # 情况四：高斯基函数 + 梯度下降
    # -----------------------------------------------------

    w_gaussian_gd, loss_gaussian_gd = gradient_descent_fit(
        Phi_gaussian_train,
        y_train,
        lr=0.05,
        epochs=5000,
        l2=0.0
    )

    y_gaussian_gd = predict(Phi_gaussian_test, w_gaussian_gd)

    # -----------------------------------------------------
    # 输出参数和误差
    # -----------------------------------------------------

    print("========== 训练结果 ==========")

    print("\n【多项式基函数 + 最小二乘法】")
    print("参数 w =", w_poly_ls)
    print("MSE =", mse(y_real, y_poly_ls))

    print("\n【高斯基函数 + 最小二乘法】")
    print("参数 w =", w_gaussian_ls)
    print("MSE =", mse(y_real, y_gaussian_ls))

    print("\n【多项式基函数 + 梯度下降】")
    print("参数 w =", w_poly_gd)
    print("MSE =", mse(y_real, y_poly_gd))

    print("\n【高斯基函数 + 梯度下降】")
    print("参数 w =", w_gaussian_gd)
    print("MSE =", mse(y_real, y_gaussian_gd))

    # -----------------------------------------------------
    # 画拟合曲线
    # -----------------------------------------------------

    plt.figure(figsize=(12, 8))

    plt.scatter(x_train, y_train, label="训练数据", color="black")
    plt.plot(x_test, y_real, label="真实函数", linewidth=2)

    plt.plot(x_test, y_poly_ls, label="多项式 + 最小二乘")
    plt.plot(x_test, y_gaussian_ls, label="高斯 + 最小二乘")
    plt.plot(x_test, y_poly_gd, label="多项式 + 梯度下降")
    plt.plot(x_test, y_gaussian_gd, label="高斯 + 梯度下降")

    plt.xlabel("x")
    plt.ylabel("y")
    plt.title("不同基函数与不同优化方法的线性回归拟合")
    plt.legend()
    plt.grid(True)
    plt.show()

    # -----------------------------------------------------
    # 画梯度下降损失下降过程
    # -----------------------------------------------------

    plt.figure(figsize=(10, 5))

    plt.plot(loss_poly_gd, label="多项式基函数 GD 损失")
    plt.plot(loss_gaussian_gd, label="高斯基函数 GD 损失")

    plt.xlabel("迭代次数")
    plt.ylabel("MSE 损失")
    plt.title("梯度下降损失变化")
    plt.legend()
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
