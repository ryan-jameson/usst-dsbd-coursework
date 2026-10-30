from __future__ import annotations

import html
import os
from pathlib import Path
from typing import Iterable

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parent
FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\NotoSansSC-VF.ttf"),
    Path(r"C:\Windows\Fonts\Deng.ttf"),
    Path(r"C:\Windows\Fonts\msyh.ttc"),
    Path(r"C:\Windows\Fonts\simsun.ttc"),
]
BOLD_FONT_CANDIDATES = [
    Path(r"C:\Windows\Fonts\Dengb.ttf"),
    Path(r"C:\Windows\Fonts\msyhbd.ttc"),
    Path(r"C:\Windows\Fonts\simhei.ttf"),
]


SOURCES = [
    "本地教材：教材nndl-book.pdf，邱锡鹏《神经网络与深度学习》，444 页。",
    "NNDL/PuGongYing 官网：https://nndl.ai/",
    "Goodfellow, Bengio, Courville, Deep Learning 官方目录：https://www.deeplearningbook.org/contents/TOC.html",
    "Deep Learning Book 优化章节：https://www.deeplearningbook.org/contents/optimization.html",
    "Deep Learning Book 自编码器章节：https://www.deeplearningbook.org/contents/autoencoders.html",
    "Deep Learning Book Monte Carlo 章节：https://www.deeplearningbook.org/contents/monte_carlo.html",
    "Dive into Deep Learning 在线教材：https://d2l.ai/",
    "D2L RNN/BPTT/LSTM：https://d2l.ai/chapter_recurrent-neural-networks/rnn.html",
    "CS231n 卷积网络笔记：https://cs231n.github.io/convolutional-networks/",
]


