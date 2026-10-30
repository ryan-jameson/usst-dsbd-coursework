import numpy as np

try:
    import tensorflow as tf
except Exception:  # pragma: no cover
    tf = None
import os

class RL_QG_agent:
    def __init__(self):
        self.model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Reversi")
        os.makedirs(self.model_dir, exist_ok=True)

        self.rng = np.random.default_rng(0)

        # Optional TF model (not strictly required for the demo interface).
        self.model = None
        self.ckpt_manager = None
        if tf is not None:
            self.init_model()

    def init_model(self):
        # Define a small policy/value network.
        # Input state: (3, 8, 8) -> output logits for 64 board positions.
        inputs = tf.keras.layers.Input(shape=(3, 8, 8))
        x = tf.keras.layers.Flatten()(inputs)
        x = tf.keras.layers.Dense(128, activation='relu')(x)
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        
        # Policy Head
        logits = tf.keras.layers.Dense(64, name='policy_logits')(x)
        # Value Head (-1 to 1 winning probability estimation)
        value = tf.keras.layers.Dense(1, activation='tanh', name='value_head')(x)
        
        self.model = tf.keras.Model(inputs=inputs, outputs=[logits, value])

        # Checkpoint for save/load.
        ckpt = tf.train.Checkpoint(model=self.model)
        self.ckpt_manager = tf.train.CheckpointManager(ckpt, self.model_dir, max_to_keep=1)

    def evaluate(self, state, enables):
        """返回 (最优action, 8x8位置概率热力值, 当前胜率评估)"""
        enables = [int(a) for a in enables if 0 <= int(a) < 64]
        
        if not enables:
            return 0, np.zeros((8,8)), 0.0

        if self.model is None:
            act = int(self.rng.choice(enables))
            probs = np.zeros((64,))
            probs[enables] = 1.0 / len(enables)
            return act, probs.reshape((8,8)), 0.0

        s = np.asarray(state, dtype=np.float32)
        if s.shape != (3, 8, 8):
            s = s.reshape(3, 8, 8)
            
        logits, val_tensor = self.model(s[None, ...], training=False)
        logits = logits.numpy().reshape(-1)
        value = float(val_tensor.numpy()[0, 0])

        # Mask invalid actions and choose the best among enabled.
        mask = np.full((64,), -1e9, dtype=np.float32)
        mask[np.asarray(enables, dtype=np.int64)] = 0.0
        
        # Softmax for probabilities
        exps = np.exp(logits + mask)
        sum_exp = np.sum(exps)
        probs = exps / sum_exp if sum_exp > 0 else np.zeros(64)
        
        action = int(np.argmax(logits + mask))
        return action, probs.reshape((8,8)), value

    def place(self,state,enables):
        action, _, _ = self.evaluate(state, enables)
        return action

    def save_model(self):  # 保存 模型
        if self.ckpt_manager is None:
            return
        self.ckpt_manager.save()

    def load_model(self):# 重新导入模型
        if self.ckpt_manager is None:
            return
        latest = self.ckpt_manager.latest_checkpoint
        if latest:
            # Expect partial to avoid warnings if optimizer slots are missing.
            self.ckpt_manager.checkpoint.restore(latest).expect_partial()

    # 定义自己需要的函数
