"""考试用线性回归：两种基函数 × 两种优化方法。

与课程练习 chap2_linear_regression 对应：
1. polynomial_basis：多项式基函数；
2. gaussian_basis：高斯基函数；
3. fit_least_squares：最小二乘法；
4. fit_gradient_descent：批量梯度下降。

运行：
    python linear_regression_exam.py
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "exercise-神经网络与深度学习课程练习" / "chap2_linear_regression"


def load_data(filename: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """读取两列数据 x, y，并统一为一维浮点数组。"""
    data = np.loadtxt(filename, dtype=np.float64)
    return data[:, 0], data[:, 1]


@dataclass
class BasisTransformer:
    """只用训练集确定缩放范围、中心和宽度，再原样变换测试集。"""

    basis: str = "polynomial"
    feature_num: int = 8
    x_min: float | None = None
    x_max: float | None = None
    centers: np.ndarray | None = None
    sigma: float | None = None

    def fit(self, x: np.ndarray) -> "BasisTransformer":
        x = np.asarray(x, dtype=np.float64).reshape(-1)
        self.x_min = float(np.min(x))
        self.x_max = float(np.max(x))
        if self.basis == "gaussian":
            self.centers = np.linspace(self.x_min, self.x_max, self.feature_num)
            span = max(self.x_max - self.x_min, 1e-12)
            self.sigma = span / max(self.feature_num - 1, 1)
        elif self.basis != "polynomial":
            raise ValueError("basis 必须是 'polynomial' 或 'gaussian'")
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.x_min is None or self.x_max is None:
            raise RuntimeError("必须先对训练集调用 fit")
        x = np.asarray(x, dtype=np.float64).reshape(-1, 1)

        if self.basis == "polynomial":
            # 将训练区间缩放到 [-1, 1]，避免 x^j 数值过大。
            span = max(self.x_max - self.x_min, 1e-12)
            z = 2.0 * (x - self.x_min) / span - 1.0
            powers = np.arange(1, self.feature_num + 1).reshape(1, -1)
            return z**powers

        assert self.centers is not None and self.sigma is not None
        return np.exp(-((x - self.centers.reshape(1, -1)) ** 2) / (2.0 * self.sigma**2))

    def fit_transform(self, x: np.ndarray) -> np.ndarray:
        return self.fit(x).transform(x)


def design_matrix(features: np.ndarray) -> np.ndarray:
    """在第 1 列加入常数 1，将偏置 b 并入权重向量。"""
    return np.column_stack([np.ones(features.shape[0]), features])


def fit_least_squares(phi: np.ndarray, y: np.ndarray) -> np.ndarray:
    """最小二乘：w=(Phi^T Phi)^(-1)Phi^T y；pinv 兼容不可逆情形。"""
    return np.linalg.pinv(phi.T @ phi) @ phi.T @ y


def fit_gradient_descent(
    phi: np.ndarray,
    y: np.ndarray,
    learning_rate: float = 0.05,
    max_iter: int = 100_000,
    tol: float = 1e-12,
) -> tuple[np.ndarray, list[float]]:
    """最小化 J(w)=||Phi w-y||^2/(2N) 的批量梯度下降。"""
    n = phi.shape[0]
    w = np.zeros(phi.shape[1], dtype=np.float64)
    history: list[float] = []
    previous_loss = np.inf

    for step in range(max_iter):
        error = phi @ w - y
        gradient = phi.T @ error / n
        w -= learning_rate * gradient

        if step % 100 == 0 or step == max_iter - 1:
            loss = float((error @ error) / (2.0 * n))
            history.append(loss)
            if abs(previous_loss - loss) < tol:
                break
            previous_loss = loss

    return w, history


class LinearBasisRegression:
    def __init__(self, basis: str, feature_num: int, method: str) -> None:
        self.transformer = BasisTransformer(basis, feature_num)
        self.method = method
        self.w: np.ndarray | None = None
        self.loss_history: list[float] = []

    def fit(self, x: np.ndarray, y: np.ndarray) -> "LinearBasisRegression":
        phi = design_matrix(self.transformer.fit_transform(x))
        if self.method == "least_squares":
            self.w = fit_least_squares(phi, y)
        elif self.method == "gradient_descent":
            self.w, self.loss_history = fit_gradient_descent(phi, y)
        else:
            raise ValueError("method 必须是 'least_squares' 或 'gradient_descent'")
        return self

    def predict(self, x: np.ndarray) -> np.ndarray:
        if self.w is None:
            raise RuntimeError("必须先调用 fit")
        phi = design_matrix(self.transformer.transform(x))
        return phi @ self.w


def rmse(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((y_true - y_pred) ** 2)))


def main() -> None:
    x_train, y_train = load_data(DATA_DIR / "train.txt")
    x_test, y_test = load_data(DATA_DIR / "test.txt")

    settings = [
        ("polynomial", 8, "least_squares"),
        ("polynomial", 8, "gradient_descent"),
        ("gaussian", 12, "least_squares"),
        ("gaussian", 12, "gradient_descent"),
    ]
    for basis, feature_num, method in settings:
        model = LinearBasisRegression(basis, feature_num, method).fit(x_train, y_train)
        train_error = rmse(y_train, model.predict(x_train))
        test_error = rmse(y_test, model.predict(x_test))
        print(
            f"basis={basis:10s} method={method:16s} "
            f"train_RMSE={train_error:8.4f} test_RMSE={test_error:8.4f}"
        )


if __name__ == "__main__":
    main()