CHAPTERS = [
    {
        "title": "1 神经网络与深度学习概述、机器学习基础引言",
        "scope": [
            "机器学习的目标是从数据分布中学习映射、概率模型或表示，而不是只记住训练样本。",
            "深度学习的核心优势是多层非线性表示学习，可以把低层特征逐步组合为高层抽象。",
            "学习系统通常由数据、模型、学习准则、优化算法和评价指标组成。",
        ],
        "concepts": [
            "数据集 D={(x_i,y_i)}_{i=1}^m；训练集用于拟合参数，验证集用于选模型和早停，测试集只用于最终估计泛化能力。",
            "模型 f(x;theta) 表示带参数的函数族；深度网络把多个仿射变换和非线性激活复合起来。",
            "经验风险最小化用训练集平均损失近似真实风险；结构风险最小化在经验风险上加入复杂度惩罚。",
            "过拟合表现为训练误差低但验证/测试误差高；欠拟合表现为训练误差也高。",
            "最大似然估计、最大后验估计、交叉熵、偏差-方差分解是后续章节的共同数学底座。",
        ],
        "formulas": [
            "经验风险：R_emp(theta)=1/m * sum_{i=1}^m L(f(x_i;theta), y_i)。",
            "真实风险：R(theta)=E_{(x,y)~p_data}[L(f(x;theta),y)]。",
            "结构风险：J(theta)=R_emp(theta)+lambda * Omega(theta)。",
            "最大似然：theta_ML=argmax_theta sum_i log p_model(y_i|x_i;theta)。",
            "最大后验：theta_MAP=argmax_theta [sum_i log p_model(y_i|x_i;theta)+log p(theta)]。",
            "二分类交叉熵：L= - y log p - (1-y) log(1-p)，p=sigmoid(z)。",
            "Softmax：p_k=exp(z_k)/sum_j exp(z_j)，交叉熵 L=-sum_k y_k log p_k。",
            "偏差-方差：E[(hat f(x)-y)^2]=Bias^2+Variance+noise。",
            "准确率：Acc=(TP+TN)/(TP+TN+FP+FN)；F1=2PR/(P+R)。",
        ],
        "pitfalls": [
            "不要把训练集准确率当作泛化能力。",
            "验证集参与了模型选择，因此不能再作为最终测试集。",
            "深层模型能力强不等于一定泛化好，仍需正则化、数据规模和优化稳定性。",
        ],
        "checklist": [
            "能写出经验风险、交叉熵、MLE、MAP。",
            "能区分训练误差、验证误差、测试误差。",
            "能解释深度学习为什么需要表示学习、非线性和端到端训练。",
        ],
    },
    {
        "title": "2 深度前馈网络、XOR、梯度学习与反向传播",
        "scope": [
            "前馈网络是从输入到输出的有向无环计算图；XOR 是说明非线性隐藏层必要性的经典例子。",
            "训练前馈网络的主线是前向传播求预测和损失，反向传播用链式法则求梯度，优化器更新参数。",
            "隐藏单元、激活函数、深度和宽度共同决定表示能力与优化难度。",
        ],
        "concepts": [
            "单层线性模型不能表示 XOR，因为 XOR 的正负样本线性不可分。",
            "多层感知机 MLP 使用 h=phi(Wx+b)，y_hat=g(Vh+c) 表示非线性函数。",
            "Sigmoid/Tanh 容易饱和导致梯度消失；ReLU 计算简单但可能出现死亡 ReLU。",
            "反向传播不是新的学习准则，而是高效计算复合函数梯度的算法。",
            "自动微分把程序看成计算图，反向模式适合标量损失对大量参数求梯度。",
        ],
        "formulas": [
            "仿射层：a=W x+b；隐藏层：h=phi(a)。",
            "二层网络：f(x)=W_2 phi(W_1 x+b_1)+b_2。",
            "XOR 例：h_1=step(x_1+x_2-0.5)，h_2=step(x_1+x_2-1.5)，y=h_1-h_2。",
            "ReLU：phi(z)=max(0,z)；Sigmoid：sigma(z)=1/(1+exp(-z))。",
            "链式法则：dL/dx=(dL/dy)(dy/dx)。",
            "仿射层梯度：dL/dW=delta x^T，dL/db=delta，dL/dx=W^T delta。",
            "Softmax+CE：dL/dz_k=p_k-y_k。",
            "梯度下降：theta <- theta - eta * grad_theta J(theta)。",
            "数值梯度检查：grad_i ~= [J(theta+eps e_i)-J(theta-eps e_i)]/(2eps)。",
        ],
        "pitfalls": [
            "XOR 的重点不是阶跃函数本身，而是隐藏层产生可分表示。",
            "反向传播依赖计算图局部导数，不能把所有层的梯度都写成同一个矩阵乘法。",
            "激活函数选择会影响梯度流、初始化和学习率。",
        ],
        "checklist": [
            "能手算二层网络的前向传播。",
            "能写出 affine、ReLU、softmax-cross-entropy 的梯度。",
            "能解释数值微分、符号微分和自动微分的区别。",
        ],
    },
    {
        "title": "3 深度学习中的正则化",
        "scope": [
            "正则化的目标是降低泛化误差，而不只是降低训练误差。",
            "常见正则化可以作用在参数、数据、噪声、模型结构、训练过程和任务关系上。",
            "Dropout、数据增强和对抗训练是深度学习中最常见的实用正则化方法。",
        ],
        "concepts": [
            "L2 惩罚倾向于小权重，L1 惩罚倾向于稀疏权重。",
            "范数惩罚可理解为无约束惩罚，也可转化为约束优化。",
            "数据增强通过保持标签不变的变换扩大训练分布。",
            "噪声注入可以作用在输入、隐藏层、权重或标签上，训练模型对扰动更平滑。",
            "多任务学习通过共享表示在相关任务之间传递统计强度。",
            "Dropout 训练时随机屏蔽单元，测试时使用期望缩放或 inverted dropout。",
            "对抗训练用最坏方向的小扰动提升局部鲁棒性。",
        ],
        "formulas": [
            "L2 正则：J_tilde(theta)=J(theta)+lambda/2 * ||w||_2^2。",
            "L2 更新：w <- (1-eta lambda)w - eta * grad_w J。",
            "L1 正则：J_tilde(theta)=J(theta)+lambda ||w||_1。",
            "约束形式：min J(theta) s.t. ||w||_2 <= c。",
            "多任务目标：J=sum_t alpha_t J_t(theta_shared,theta_t)。",
            "Dropout：m_j~Bernoulli(p)，h_tilde=m*h/p，E[h_tilde]=h。",
            "对抗训练：min_theta E[max_{||r||<=epsilon} L(f(x+r;theta),y)]。",
            "FGSM：r_adv=epsilon * sign(grad_x L(f(x;theta),y))。",
            "标签平滑：y'_k=(1-epsilon)y_k+epsilon/K。",
        ],
        "pitfalls": [
            "正则化强度过大也会欠拟合。",
            "Dropout 与 BatchNorm 同用时需要注意训练/测试统计差异。",
            "数据增强必须保持标签语义不变，不能随意变换。",
        ],
        "checklist": [
            "能从目标函数写出 L2 的权重衰减更新。",
            "能解释 Dropout 的训练/测试差异。",
            "能说明对抗训练和普通噪声增强的区别。",
        ],
    },
    {
        "title": "4 深度模型训练中的优化",
        "scope": [
            "深度学习优化的目标是找到泛化好的参数，而不是严格求某个固定函数的全局最小值。",
            "非凸、高维、病态曲率、鞍点、梯度消失/爆炸、随机梯度噪声是神经网络优化的核心挑战。",
            "初始化、学习率、批量大小、动量、自适应学习率和归一化会显著影响训练。",
        ],
        "concepts": [
            "训练通常优化训练集 surrogate loss，但真正关心测试集性能。",
            "小批量 SGD 用随机样本估计全梯度，计算快但有噪声。",
            "动量把过去梯度做指数平均，加速一致方向并抑制震荡。",
            "AdaGrad 适合稀疏特征但学习率会持续衰减；RMSProp 用滑动平均缓解该问题。",
            "Adam 结合一阶矩和二阶矩估计，并做偏差校正。",
            "Xavier/He 初始化通过保持前向或反向方差稳定减轻梯度消失/爆炸。",
            "二阶方法利用 Hessian 曲率信息，但深度网络中存储和求逆代价高。",
        ],
        "formulas": [
            "小批量梯度：g=1/B * sum_{i in B} grad_theta L_i(theta)。",
            "SGD：theta_{t+1}=theta_t-eta g_t。",
            "动量：v_t=mu v_{t-1}-eta g_t，theta_t=theta_{t-1}+v_t。",
            "Nesterov：先看 theta+mu v，再用该处梯度更新。",
            "AdaGrad：r_t=r_{t-1}+g_t*g_t，theta<-theta-eta g_t/(sqrt(r_t)+eps)。",
            "RMSProp：r_t=rho r_{t-1}+(1-rho)g_t*g_t。",
            "Adam：m_t=beta1 m_{t-1}+(1-beta1)g_t；v_t=beta2 v_{t-1}+(1-beta2)g_t^2。",
            "Adam 偏差校正：m_hat=m_t/(1-beta1^t)，v_hat=v_t/(1-beta2^t)。",
            "Xavier：Var(W)=2/(n_in+n_out)；He：Var(W)=2/n_in。",
            "Newton：theta<-theta-H^{-1}g；梯度裁剪：g<-g*min(1,tau/||g||)。",
        ],
        "pitfalls": [
            "训练损失下降快不代表测试性能最好。",
            "学习率过大可能发散，过小会训练极慢或卡在平台区。",
            "Adam 方便但不总是泛化最好，必要时可对比 SGD+momentum。",
        ],
        "checklist": [
            "能写出 SGD、Momentum、RMSProp、Adam 更新式。",
            "能根据激活函数选择 Xavier 或 He 初始化。",
            "能解释小批量大小对噪声、显存和收敛的影响。",
        ],
    },
    {
        "title": "5 卷积神经网络",
        "scope": [
            "卷积网络利用局部连接、权值共享和平移等变性处理具有网格结构的数据。",
            "卷积层、非线性、池化、归一化和全连接/全局池化共同构成典型 CNN。",
            "输出尺寸、参数量、感受野和反向传播是考试中最常见的计算点。",
        ],
        "concepts": [
            "深度学习框架中的卷积通常实现互相关，即不翻转卷积核。",
            "多通道卷积对所有输入通道求局部内积，再对输出通道堆叠。",
            "池化通过局部统计汇聚降低空间尺寸，提供一定局部平移不变性。",
            "空洞卷积扩大感受野，转置卷积常用于上采样，深度可分离卷积减少参数。",
            "结构化输出任务如语义分割需要输出空间结构，而不是一个类别。",
        ],
        "formulas": [
            "一维卷积：s(t)=sum_a x(a) w(t-a)。",
            "二维互相关：Y[i,j]=sum_u sum_v X[i+u,j+v] K[u,v]。",
            "输出尺寸：H_out=floor((H+2P-K)/S)+1，W_out=floor((W+2P-K)/S)+1。",
            "参数量：K_h*K_w*C_in*C_out + C_out。",
            "多通道：Y[:,:,c_o]=sum_{c_i} X[:,:,c_i] * K[:,:,c_i,c_o] + b_{c_o}。",
            "最大池化：Y[i,j,c]=max_{(u,v) in window} X[iS+u,jS+v,c]。",
            "空洞卷积有效核：K_eff=K+(K-1)(d-1)。",
            "转置卷积常用输出：H_out=(H_in-1)S-2P+K+output_padding。",
            "卷积层权重梯度：dL/dK = X 与 dL/dY 的相关累加。",
        ],
        "pitfalls": [
            "卷积输出尺寸必须是整数，否则 padding/stride 设置不匹配。",
            "池化不是严格全局平移不变，只是局部降低对位置的敏感性。",
            "1x1 卷积不是没用，它在通道维做线性组合。",
        ],
        "checklist": [
            "能手算卷积层输出尺寸和参数量。",
            "能解释局部连接、权值共享、平移等变性。",
            "能区分普通卷积、空洞卷积、转置卷积、深度可分离卷积。",
        ],
    },
    {
        "title": "6 循环神经网络与 LSTM",
        "scope": [
            "RNN 通过隐藏状态保存序列历史，适合文本、语音、时间序列等有顺序的数据。",
            "展开计算图把循环结构变成跨时间共享参数的深层前馈网络。",
            "BPTT、梯度消失/爆炸、门控记忆、双向和深层结构是本章重点。",
        ],
        "concepts": [
            "简单 RNN 的隐藏状态同时依赖当前输入和上一时刻隐藏状态。",
            "BPTT 沿时间反传梯度，长序列中反复乘 Jacobian 会导致梯度消失或爆炸。",
            "LSTM 用输入门、遗忘门、输出门和记忆单元控制信息流。",
            "GRU 合并部分门结构，参数更少。",
            "双向 RNN 同时利用过去和未来上下文，但不适合严格在线预测。",
            "递归神经网络在树或图结构上共享组合函数。",
        ],
        "formulas": [
            "RNN 隐状态：h_t=phi(W_xh x_t + W_hh h_{t-1}+b_h)。",
            "RNN 输出：o_t=W_hy h_t+b_y，p_t=softmax(o_t)。",
            "序列损失：L=sum_t L_t(p_t,y_t)。",
            "梯度核心：d h_t / d h_k 包含 prod_{i=k+1}^t W_hh^T diag(phi'(a_i))。",
            "LSTM 输入门：i_t=sigma(W_xi x_t+W_hi h_{t-1}+b_i)。",
            "LSTM 遗忘门：f_t=sigma(W_xf x_t+W_hf h_{t-1}+b_f)。",
            "LSTM 候选：g_t=tanh(W_xg x_t+W_hg h_{t-1}+b_g)。",
            "LSTM 记忆：c_t=f_t*c_{t-1}+i_t*g_t。",
            "LSTM 输出门与隐藏态：o_t=sigma(...), h_t=o_t*tanh(c_t)。",
            "梯度裁剪：g<-g*min(1,tau/||g||)。",
        ],
        "pitfalls": [
            "RNN 的深度既包括层数，也包括时间展开长度。",
            "LSTM 缓解但不能完全消除长依赖学习困难。",
            "训练时 teacher forcing 和推理时自回归会产生暴露偏差。",
        ],
        "checklist": [
            "能画出展开计算图并说明参数共享。",
            "能写出 LSTM 四组核心公式。",
            "能解释双向 RNN、深层 RNN、递归 NN 的差别。",
        ],
    },
    {
        "title": "7 概率 PCA、因子分析、稀疏编码与自编码器",
        "scope": [
            "线性因子模型用少量潜变量解释高维观测，自编码器用编码器和解码器学习表示。",
            "PCA、PPCA、因子分析、稀疏编码和自编码器都可看作表示学习方法。",
            "欠完备、稀疏、去噪、收缩等约束用于避免自编码器学习无意义恒等映射。",
        ],
        "concepts": [
            "PCA 寻找最大方差方向，也等价于最小化线性重构误差。",
            "PPCA 令 x=Wz+mu+epsilon，用各向同性高斯噪声建立概率模型。",
            "因子分析允许观测维度有不同噪声方差。",
            "稀疏编码同时学习字典和稀疏系数。",
            "欠完备自编码器在编码维度小于输入维度时被迫保留主要信息。",
            "正则自编码器通过对编码、噪声鲁棒性或 Jacobian 施加约束学习有用表示。",
        ],
        "formulas": [
            "PCA 投影：z=W^T(x-mu)，重构：x_hat=Wz+mu。",
            "PCA 目标：min_W sum_i ||x_i-WW^T x_i||_2^2, s.t. W^T W=I。",
            "PPCA：z~N(0,I)，x|z~N(Wz+mu, sigma^2 I)。",
            "PPCA 边缘：x~N(mu, W W^T + sigma^2 I)。",
            "因子分析：x|z~N(Wz+mu, Psi)，Psi 为对角噪声协方差。",
            "稀疏编码：min_{D,a} ||x-Da||_2^2 + lambda ||a||_1。",
            "自编码器：h=f(x)，r=g(h)，L(x,r)=||x-r||^2 或交叉熵。",
            "稀疏 AE：L(x,g(f(x))) + lambda Omega(h)。",
            "去噪 AE：min E_{q(x_tilde|x)} ||x-g(f(x_tilde))||^2。",
            "收缩 AE：L + lambda ||J_f(x)||_F^2。",
        ],
        "pitfalls": [
            "编码维度小不自动保证表示有用，解码器容量也会影响结果。",
            "线性欠完备 AE 与 PCA 相关，但非线性 AE 可学更复杂流形。",
            "稀疏编码的稀疏性约束在编码变量上，不一定等同于稀疏权重。",
        ],
        "checklist": [
            "能写出 PPCA 和因子分析的生成过程。",
            "能解释稀疏编码和自编码器目标的区别。",
            "能比较欠完备、去噪、稀疏、收缩自编码器。",
        ],
    },
    {
        "title": "8 预训练、迁移学习、领域自适应与结构化概率模型",
        "scope": [
            "贪心逐层无监督预训练曾用于缓解深层网络优化和标注不足问题。",
            "迁移学习和领域自适应关注源域知识如何迁移到目标域。",
            "结构化概率模型用图表达变量依赖，深度学习可用于学习表示、势函数或近似推断。",
        ],
        "concepts": [
            "逐层预训练先无监督训练每一层，再以监督目标微调整个网络。",
            "迁移学习常见策略是固定特征提取器、部分微调或全量微调。",
            "领域自适应处理 p_s(x,y) 与 p_t(x,y) 不同的问题，常见情形是协变量偏移。",
            "分布式表示用多个维度组合表达概念，可带来组合泛化。",
            "图模型把联合分布分解为局部因子，降低建模复杂度。",
            "有向图适合生成过程描述，无向图适合对称依赖和能量函数。",
            "结构化概率模型中的精确推断常不可行，需要采样、变分或神经近似推断。",
        ],
        "formulas": [
            "预训练加微调：theta_0 <- unsupervised pretrain；theta* <- supervised finetune(theta_0)。",
            "迁移目标：min_theta E_{(x,y)~D_t} L(f(x;theta),y)，theta 初始化或约束来自源域。",
            "协变量偏移风险：R_t(f)=E_{p_s(x,y)} [p_t(x)/p_s(x) * L(f(x),y)]。",
            "MMD 思想：dist(P,Q)=||E_P phi(x)-E_Q phi(x)||_H。",
            "有向图分解：p(x_1,...,x_n)=prod_i p(x_i | Pa_i)。",
            "无向图分解：p(x)=1/Z prod_c psi_c(x_c)=exp(-E(x))/Z。",
            "条件独立：x_A independent x_B | x_C 可由图分离关系读出。",
            "深度结构化模型：psi_c(x_c;theta) 或 q(z|x;phi) 可由神经网络参数化。",
        ],
        "pitfalls": [
            "源域性能好不代表目标域性能好，负迁移可能发生。",
            "领域自适应需要说明分布差异类型，不能只说数据不同。",
            "图模型结构是建模假设，错误结构会限制可表达依赖。",
        ],
        "checklist": [
            "能说清预训练和微调的流程。",
            "能区分迁移学习、领域自适应、半监督学习。",
            "能写出有向图和无向图的联合分布分解。",
        ],
    },
    {
        "title": "9 采样、蒙特卡洛、MCMC、EM 与变分推断",
        "scope": [
            "当积分、求和或后验推断不可精确计算时，采样和近似推断提供可行方案。",
            "Monte Carlo 用样本均值近似期望；MCMC 构造以目标分布为平稳分布的马尔科夫链。",
            "EM 和变分推断把含潜变量的学习问题转化为可迭代优化的下界问题。",
        ],
        "concepts": [
            "Monte Carlo 估计在独立同分布采样下无偏且方差随样本数按 1/n 缩小。",
            "重要性采样从易采样分布 q 采样，再用 p/q 加权。",
            "Metropolis-Hastings 用接受率保证目标分布不变。",
            "Gibbs 采样逐个变量从完整条件分布采样。",
            "EM 交替进行 E 步估计潜变量后验期望和 M 步最大化期望完全数据对数似然。",
            "变分推断用简单分布 q(z) 近似真实后验 p(z|x)，最大化 ELBO。",
        ],
        "formulas": [
            "MC 估计：s=E_p[f(x)]，s_hat=1/n sum_i f(x_i)，x_i~p。",
            "方差：Var(s_hat)=Var(f(x))/n。",
            "重要性采样：E_p[f(x)]=E_q[f(x)p(x)/q(x)]。",
            "MH 接受率：alpha=min(1, p(x')q(x|x')/[p(x)q(x'|x)])。",
            "Gibbs：x_j^{t+1} ~ p(x_j | x_{-j}^{t})。",
            "EM 辅助函数：Q(theta,theta_old)=E_{z|x,theta_old}[log p(x,z;theta)]。",
            "ELBO：log p(x) >= E_q[log p(x,z)] - E_q[log q(z)]。",
            "KL 关系：log p(x)=ELBO(q)+KL(q(z)||p(z|x))。",
            "平均场：q(z)=prod_j q_j(z_j)。",
        ],
        "pitfalls": [
            "MCMC 样本相关，不能简单当成完全独立样本。",
            "重要性采样如果 q 覆盖不了 p 的高概率区域，方差会很大。",
            "ELBO 最大化等价于让 q 接近后验，但接近方向是 KL(q||p)。",
        ],
        "checklist": [
            "能推导 MC 估计无偏性和方差。",
            "能写出 MH、Gibbs、EM、ELBO 的核心公式。",
            "能解释采样近似和变分近似的优缺点。",
        ],
    },
    {
        "title": "10 玻尔兹曼机、RBM、DBN、DBM 与生成模型评估",
        "scope": [
            "玻尔兹曼机是基于能量函数的无向生成模型，概率由能量和配分函数定义。",
            "RBM 限制层内无连接，使可见层和隐藏层条件独立，从而能用 Gibbs 采样训练。",
            "深度信念网络和深度玻尔兹曼机把多个潜变量层组合起来表达复杂分布。",
        ],
        "concepts": [
            "能量越低的状态概率越高，配分函数负责归一化但通常难以精确计算。",
            "RBM 的二部图结构让 p(h|v) 和 p(v|h) 分解成独立 Bernoulli 条件。",
            "对比散度用短链 Gibbs 近似最大似然梯度中的模型期望。",
            "DBN 顶层通常是无向 RBM，低层是有向生成连接。",
            "DBM 多层都是无向连接，推断和训练更困难，常需均值场和 MCMC。",
            "生成模型评估可看似然、样本质量、覆盖性、下游任务和人为检查，但每种指标都有盲点。",
        ],
        "formulas": [
            "BM 概率：p(x)=exp(-E(x))/Z，Z=sum_x exp(-E(x))。",
            "BM 能量：E(s)= - sum_{i<j} w_ij s_i s_j - sum_i b_i s_i。",
            "RBM 能量：E(v,h)= -b^T v - c^T h - v^T W h。",
            "RBM 条件：p(h_j=1|v)=sigma(c_j+W_:j^T v)。",
            "RBM 条件：p(v_i=1|h)=sigma(b_i+W_i: h)。",
            "似然梯度：d log p(v)/dW = E_{p(h|v)}[v h^T] - E_{p(v,h)}[v h^T]。",
            "CD-k 更新近似：Delta W ∝ v_data h_data^T - v_k h_k^T。",
            "自由能：F(v)= -b^T v - sum_j log(1+exp(c_j+W_:j^T v))。",
            "AIS/重要性采样可用于估计难以直接计算的配分函数。",
        ],
        "pitfalls": [
            "RBM 的条件分布容易算，不代表边缘似然容易算。",
            "CD-k 是近似梯度，k 太小会有偏差。",
            "生成样本清晰不等于覆盖真实分布，评估要兼顾质量和多样性。",
        ],
        "checklist": [
            "能写出 BM/RBM 能量、概率和条件分布。",
            "能解释配分函数为什么困难。",
            "能比较 RBM、DBN、DBM 和有向生成模型。",
        ],
    },
]


