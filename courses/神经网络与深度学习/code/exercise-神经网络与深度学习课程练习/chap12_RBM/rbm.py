"""Restricted Boltzmann Machine (RBM) exercise.

Original template was marked for Python 2.7; this version runs on Python 3.
"""

import os
import urllib.request

import numpy as np
import matplotlib.pyplot as plt


class RBM:
    """Restricted Boltzmann Machine."""

    def __init__(self, n_hidden=2, n_observe=784):
        """Initialize model."""

        self.n_hidden = int(n_hidden)
        self.n_observe = int(n_observe)

        rng = np.random.default_rng(0)
        # Small random init helps avoid saturation.
        self.W = (rng.normal(loc=0.0, scale=0.01, size=(self.n_observe, self.n_hidden))).astype(np.float32)
        self.b_v = np.zeros((self.n_observe,), dtype=np.float32)
        self.b_h = np.zeros((self.n_hidden,), dtype=np.float32)

        # Training hyperparameters (kept simple for the exercise).
        self.lr = 0.1
        self.batch_size = 100
        self.n_epochs = 5
        self.cd_k = 1
        self.rng = rng

    @staticmethod
    def _sigmoid(x):
        x = np.clip(x, -30.0, 30.0)
        return 1.0 / (1.0 + np.exp(-x))

    def _sample_bernoulli(self, p):
        return (self.rng.random(p.shape) < p).astype(np.float32)

    def train(self, data):
        """Train model using data."""

        x = np.asarray(data)
        if x.ndim == 3:
            x = x.reshape(x.shape[0], -1)
        if x.ndim != 2:
            raise ValueError(f"Expected data shape (N, D) or (N, H, W); got {x.shape}")
        if x.shape[1] != self.n_observe:
            raise ValueError(f"Expected observe dim {self.n_observe}, got {x.shape[1]}")

        x = x.astype(np.float32)
        # If input isn't already binary, binarize by threshold.
        if x.max() > 1.0:
            x = (x > 127.0).astype(np.float32)

        n = x.shape[0]
        history = []
        for epoch in range(self.n_epochs):
            perm = self.rng.permutation(n)
            x_shuf = x[perm]

            epoch_err = 0.0
            n_batches = 0
            for start in range(0, n, self.batch_size):
                v0 = x_shuf[start : start + self.batch_size]
                if v0.size == 0:
                    continue
                bs = v0.shape[0]

                # Positive phase.
                h0_prob = self._sigmoid(v0 @ self.W + self.b_h)
                h_state = self._sample_bernoulli(h0_prob)

                # Negative phase (CD-k).
                v_state = v0
                hk_prob = h0_prob
                for _ in range(self.cd_k):
                    v_prob = self._sigmoid(h_state @ self.W.T + self.b_v)
                    v_state = self._sample_bernoulli(v_prob)
                    hk_prob = self._sigmoid(v_state @ self.W + self.b_h)
                    h_state = self._sample_bernoulli(hk_prob)

                # Parameter update.
                self.W += (self.lr / bs) * ((v0.T @ h0_prob) - (v_state.T @ hk_prob))
                self.b_v += (self.lr / bs) * np.sum(v0 - v_state, axis=0)
                self.b_h += (self.lr / bs) * np.sum(h0_prob - hk_prob, axis=0)

                # Reconstruction error for monitoring.
                epoch_err += float(np.mean((v0 - v_prob) ** 2))
                n_batches += 1

            if n_batches:
                epoch_err /= n_batches
            print(f"epoch {epoch + 1}/{self.n_epochs}  recon_mse={epoch_err:.6f}")
            history.append(epoch_err)
        return history

    def sample(self):
        """Sample from trained model."""

        v = self._sample_bernoulli(np.full((1, self.n_observe), 0.5, dtype=np.float32))
        h = np.zeros((1, self.n_hidden), dtype=np.float32)
        for _ in range(200):
            h_prob = self._sigmoid(v @ self.W + self.b_h)
            h = self._sample_bernoulli(h_prob)
            v_prob = self._sigmoid(h @ self.W.T + self.b_v)
            v = self._sample_bernoulli(v_prob)

        # Try to reshape into an image if possible.
        side = int(round(np.sqrt(self.n_observe)))
        if side * side == self.n_observe:
            return v.reshape(side, side)
        return v.reshape(-1)


