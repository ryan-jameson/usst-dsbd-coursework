# 数学建模课堂练习实验项目

本项目包含 3 个完整、可从头到尾运行的 Jupyter Notebook，均使用 Python 完成，不依赖外部数据文件。

## 目录说明

- `notebooks/01_team_selection_planning_model.ipynb`  
  任务一：组队选择规划模型。使用 0-1 规划思想，从候选队员中选择综合能力较优、预算和时间满足约束的参赛团队。

- `notebooks/02_pest_control_equation_model.ipynb`  
  任务二：害虫防治方程模型。建立害虫与天敌相互作用的微分方程，比较不同防治策略下害虫数量变化。

- `notebooks/03_comment_recognition_bayes_model.ipynb`  
  任务三：评论识别贝叶斯模型。使用朴素贝叶斯方法，对中文短评论进行正向/负向情感识别。

- `outputs/`  
  Notebook 运行后保存图表结果的目录。

## 建议运行顺序

建议按编号依次运行：

1. `01_team_selection_planning_model.ipynb`
2. `02_pest_control_equation_model.ipynb`
3. `03_comment_recognition_bayes_model.ipynb`

三个 Notebook 互相独立，也可以单独运行。

## 依赖库

建议 Python 版本为 3.9 及以上。主要依赖如下：

```bash
pip install numpy pandas matplotlib scipy
```

其中：

- 任务一使用 `scipy.optimize.milp` 求解 0-1 线性规划；若本机 SciPy 版本较旧，Notebook 内置了枚举法备用求解。
- 任务二使用 `scipy.integrate.solve_ivp` 求解微分方程。
- 任务三手写朴素贝叶斯分类器，不依赖外部机器学习库。