QUESTIONS = [
    [
        "给定训练集 D={(x_i,y_i)}_{i=1}^m，写出经验风险、真实风险和结构风险，并说明三者的关系。",
        "设回归模型 y=f(x;theta)+epsilon，epsilon~N(0,sigma^2)。证明最大似然估计等价于最小化平方误差。",
        "二分类中 p=sigmoid(z)，损失 L=-y log p-(1-y)log(1-p)。求 dL/dz。",
        "说明训练集、验证集、测试集各自用途，并解释为什么不能用测试集调参。",
        "用偏差-方差分解解释过拟合和欠拟合。",
        "给定混淆矩阵 TP=40，FP=10，FN=20，TN=30，计算 precision、recall、F1 和 accuracy。",
        "解释局部表示和分布式表示的区别，并给出深度学习中分布式表示的优势。",
        "什么是归纳偏置？为什么没有归纳偏置就不能有效泛化？",
        "比较 MLE 和 MAP，并说明 L2 正则与高斯先验的关系。",
        "列出深度学习相对传统机器学习的三个挑战，并说明每个挑战对应的处理策略。",
    ],
    [
        "证明 XOR 不能被单个线性分类器分开，并构造一个两隐藏单元的 XOR 网络。",
        "给定 x in R^4，隐藏层 8 个 ReLU 单元，输出层 3 类 softmax，计算参数总数。",
        "写出二层 MLP 的前向传播公式，并说明每一层的张量形状。",
        "推导 softmax 加交叉熵对 logits 的梯度 dL/dz_k。",
        "对 affine 层 a=Wx+b，已知上游梯度 delta=dL/da，求 dL/dW、dL/db、dL/dx。",
        "说明 Sigmoid、Tanh、ReLU、Leaky ReLU 的优缺点。",
        "什么是反向传播？它与梯度下降是什么关系？",
        "给出中心差分数值梯度公式，并说明梯度检查为什么不能替代反向传播训练。",
        "解释通用近似定理的含义和局限。",
        "给定 mini-batch 大小 B，写出小批量梯度估计，并说明它为什么是全梯度的无偏估计。",
    ],
    [
        "写出带 L2 正则的目标函数，并推导普通 SGD 下的权重更新式。",
        "比较 L1 和 L2 正则对参数的影响，为什么 L1 更容易产生稀疏解？",
        "说明范数惩罚和约束优化之间的等价思想。",
        "给出三个图像任务中的数据增强例子，并说明哪些增强可能破坏标签。",
        "解释向输入加入小高斯噪声为什么可能提升鲁棒性。",
        "推导 inverted dropout 中 h_tilde=m*h/p 的期望。",
        "什么是早停？为什么它可以看作正则化？",
        "写出多任务学习目标函数，并说明共享层和任务特定层的作用。",
        "写出 FGSM 对抗样本公式，并说明对抗训练的 min-max 结构。",
        "比较 Dropout、Bagging 和模型集成的联系与差别。",
    ],
    [
        "说明学习问题中的优化和纯优化的区别。",
        "写出 SGD、Momentum、Nesterov Momentum 的更新思想。",
        "比较 AdaGrad、RMSProp、Adam 的二阶矩处理方式。",
        "推导 Adam 的偏差校正项为什么需要除以 1-beta^t。",
        "给定 n_in=100，n_out=50，写出 Xavier 初始化和 He 初始化的权重方差。",
        "什么是病态曲率？为什么它会让梯度下降震荡或进展缓慢？",
        "解释鞍点和局部极小值在高维非凸优化中的差异。",
        "写出梯度裁剪公式，并说明它在 RNN 中为什么常用。",
        "比较大 batch 和小 batch 的训练优缺点。",
        "写出 Newton 更新，并说明深度学习中很少直接使用精确 Newton 的原因。",
    ],
    [
        "给定输入 32x32x3，卷积核 5x5，输出通道 16，stride=1，padding=2，求输出尺寸和参数量。",
        "给定输入 28x28，卷积核 3x3，stride=2，padding=1，求输出高宽。",
        "写出二维互相关的公式，并说明它与数学卷积的差别。",
        "说明局部连接和权值共享如何减少参数量。",
        "给出 max pooling 的公式，并说明它对空间分辨率和不变性的影响。",
        "推导卷积层对卷积核参数的梯度含义。",
        "空洞卷积 dilation=2，核大小 3，有效感受野是多少？",
        "写出转置卷积输出尺寸公式，并说明它常用于什么任务。",
        "比较普通卷积和深度可分离卷积的参数量。",
        "解释结构化输出任务为什么常用全卷积网络。",
    ],
    [
        "写出简单 RNN 的隐藏状态和输出公式。",
        "说明展开计算图中参数共享的含义。",
        "用梯度连乘解释 RNN 的梯度消失和梯度爆炸。",
        "写出 LSTM 的输入门、遗忘门、候选记忆、记忆单元和输出门公式。",
        "比较 LSTM 和 GRU 的结构差异。",
        "什么是双向 RNN？它适合和不适合哪些场景？",
        "什么是深层 RNN？它与普通 RNN 的时间展开深度有何区别？",
        "解释递归神经网络和循环神经网络的差别。",
        "什么是 teacher forcing？它可能带来什么推理阶段问题？",
        "说明截断 BPTT 的目的、做法和代价。",
    ],
    [
        "写出 PCA 的重构误差最小化目标，并说明它与最大方差方向的关系。",
        "写出 PPCA 的生成模型和边缘分布。",
        "比较 PPCA 和因子分析的噪声协方差假设。",
        "写出稀疏编码的优化目标，并解释字典和编码变量的作用。",
        "为什么线性欠完备自编码器与 PCA 有联系？",
        "写出普通自编码器的编码、解码和重构损失。",
        "说明稀疏自编码器如何避免恒等映射。",
        "写出去噪自编码器的训练目标，并说明它学到什么鲁棒性。",
        "写出收缩自编码器的 Jacobian 惩罚项，并解释其意义。",
        "比较稀疏编码、自编码器和预测稀疏分解。",
    ],
    [
        "描述贪心逐层无监督预训练的完整流程。",
        "为什么无监督预训练曾经重要？现代深度学习中它的重要性为什么下降？",
        "比较特征提取式迁移、部分微调和全量微调。",
        "写出协变量偏移下的加权风险公式。",
        "什么是负迁移？如何在实验中发现它？",
        "解释半监督学习、迁移学习、领域自适应三者的区别。",
        "什么是分布式表示？为什么它可能带来组合泛化能力？",
        "写出有向图模型的联合分布分解。",
        "写出无向图模型的能量形式，并解释配分函数。",
        "说明深度学习如何用于结构化概率模型的表示、推断或势函数学习。",
    ],
    [
        "证明 Monte Carlo 样本均值估计 E_p[f(x)] 是无偏估计。",
        "推导 Monte Carlo 估计方差随样本数 n 的变化。",
        "写出重要性采样公式，并说明选择 q(x) 的原则。",
        "写出 Metropolis-Hastings 接受率公式。",
        "解释 Gibbs 采样为什么是 MCMC 的特例。",
        "什么是混合慢？它对样本估计有什么影响？",
        "写出 EM 的 E 步和 M 步。",
        "推导 ELBO 与 KL(q(z)||p(z|x)) 的关系。",
        "写出平均场变分分布的形式，并说明它的优缺点。",
        "比较采样近似、EM 和变分推断的适用场景。",
    ],
    [
        "写出玻尔兹曼机的能量函数、概率分布和配分函数。",
        "为什么配分函数 Z 会让最大似然训练困难？",
        "写出 RBM 的能量函数以及 p(h_j=1|v)、p(v_i=1|h)。",
        "推导 RBM 对数似然关于 W 的梯度由数据期望和模型期望组成。",
        "说明 Contrastive Divergence k 的算法步骤。",
        "比较 RBM、DBN、DBM 的结构差异。",
        "如何把 RBM 扩展到实值可见变量？",
        "卷积玻尔兹曼机为什么适合图像数据？",
        "比较有向生成网络和无向能量模型的训练难点。",
        "生成模型评估应考虑哪些指标？为什么单一指标不充分？",
    ],
]


