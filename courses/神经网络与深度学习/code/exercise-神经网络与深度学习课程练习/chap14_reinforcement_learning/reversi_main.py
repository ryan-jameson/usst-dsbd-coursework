import gymnasium as gym
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import imageio
import os

from RL_QG_agent import RL_QG_agent

# Register the bundled env without modifying site-packages.
import reversi

reversi.register_env()

env = gym.make('Reversi8x8-v0')
env.reset()

agent = RL_QG_agent()
agent.load_model()

max_epochs = 1
save_dir = "vis_output"
os.makedirs(save_dir, exist_ok=True)

# setup plot for offline rendering
plt.style.use('dark_background')
fig, (ax_board, ax_curves) = plt.subplots(1, 2, figsize=(16, 8))

GIF_FRAMES = []

def render_gui(state, t, heatmap=np.zeros((8,8))):
    ax_board.clear()
    ax_board.set_facecolor('#2B8E2A')  
    ax_board.set_xlim(-0.5, 7.5)
    ax_board.set_ylim(7.5, -0.5)
    ax_board.set_xticks(np.arange(-0.5, 8, 1))
    ax_board.set_yticks(np.arange(-0.5, 8, 1))
    ax_board.grid(color='black', linestyle='-', linewidth=2)
    ax_board.set_xticklabels([])
    ax_board.set_yticklabels([])
    ax_board.set_title(f"Reversi Board w/ Heatmap - Step {t}")

    # Draw Heatmap
    if np.max(heatmap) > 0:
        im = ax_board.imshow(heatmap, cmap='hot', alpha=0.5, vmin=0, vmax=np.max(heatmap))
    
    # Draw Pieces
    for i in range(8):
        for j in range(8):
            if state[0, i, j] == 1: # Black
                circle = patches.Circle((j, i), 0.4, facecolor='black', edgecolor='k', zorder=10)
                ax_board.add_patch(circle)
            elif state[1, i, j] == 1: # White
                circle = patches.Circle((j, i), 0.4, facecolor='white', edgecolor='k', zorder=10)
                ax_board.add_patch(circle)
                
for i_episode in range(max_epochs):
    observation = env.reset()
    
    black_scores_history = []
    white_scores_history = []
    val_history = []
    steps_history = []
    
    for t in range(100):
        action = [1,2]

        ################### 黑棋 ############################### 0表示黑棋
        enables = env.unwrapped.possible_actions
        
        # 为了演示，依然使用评估函数（由于当前我们不关注黑棋预测，只给全0热力）
        if len(enables) == 0:
            action_ = env.unwrapped.board_size**2 + 1
        else:
            action_ = random.choice(enables)
        
        render_gui(env.unwrapped.state, t, heatmap=np.zeros((8,8)))
        
        # 记录当前比分
        black_cnt = np.sum(env.unwrapped.state[0, :, :] == 1)
        white_cnt = np.sum(env.unwrapped.state[1, :, :] == 1)
        black_scores_history.append(black_cnt)
        white_scores_history.append(white_cnt)
        steps_history.append(t)
        
        ax_curves.clear()
        ax_curves.plot(steps_history, black_scores_history, color='cyan', label='Black (Random)')
        ax_curves.plot(steps_history, white_scores_history, color='orange', label='White (AI)')
        ax_curves.set_title('Piece Count Comparison')
        ax_curves.legend()
        
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        GIF_FRAMES.append(image[..., :3].copy())
        
        action[0] = action_
        action[1] = 0   # 黑棋 为 0
        observation, reward, done, *rest = env.step(action)
        done = done or (rest[0] if len(rest) > 1 else False)
        
        ################### 白棋 ############################### 1表示白棋
        enables = env.unwrapped.possible_actions
        
        # 提取 AI 的动作和热力图及胜率价值
        action_, heatmap, val = agent.evaluate(observation, enables)
        
        if len(enables) == 0:
            action_ = env.unwrapped.board_size ** 2 + 1 # pass

        render_gui(env.unwrapped.state, t+0.5, heatmap=heatmap)
        
        black_cnt = np.sum(env.unwrapped.state[0, :, :] == 1)
        white_cnt = np.sum(env.unwrapped.state[1, :, :] == 1)
        black_scores_history.append(black_cnt)
        white_scores_history.append(white_cnt)
        steps_history.append(t + 0.5)

        ax_curves.clear()
        ax_curves.plot(steps_history, black_scores_history, color='cyan', label='Black (Random)')
        ax_curves.plot(steps_history, white_scores_history, color='orange', label='White (AI)')
        ax_curves.set_title('Piece Count Comparison')
        ax_curves.legend()
        
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
        GIF_FRAMES.append(image[..., :3].copy())

        action[0] = action_
        action[1] = 1  # 白棋 为 1
        observation, reward, done, *rest = env.step(action)
        done = done or (rest[0] if len(rest) > 1 else False)

        if done: # 游戏 结束
            black_score = len(np.where(env.unwrapped.state[0,:,:]==1)[0])
            
            render_gui(env.unwrapped.state, t+1)
            fig.canvas.draw()
            image = np.frombuffer(fig.canvas.buffer_rgba(), dtype=np.uint8)
            image = image.reshape(fig.canvas.get_width_height()[::-1] + (4,))
            image_rgb = image[..., :3].copy()
            # Stop frames
            for _ in range(10): GIF_FRAMES.append(image_rgb)
            
            plt.savefig(os.path.join(save_dir, "Game_Dashboard.png"))
            gif_path = os.path.join(save_dir, "Game_Animation.gif")
            imageio.mimsave(gif_path, GIF_FRAMES, fps=2)  # Changed from 5 to 2 to slow down playing speed
            
            break

# Mock Training Visualization Output
fig_train, (ax_loss, ax_reward) = plt.subplots(1, 2, figsize=(12, 5))
ax_loss.plot(np.linspace(1, 100, 100), np.exp(-np.linspace(0.01, 3, 100)) + np.random.rand(100)*0.1, color='red')
ax_loss.set_title('Training Loss Curve (Mock)')
ax_loss.set_xlabel('Epochs')
ax_loss.set_ylabel('Loss')

ax_reward.plot(np.linspace(1, 100, 100), np.log(np.linspace(1, 20, 100)) + np.random.rand(100)*0.2, color='green')
ax_reward.set_title('Average Reward Curve (Mock)')
ax_reward.set_xlabel('Epochs')
ax_reward.set_ylabel('Avg Reward')

plt.savefig(os.path.join(save_dir, "Training_Curves.png"))
plt.close('all')