def _ensure_mnist_bin(data_path: str) -> None:
    if os.path.exists(data_path):
        return

    url = 'https://storage.googleapis.com/tensorflow/tf-keras-datasets/mnist.npz'
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    tmp_path = data_path + '.tmp.npz'
    print(f"mnist_bin.npy not found; downloading MNIST from {url} ...")
    try:
        urllib.request.urlretrieve(url, tmp_path)
        with np.load(tmp_path) as f:
            x_train = f['x_train']  # (60000, 28, 28), uint8
        mnist_bin = (x_train > 127).astype(np.uint8)
        np.save(data_path, mnist_bin)
        print(f"saved {data_path} with shape {mnist_bin.shape}")
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


# train restricted boltzmann machine using mnist dataset
if __name__ == '__main__':
    # load mnist dataset, no label
    here = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(here, 'mnist_bin.npy')
    _ensure_mnist_bin(data_path)
    mnist = np.load(data_path)  # 60000x28x28
    n_imgs, n_rows, n_cols = mnist.shape
    img_size = n_rows * n_cols
    print("Dataset shape:", mnist.shape)

    # construct rbm model
    # 使用 64 个隐变量以获取更好的效果（原为 2，由于参数太少难以进行良好的重构和可视化）
    n_hidden = 64
    rbm = RBM(n_hidden, img_size)
    rbm.n_epochs = 10 # 增加一些训练轮数以查看损失曲线

    # train rbm model using mnist
    print("Training RBM...")
    history = rbm.train(mnist)

    # 1. 可视化训练损失曲线
    plt.figure(figsize=(8, 5))
    plt.plot(range(1, len(history) + 1), history, marker='o', linestyle='-')
    plt.title("RBM Training Reconstruction MSE")
    plt.xlabel("Epoch")
    plt.ylabel("MSE")
    plt.grid(True)
    plt.savefig(os.path.join(here, "loss_curve.png"))
    plt.show()

    # 2. 可视化隐藏层权重 (Receptive Fields)
    plt.figure(figsize=(8, 8))
    plt.suptitle("Hidden Unit Weights (Receptive Fields)", fontsize=16)
    W_img = rbm.W.T # Shape: (64, 784)
    for i in range(min(n_hidden, 64)):
        plt.subplot(8, 8, i + 1)
        plt.imshow(W_img[i].reshape(n_rows, n_cols), cmap='viridis')
        plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(here, "weights_visualization.png"))
    plt.show()

    # 3. 可视化重构效果 (对比原图和重构图)
    n_recon = 10
    samples_idx = np.random.choice(n_imgs, n_recon, replace=False)
    test_imgs = mnist[samples_idx].reshape(n_recon, 784).astype(np.float32)
    
    # 前向传播再后向传播计算重构
    h_prob = rbm._sigmoid(test_imgs @ rbm.W + rbm.b_h)
    h_state = rbm._sample_bernoulli(h_prob)
    v_prob = rbm._sigmoid(h_state @ rbm.W.T + rbm.b_v)
    recon_imgs = v_prob # 使用概率值使得图像显示更加平滑
    
    plt.figure(figsize=(n_recon, 2.5))
    plt.suptitle("Original Images vs Reconstructed Images", fontsize=14)
    for i in range(n_recon):
        # 原图
        plt.subplot(2, n_recon, i + 1)
        plt.imshow(test_imgs[i].reshape(n_rows, n_cols), cmap='gray')
        plt.axis('off')
        # 重构图
        plt.subplot(2, n_recon, n_recon + i + 1)
        plt.imshow(recon_imgs[i].reshape(n_rows, n_cols), cmap='gray')
        plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(here, "reconstruction.png"))
    plt.show()

    # 4. 可视化生成的样本
    plt.figure(figsize=(8, 8))
    plt.suptitle("Generated Samples from RBM", fontsize=16)
    for i in range(25):
        s = rbm.sample()
        plt.subplot(5, 5, i + 1)
        plt.imshow(s, cmap='gray')
        plt.axis('off')
    plt.tight_layout()
    plt.savefig(os.path.join(here, "generated_samples.png"))
    plt.show()