ANSWERS = [
    [
        "经验风险是 R_emp(theta)=1/m sum_i L(f(x_i;theta),y_i)，真实风险是 R(theta)=E_{p_data}L(f(x;theta),y)，结构风险是 R_emp(theta)+lambda Omega(theta)。训练时只能直接看到经验风险，目标是通过合适模型和正则化降低真实风险。",
        "高斯噪声下 p(y_i|x_i;theta)=1/(sqrt(2pi)sigma) exp(-(y_i-f_i)^2/(2sigma^2))。对数似然等于常数 -1/(2sigma^2)sum_i(y_i-f_i)^2，最大化它等价于最小化平方误差。",
        "p=sigma(z)，dp/dz=p(1-p)。dL/dp= -y/p+(1-y)/(1-p)，相乘得 dL/dz=p-y。这也是 logistic 回归最常用的梯度形式。",
        "训练集拟合参数，验证集选择超参数、早停和模型结构，测试集估计最终泛化性能。若用测试集调参，测试集信息已经泄漏到模型选择中，最终误差会偏乐观。",
        "欠拟合通常偏差大，模型表达能力不足或训练不充分；过拟合通常方差大，对训练样本扰动敏感。正则化、更多数据、数据增强和早停可降低方差，提高模型容量或训练质量可降低偏差。",
        "Precision=TP/(TP+FP)=40/50=0.80；Recall=TP/(TP+FN)=40/60=0.667；F1=2PR/(P+R)=0.727；Accuracy=(TP+TN)/100=0.70。",
        "局部表示常用一个维度或符号表示一个概念，分布式表示用多个维度的组合表示概念。分布式表示能以较少维度表达大量组合，并让相似样本在表示空间中接近。",
        "归纳偏置是学习算法偏好的函数类别或解释方式。没有归纳偏置，任何未见样本标签都同样可能，算法无法从有限数据推出对新样本的可靠判断。",
        "MLE 最大化数据似然，MAP 最大化似然乘先验。若先验 p(w)∝exp(-lambda ||w||_2^2/2)，则负对数后验等于负对数似然加 L2 惩罚。",
        "挑战包括高维非凸优化、过拟合和可解释/可控性不足。对应策略包括良好初始化和优化器、正则化和数据增强、可视化/消融/不确定性评估。",
    ],
    [
        "XOR 的正样本 (1,0),(0,1) 和负样本 (0,0),(1,1) 无法由一条直线分开。可用 h1=step(x1+x2-0.5)，h2=step(x1+x2-1.5)，y=h1-h2；仅当两个输入中恰有一个为 1 时输出 1。",
        "隐藏层参数为 4*8+8=40；输出层参数为 8*3+3=27；总参数 67。",
        "设批量输入 X 为 Bx4，W1 为 4xH，b1 为 H，H=phi(XW1+b1)，W2 为 Hx3，Z=HW2+b2，Y_hat=softmax(Z)。每行对应一个样本。",
        "p_k=exp(z_k)/sum_j exp(z_j)，L=-sum_k y_k log p_k。对 z_k 求导得 dL/dz_k=p_k-y_k，这是 softmax 与交叉熵合并后的简洁形式。",
        "若 a=Wx+b，delta=dL/da，则 dL/dW=delta x^T，dL/db=delta，dL/dx=W^T delta。对 batch 情况，dW 需对样本求和或平均。",
        "Sigmoid 输出可解释为概率但饱和区梯度小；Tanh 零中心但仍会饱和；ReLU 简单且缓解梯度消失但可能死亡；Leaky ReLU 给负半轴小斜率以缓解死亡 ReLU。",
        "反向传播是用链式法则在计算图上高效求梯度的方法；梯度下降是利用这些梯度更新参数的优化算法。反向传播负责算梯度，优化器负责怎么走。",
        "中心差分为 [J(theta+eps e_i)-J(theta-eps e_i)]/(2eps)。它需要对每个参数多次前向计算，代价极高且有数值误差，适合调试不适合训练。",
        "通用近似定理说明足够宽的单隐藏层非线性网络可逼近连续函数。局限是它不保证需要多少单元、能否高效训练或是否泛化好。",
        "g_B=1/B sum_{i in B} grad L_i。若 mini-batch 从训练集均匀抽样，E[g_B]=1/m sum_i grad L_i，即为全梯度的无偏估计。",
    ],
    [
        "目标 J_tilde=J+lambda/2 ||w||_2^2。梯度为 grad J + lambda w，因此 SGD 更新 w <- w - eta(grad J + lambda w) = (1-eta lambda)w - eta grad J。",
        "L2 惩罚平滑地缩小所有权重；L1 在零点不可导，等值线有尖角，最优解更容易落在坐标轴上，因此产生稀疏参数。",
        "min J(theta)+lambda Omega(theta) 与 min J(theta) s.t. Omega(theta)<=c 在一定条件下可通过拉格朗日乘子联系。lambda 与 c 控制可接受模型复杂度。",
        "合理增强包括平移、轻微旋转、随机裁剪、颜色扰动。若任务是识别 6 和 9，180 度旋转会破坏标签；医学图像中过强颜色变换也可能改变诊断意义。",
        "小高斯噪声迫使模型在样本邻域内输出稳定，相当于惩罚输入方向上的过大敏感性。它降低模型对微小扰动的依赖，从而提升鲁棒性。",
        "m~Bernoulli(p)，h_tilde=m*h/p。E[h_tilde]=E[m]h/p=ph/p=h，因此测试时无需再缩放。",
        "早停在验证误差开始上升时停止训练，限制参数继续贴合训练噪声。它相当于用训练轮数约束模型有效复杂度。",
        "J=sum_t alpha_t J_t(theta_shared,theta_t)。共享层学习通用表示，任务特定层处理各任务输出和差异；相关任务可互相提供归纳偏置。",
        "FGSM 为 x_adv=x+epsilon sign(grad_x L(f(x),y))。对抗训练求 min_theta E[max_{||r||<=epsilon}L(f(x+r;theta),y)]，内层找最坏扰动，外层提升鲁棒性。",
        "Dropout 可看作共享参数的指数级子网络集成；Bagging 训练多个独立模型并平均；普通集成显式保存多个模型，成本更高但通常更稳定。",
    ],
    [
        "纯优化通常只关心最小化给定目标函数；学习问题关心未见数据性能，训练目标只是泛化目标的代理。因此学习中的优化常配合早停、验证集和正则化。",
        "SGD 用 theta<-theta-eta g。Momentum 维护速度 v=mu v-eta g，再 theta<-theta+v。Nesterov 先在前瞻位置 theta+mu v 计算梯度，再更新速度。",
        "AdaGrad 累积所有历史平方梯度，学习率单调变小；RMSProp 用指数滑动平均替代累积；Adam 同时估计一阶矩和二阶矩，并使用偏差校正。",
        "若 m_0=0，m_t=(1-beta)sum_{i=1}^t beta^{t-i}g_i，其期望被因子 1-beta^t 缩小。除以 1-beta^t 可消除初始化为零带来的早期偏差。",
        "Xavier 方差为 2/(100+50)=1/75。He 方差为 2/100=0.02。若用均匀分布，还需把方差换成对应区间。",
        "病态曲率指不同方向曲率差异很大，等高线狭长。梯度下降在陡峭方向震荡，在平缓方向推进慢，导致收敛效率低。",
        "局部极小值附近所有方向曲率非负且函数值较低；鞍点某些方向曲率为正、某些为负。高维空间中鞍点很多，随机梯度噪声常能帮助逃离。",
        "若 ||g||>tau，令 g<-tau g/||g||；否则保持不变。RNN 长时间反传会产生梯度爆炸，裁剪可限制单步更新幅度。",
        "大 batch 梯度估计稳定、硬件吞吐高，但显存大、更新次数少、可能泛化较差。小 batch 噪声大但更新频繁，常有正则化效果。",
        "Newton 更新 theta<-theta-H^{-1}g。深度网络参数多，Hessian 存储、求逆和数值稳定性成本过高，且非凸下二阶方向也需谨慎处理。",
    ],
    [
        "padding=2 保持空间尺寸，输出为 32x32x16。参数量为 5*5*3*16+16=1216。",
        "H_out=floor((28+2*1-3)/2)+1=floor(27/2)+1=14，宽同理为 14。",
        "互相关为 Y[i,j]=sum_u sum_v X[i+u,j+v]K[u,v]。数学卷积会把 K 翻转；深度学习框架通常不翻转但仍称卷积。",
        "局部连接让每个输出只看局部感受野；权值共享让同一个卷积核在所有位置复用。参数量从全连接的 HWC*M 降为 K_h K_w C_in C_out。",
        "Max pooling：Y[i,j,c]=max_{u,v in window}X[iS+u,jS+v,c]。它降低高宽和计算量，对小范围平移不敏感，但会损失精确位置。",
        "卷积核梯度是输入局部窗口与上游梯度的累加相关。直观上，某个核元素的梯度等于它参与过的所有输出位置的 input_value * upstream_delta 之和。",
        "K_eff=K+(K-1)(d-1)=3+2*1=5。即 3x3 核在 dilation=2 时覆盖 5x5 范围中的 9 个采样点。",
        "常用公式 H_out=(H_in-1)S-2P+K+output_padding。它常用于解码器、语义分割、生成模型中的上采样。",
        "普通卷积参数 K_h K_w C_in C_out。深度可分离卷积为 K_h K_w C_in + C_in C_out。若 K=3,C_in=64,C_out=128，参数从 73728 降为 8768。",
        "结构化输出需要每个空间位置都有预测，如分割的像素类别。全卷积网络保留空间网格并用卷积产生 dense prediction，比展平全连接更适合。",
    ],
    [
        "h_t=phi(W_xh x_t+W_hh h_{t-1}+b_h)，o_t=W_hy h_t+b_y，p_t=softmax(o_t)。同一组 W_xh、W_hh、W_hy 在所有时间步共享。",
        "展开后每个时间步是一个复制的计算单元，但参数指向同一组变量。梯度会从所有时间步累加到共享参数上。",
        "d h_t/d h_k 包含多个 Jacobian 连乘。若谱半径和激活导数乘积小于 1，梯度指数衰减；大于 1，则梯度可能爆炸。",
        "i_t=sigma(W_xi x_t+W_hi h_{t-1}+b_i)，f_t=sigma(W_xf x_t+W_hf h_{t-1}+b_f)，g_t=tanh(W_xg x_t+W_hg h_{t-1}+b_g)，c_t=f_t*c_{t-1}+i_t*g_t，o_t=sigma(W_xo x_t+W_ho h_{t-1}+b_o)，h_t=o_t*tanh(c_t)。",
        "LSTM 有输入门、遗忘门、输出门和显式记忆单元；GRU 通常用更新门和重置门合并记忆与隐藏状态，参数更少，训练更快但表达控制略简化。",
        "双向 RNN 同时从左到右和从右到左处理序列，适合离线文本标注、语音转写后处理等。它不适合必须实时预测且不能看到未来的任务。",
        "深层 RNN 是在每个时间步堆叠多层循环层；时间展开深度来自序列长度，层深度来自网络堆叠，两者都会影响梯度传播。",
        "循环神经网络处理线性时间序列，递归神经网络按树或图的拓扑递归组合子节点表示。递归 NN 更适合句法树、表达式树等结构化输入。",
        "Teacher forcing 训练时把真实上一 token 输入解码器，推理时只能输入模型自己生成的 token。这会造成训练/推理分布不一致，即暴露偏差。",
        "截断 BPTT 只在固定窗口内反传，降低显存和计算量，也稳定训练。代价是超过窗口的长依赖梯度被截断，可能学不到远距离关系。",
    ],
    [
        "PCA 目标为 min_W sum_i ||x_i-WW^T x_i||^2，s.t. W^TW=I。最优 W 由样本协方差最大特征值对应的特征向量组成，也就是最大方差方向。",
        "PPCA：z~N(0,I)，x|z~N(Wz+mu,sigma^2 I)。边缘分布为 x~N(mu,WW^T+sigma^2 I)。",
        "PPCA 假设观测噪声为 sigma^2 I，各维噪声相同且独立。因子分析假设 Psi 为对角矩阵，不同观测维度可有不同噪声方差。",
        "目标 min_{D,a} ||x-Da||^2+lambda||a||_1。D 是字典基，a 是样本在字典上的稀疏编码；多个样本共同学习 D。",
        "线性欠完备 AE 若用平方重构误差且没有额外非线性，其最优编码子空间与 PCA 主子空间一致。它学习的是低维线性投影和重构。",
        "编码 h=f(x)，解码 r=g(h)，损失 L(x,r)=||x-r||^2 或逐维交叉熵。训练目标是让 r 接近 x，同时通过结构或正则让 h 有用。",
        "稀疏 AE 在重构损失外加入 Omega(h)，惩罚过多激活。即使编码维度较大，模型也被迫用少数活跃单元解释输入，避免简单复制。",
        "去噪 AE 采样 x_tilde~q(x_tilde|x)，最小化 ||x-g(f(x_tilde))||^2。它学习从受扰动样本回到数据流形，提升对输入噪声的鲁棒性。",
        "收缩 AE 用 L + lambda ||J_f(x)||_F^2，其中 J_f 是编码器对输入的 Jacobian。惩罚表示对输入小扰动过敏，使局部表示更稳定。",
        "稀疏编码通常为每个样本求解稀疏 a；自编码器用前向网络直接给出编码；预测稀疏分解增加编码预测器，使推理比单纯优化稀疏系数更快。",
    ],
    [
        "流程是先训练第一层无监督模型得到表示，再把该表示作为下一层输入逐层训练，最后把各层堆叠成深层网络，用监督损失全局微调。",
        "早期深层网络缺少大数据、好初始化、归一化和优化技巧，预训练能提供较好初值。现代 ReLU、BatchNorm、残差网络、大规模数据和优化器降低了对它的依赖。",
        "特征提取固定预训练骨干，只训练新头部；部分微调解冻高层；全量微调更新所有层。数据少时偏向冻结，目标域差异大且数据多时偏向全量微调。",
        "若 p_s(y|x)=p_t(y|x) 但 p_s(x) != p_t(x)，目标风险 R_t=E_{p_s}[p_t(x)/p_s(x) L(f(x),y)]。",
        "负迁移是源域知识降低目标域性能。可通过与从头训练、只用目标域训练、冻结不同层的消融比较发现。",
        "半监督学习利用少量标注和大量未标注同域数据；迁移学习从源任务/源域迁移知识；领域自适应专门处理源域和目标域分布差异。",
        "分布式表示用多个连续维度共同表达因素。不同维度组合可表示指数级概念，并让相似概念共享部分维度，从而提高组合泛化。",
        "有向图联合分布为 p(x_1,...,x_n)=prod_i p(x_i|Pa_i)。每个变量只依赖父节点，图结构编码条件独立假设。",
        "无向图可写 p(x)=exp(-E(x))/Z，Z=sum_x exp(-E(x))。Z 让概率归一化，但在高维离散空间常不可精确求和。",
        "深度网络可学习图模型中的特征表示、势函数、条件分布或近似后验 q(z|x)，也可用于摊销推断，把每次优化变成一次前向传播。",
    ],
    [
        "s_hat=1/n sum_i f(x_i)，x_i~p。E[s_hat]=1/n sum_i E[f(x_i)]=E_p[f(x)]=s，所以无偏。",
        "若样本独立同分布，Var(s_hat)=Var(1/n sum_i f_i)=1/n^2 sum_i Var(f_i)=Var(f)/n。因此标准误差按 1/sqrt(n) 下降。",
        "E_p[f]=int f(x)p(x)dx=int f(x)p(x)/q(x) q(x)dx=E_q[f p/q]。q 应覆盖 p 的高概率区域，并使权重 p/q 方差尽量小。",
        "alpha=min(1, p(x')q(x|x')/[p(x)q(x'|x)])。若提议对称，化简为 min(1,p(x')/p(x))。",
        "Gibbs 每次从一个变量的完整条件分布 p(x_j|x_-j) 采样，相当于 MH 中该提议总被接受的特殊情形。",
        "混合慢指马尔科夫链长时间停留在局部模式，样本自相关高、有效样本量低。估计会偏向已访问区域，置信区间也会过于乐观。",
        "E 步计算 q(z)=p(z|x,theta_old) 或其期望，构造 Q(theta,theta_old)=E_q log p(x,z;theta)。M 步最大化 Q 得到新 theta。",
        "log p(x)=log p(x,z)/p(z|x)。取 q 期望可得 log p(x)=E_q log p(x,z)-E_q log q(z)+KL(q||p(z|x))，前两项是 ELBO。",
        "平均场令 q(z)=prod_j q_j(z_j)，降低推断难度。优点是可优化、可扩展；缺点是独立性假设强，可能低估后验不确定性。",
        "采样适合可构造采样器且需要渐近精确估计的场景；EM 适合潜变量模型的点估计；变分推断适合大规模快速近似后验，但有近似偏差。",
    ],
    [
        "BM 能量可写 E(s)=-sum_{i<j}w_ij s_i s_j - sum_i b_i s_i。概率 p(s)=exp(-E(s))/Z，Z=sum_s exp(-E(s))。",
        "对 n 个二值变量，Z 需要对 2^n 个状态求和。似然梯度还包含模型分布下的期望，通常也需采样近似。",
        "RBM 能量 E(v,h)=-b^Tv-c^Th-v^TWh。条件分布为 p(h_j=1|v)=sigma(c_j+W_:j^T v)，p(v_i=1|h)=sigma(b_i+W_i:h)。",
        "log p(v)=log sum_h exp(-E(v,h))-log Z。求 W 梯度得到数据相的 E_{p(h|v)}[vh^T] 减模型相的 E_{p(v,h)}[vh^T]。",
        "CD-k 从数据 v0 出发，采 h0~p(h|v0)，交替采 v,h 运行 k 步 Gibbs，最后用 v0h0^T-v_kh_k^T 近似梯度更新。",
        "RBM 是一层可见一层隐藏的二部无向模型。DBN 顶层是 RBM、低层为有向生成连接。DBM 多层均为无向连接，推断更困难。",
        "可令 v_i|h 服从 Gaussian，均值由 b_i+W_i:h 给出，隐藏层仍常为 Bernoulli。这得到 Gaussian-Bernoulli RBM，适合连续输入。",
        "卷积 BM 使用局部连接和权值共享，能捕捉图像局部平移重复结构，参数少于全连接 BM，并可学习类似滤波器的特征。",
        "有向生成网络常可祖先采样，但后验推断可能困难；无向能量模型定义灵活，但配分函数和模型期望难算。",
        "指标包括对数似然或其估计、样本质量、多样性、覆盖率、下游任务表现和人评。单一指标可能只反映清晰度或只反映似然，不能完整衡量生成分布。",
    ],
]


