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
    plot_gmm(x, y_pred, params, save_path='e:\\平时作业\\神经网络与深度学习\\exercise-神经网络与深度学习课程练习\\chap11_gaussian_mixture\\gmm_clustering.png')
