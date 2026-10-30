# python: 3.5.2
# encoding: utf-8

import os
import numpy as np


def load_data(fname):
    """
    载入数据。
    """
    with open(fname, 'r') as f:
        data = []
        line = f.readline()
        for line in f:
            line = line.strip().split()
            x1 = float(line[0])
            x2 = float(line[1])
            t = int(line[2])
            data.append([x1, x2, t])
        return np.array(data)


def eval_acc(label, pred):
    """
    计算准确率。
    """
    return np.sum(label == pred) / len(pred)


class SVM():
    """
    SVM模型。
    """

    def __init__(self, lr=1e-3, lambda_=1e-2, n_iters=20000):
        """Initialize a simple linear SVM classifier.

        Notes:
            This template is used by the provided `__main__` block which loads
            `train_linear.txt` / `test_linear.txt`.

            The original README mentions additional parts (kernel / multi-class).
            This file template only exposes a single SVM class with `train`
            and `predict`, so we implement a linear SVM with hinge loss.
        """
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
                # d/dw: lambda*w - mean(t_i * x_i) over misclassified / within-margin samples
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


if __name__ == '__main__':
    # 载入数据，实际实用时将x替换为具体名称
    here = os.path.dirname(os.path.abspath(__file__))
    train_file = os.path.join(here, 'data', 'train_linear.txt')
    test_file = os.path.join(here, 'data', 'test_linear.txt')
    data_train = load_data(train_file)  # 数据格式[x1, x2, t]
    data_test = load_data(test_file)

    # 使用训练集训练SVM模型
    svm = SVM()  # 初始化模型
    svm.train(data_train)  # 训练模型

    # 使用SVM模型预测标签
    x_train = data_train[:, :2]  # feature [x1, x2]
    t_train = data_train[:, 2]  # 真实标签
    t_train_pred = svm.predict(x_train)  # 预测标签
    x_test = data_test[:, :2]
    t_test = data_test[:, 2]
    t_test_pred = svm.predict(x_test)

    # 评估结果，计算准确率
    acc_train = eval_acc(t_train, t_train_pred)
    acc_test = eval_acc(t_test, t_test_pred)
    print("train accuracy: {:.1f}%".format(acc_train * 100))
    print("test accuracy: {:.1f}%".format(acc_test * 100))