def choose_font(candidates: Iterable[Path], fallback: str) -> str:
    for path in candidates:
        if path.exists():
            return str(path)
    return fallback


def register_fonts() -> tuple[str, str]:
    normal_path = choose_font(FONT_CANDIDATES, "")
    bold_path = choose_font(BOLD_FONT_CANDIDATES, normal_path)
    if normal_path:
        pdfmetrics.registerFont(TTFont("CN", normal_path))
    else:
        raise FileNotFoundError("No Chinese font found in C:\\Windows\\Fonts")
    if bold_path:
        pdfmetrics.registerFont(TTFont("CN-Bold", bold_path))
    else:
        pdfmetrics.registerFont(TTFont("CN-Bold", normal_path))
    return "CN", "CN-Bold"


def styles() -> dict[str, ParagraphStyle]:
    normal, bold = register_fonts()
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "TitleCN",
            parent=base["Title"],
            fontName=bold,
            fontSize=22,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#1F2937"),
            wordWrap="CJK",
            spaceAfter=10,
        ),
        "subtitle": ParagraphStyle(
            "SubtitleCN",
            parent=base["Normal"],
            fontName=normal,
            fontSize=10.5,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4B5563"),
            wordWrap="CJK",
            spaceAfter=16,
        ),
        "h1": ParagraphStyle(
            "H1CN",
            parent=base["Heading1"],
            fontName=bold,
            fontSize=16,
            leading=22,
            textColor=colors.HexColor("#111827"),
            wordWrap="CJK",
            spaceBefore=12,
            spaceAfter=8,
        ),
        "h2": ParagraphStyle(
            "H2CN",
            parent=base["Heading2"],
            fontName=bold,
            fontSize=13,
            leading=18,
            textColor=colors.HexColor("#1F2937"),
            wordWrap="CJK",
            spaceBefore=8,
            spaceAfter=5,
        ),
        "body": ParagraphStyle(
            "BodyCN",
            parent=base["BodyText"],
            fontName=normal,
            fontSize=10.2,
            leading=16,
            alignment=TA_LEFT,
            textColor=colors.HexColor("#111827"),
            wordWrap="CJK",
            spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "BulletCN",
            parent=base["BodyText"],
            fontName=normal,
            fontSize=9.8,
            leading=15,
            leftIndent=12,
            firstLineIndent=-8,
            wordWrap="CJK",
            spaceAfter=3,
        ),
        "formula": ParagraphStyle(
            "FormulaCN",
            parent=base["BodyText"],
            fontName=normal,
            fontSize=9.5,
            leading=14,
            leftIndent=10,
            rightIndent=6,
            backColor=colors.HexColor("#F3F4F6"),
            borderColor=colors.HexColor("#E5E7EB"),
            borderWidth=0.4,
            borderPadding=4,
            wordWrap="CJK",
            spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "SmallCN",
            parent=base["BodyText"],
            fontName=normal,
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#4B5563"),
            wordWrap="CJK",
        ),
    }


def p(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(html.escape(text), style)


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("CN", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawCentredString(A4[0] / 2, 11 * mm, f"{doc.title}  |  第 {canvas.getPageNumber()} 页")
    canvas.restoreState()


def build_pdf(title: str, subtitle: str, sections: list, output: Path) -> None:
    st = styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title=title,
        author="Codex Scholar",
    )
    story = [p(title, st["title"]), p(subtitle, st["subtitle"])]
    for item in sections:
        kind = item[0]
        if kind == "h1":
            story.append(p(item[1], st["h1"]))
        elif kind == "h2":
            story.append(p(item[1], st["h2"]))
        elif kind == "body":
            story.append(p(item[1], st["body"]))
        elif kind == "bullet":
            story.append(p("• " + item[1], st["bullet"]))
        elif kind == "formula":
            story.append(p(item[1], st["formula"]))
        elif kind == "small":
            story.append(p(item[1], st["small"]))
        elif kind == "space":
            story.append(Spacer(1, item[1]))
        elif kind == "pagebreak":
            story.append(PageBreak())
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)


def review_sections() -> list:
    sections = [
        ("body", "说明：本复习大纲按用户给定 10 个课程单元组织，结合本地教材《神经网络与深度学习》、本地课程练习目录，以及开放网络教材/课程资料综合整理。公式采用纯文本写法，便于打印复习。"),
        ("h1", "总复习路线"),
        ("bullet", "先掌握机器学习风险、损失、MLE/MAP、偏差-方差这些底层概念。"),
        ("bullet", "再掌握前馈网络、反向传播、正则化、优化、CNN、RNN 六个核心训练模块。"),
        ("bullet", "最后把自编码器、预训练/迁移、概率图模型、采样/VI、BM/RBM 串成生成建模主线。"),
    ]
    for ch in CHAPTERS:
        sections.append(("pagebreak",))
        sections.append(("h1", ch["title"]))
        sections.append(("h2", "学习目标"))
        for s in ch["scope"]:
            sections.append(("bullet", s))
        sections.append(("h2", "核心知识点"))
        for s in ch["concepts"]:
            sections.append(("bullet", s))
        sections.append(("h2", "重点公式"))
        for s in ch["formulas"]:
            sections.append(("formula", s))
        sections.append(("h2", "易错点"))
        for s in ch["pitfalls"]:
            sections.append(("bullet", s))
        sections.append(("h2", "考前自查"))
        for s in ch["checklist"]:
            sections.append(("bullet", s))
    sections.append(("pagebreak",))
    sections.append(("h1", "参考来源"))
    for s in SOURCES:
        sections.append(("small", s))
    return sections


def question_sections() -> list:
    sections = [
        ("body", "说明：本习题集共 100 题，每个课程单元 10 题。题目依据教材章节、课程安排、本地练习主题和开放网络资料综合改编/自拟，重点训练公式、推导、概念辨析和小计算。"),
    ]
    for idx, ch in enumerate(CHAPTERS, 1):
        sections.append(("h1", ch["title"]))
        for qidx, q in enumerate(QUESTIONS[idx - 1], 1):
            sections.append(("body", f"{idx}.{qidx} {q}"))
        if idx != len(CHAPTERS):
            sections.append(("pagebreak",))
    sections.append(("h1", "参考来源"))
    for s in SOURCES:
        sections.append(("small", s))
    return sections


def answer_sections() -> list:
    sections = [
        ("body", "说明：答案编号与《习题.pdf》完全对应。解答以复习用途为主，保留关键公式、推导路径和结论。"),
    ]
    for idx, ch in enumerate(CHAPTERS, 1):
        sections.append(("h1", ch["title"]))
        for qidx, ans in enumerate(ANSWERS[idx - 1], 1):
            sections.append(("h2", f"{idx}.{qidx} 解答"))
            sections.append(("body", ans))
        if idx != len(CHAPTERS):
            sections.append(("pagebreak",))
    sections.append(("h1", "参考来源"))
    for s in SOURCES:
        sections.append(("small", s))
    return sections


def markdown_from_sections(title: str, subtitle: str, sections: list) -> str:
    lines = [f"# {title}", "", subtitle, ""]
    for item in sections:
        kind = item[0]
        if kind == "h1":
            lines += ["", f"## {item[1]}", ""]
        elif kind == "h2":
            lines += ["", f"### {item[1]}", ""]
        elif kind == "body":
            lines += [item[1], ""]
        elif kind == "bullet":
            lines += [f"- {item[1]}"]
        elif kind == "formula":
            lines += [f"> 公式：{item[1]}"]
        elif kind == "small":
            lines += [f"- {item[1]}"]
        elif kind == "pagebreak":
            lines += ["", "<div style=\"page-break-after: always\"></div>", ""]
    return "\n".join(lines).strip() + "\n"


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def main() -> None:
    assert len(CHAPTERS) == 10
    assert len(QUESTIONS) == 10
    assert len(ANSWERS) == 10
    assert sum(len(x) for x in QUESTIONS) == 100
    assert sum(len(x) for x in ANSWERS) == 100

    outputs = [
        (
            "神经网络与深度学习复习大纲",
            "按课程安排整理：知识点、公式、易错点、考前自查",
            review_sections(),
            ROOT / "复习.md",
            ROOT / "复习.pdf",
        ),
        (
            "神经网络与深度学习习题复习集",
            "10 个单元，共 100 题",
            question_sections(),
            ROOT / "习题.md",
            ROOT / "习题.pdf",
        ),
        (
            "神经网络与深度学习习题答案",
            "与习题集逐题对应的解答与公式",
            answer_sections(),
            ROOT / "习题答案.md",
            ROOT / "习题答案.pdf",
        ),
    ]

    for title, subtitle, sections, md_path, pdf_path in outputs:
        write_text(md_path, markdown_from_sections(title, subtitle, sections))
        build_pdf(title, subtitle, sections, pdf_path)
        print(f"WROTE {md_path.name} {os.path.getsize(md_path)} bytes")
        print(f"WROTE {pdf_path.name} {os.path.getsize(pdf_path)} bytes")


if __name__ == "__main__":
    main()
