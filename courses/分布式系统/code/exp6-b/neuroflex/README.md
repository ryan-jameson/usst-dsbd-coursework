<div align="center">

# 🧠 NeuroFlex

**科学认知训练系统 | Scientific Cognitive Training System**

[![Vue3](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-5.4-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![PWA](https://img.shields.io/badge/PWA-Ready-FF6B6B?logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于神经科学研究的专业认知训练平台，通过7种科学训练模块全面提升注意力、记忆力和认知控制能力

[在线体验](https://neuroflex.061129.xyz) · [功能介绍](#-训练模块) · [快速开始](#-快速开始)

</div>

---

## ✨ 核心特性

- 🎯 **7种科学训练** - 涵盖注意力、记忆力、认知控制等多维度训练
- 📱 **PWA 应用** - 支持离线使用，可安装到桌面和手机主屏幕
- 🎨 **现代化UI** - 玻璃拟态风格，神经网络主题设计，流畅动画
- 📊 **数据追踪** - 本地存储训练记录，可视化进步曲线
- ⚡ **极致性能** - Vite构建，秒级启动，丝滑交互
- 🔒 **隐私优先** - 所有数据本地存储，无需注册登录
- 🎭 **个性化** - 自定义头像，NeuroFlex logo 默认头像
- 📈 **数据分析** - 集成 Umami 分析，了解使用情况

---

## 🎮 训练模块

### 1. 舒尔特方格 (Schulte Grid)
**提升视觉搜索速度和注意力广度**

- 支持 3×3 至 9×9 多种难度
- 实时计时和标准时间对比
- 准确率统计和反应速度分析

### 2. Stroop 色词干扰 (Stroop Test)
**增强认知控制和抗干扰能力**

- 9种颜色选择（红、蓝、绿、黄、紫、橙、粉、白、黑）
- **标准模式** - 测试纯反应速度
- **限时模式** - 每个字3秒倒计时，增加挑战性
- 详细统计：平均/最快/最慢反应时间、超时次数

### 3. 序列记忆 (Sequence Memory)
**提高工作记忆容量**

- 递增难度的数字序列
- 视觉记忆强化训练
- 短期记忆容量测试

### 4. 听觉选择性注意 (Auditory Attention)
**增强抗干扰能力和听觉信息识别**

- 数字语音播报 + 背景噪音干扰
- 3种难度等级（简单/中等/困难）
- 支持6/8/9位数字记忆
- 实时输入进度提示

### 5. 镜像协调 (Mirror Coordination)
**提升左右脑配合和运动协调**

- 左侧绘制，右侧自动镜像显示
- 4种训练模式（睁眼/闭眼/快速/复杂）
- 多种模板选择（自由/圆形/方形/波浪）
- 实时镜像反馈

### 6. 规则分类 (Rule-based Categorization)
**优化逻辑思维和快速决策**

- 单维度/双维度分类规则
- 规则切换训练
- 认知灵活性提升

### 7. 情景记忆 (Episodic Memory)
**增强记忆联想和语义整合**

- 故事情节记忆
- 语义关联训练
- 情景重构能力

---

## 🚀 快速开始

### 环境要求

```bash
Node.js >= 18.0.0
pnpm >= 8.0.0
```

### 安装运行

```bash
# 克隆项目
git clone https://github.com/IT-NuanxinPro/NeuroFlex.git
cd neuroflex

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build

# 预览生产构建
pnpm preview
```

---

## 🛠️ 技术栈

### 核心技术
- **Vue 3.5** - 组合式API，响应式系统
- **Vite 5.4** - 极速构建工具
- **Vue Router 4** - 路由管理
- **Pinia** - 状态管理
- **PWA** - 渐进式Web应用，支持离线使用

### UI & 样式
- **SCSS** - CSS预处理器，模块化样式
- **Glassmorphism** - 玻璃拟态设计
- **神经网络主题** - 专业的认知训练视觉设计
- **响应式设计** - 移动端优先

### 工具链
- **ESLint** - 代码质量
- **Prettier** - 代码格式化
- **PostCSS** - CSS后处理
- **Umami Analytics** - 隐私友好的网站分析

---

## 📁 项目结构

```
neuroflex/
├── src/
│   ├── components/          # 公共组件
│   │   ├── ButtonGroupSelect.vue
│   │   ├── Modal.vue
│   │   ├── NeuroFlexLogo.vue    # NeuroFlex Logo 组件
│   │   └── UserAvatar.vue       # 用户头像组件
│   ├── layouts/            # 布局组件
│   │   └── TabLayout.vue
│   ├── pages/              # 页面组件
│   │   ├── games/         # 训练模块
│   │   │   ├── Schulte.vue      # 舒尔特方格
│   │   │   ├── Stroop.vue       # Stroop训练
│   │   │   ├── Sequence.vue     # 序列记忆
│   │   │   ├── Audio.vue        # 听觉注意
│   │   │   ├── Mirror.vue       # 镜像协调
│   │   │   ├── Categorize.vue   # 规则分类
│   │   │   └── MemoryStory.vue  # 情景记忆
│   │   ├── Home.vue        # 首页
│   │   ├── Record.vue      # 训练记录
│   │   ├── Profile.vue     # 个人中心
│   │   └── Settings.vue    # 设置
│   ├── router/             # 路由配置
│   ├── stores/             # 状态管理
│   │   ├── config.js
│   │   ├── training.js
│   │   └── user.js
│   ├── styles/             # 全局样式
│   │   ├── variables.scss  # 变量定义
│   │   ├── mixins.scss     # 混入函数
│   │   └── global.scss     # 全局样式
│   ├── utils/              # 工具函数
│   │   ├── animations.js
│   │   └── storage.js
│   ├── App.vue
│   └── main.js
├── public/                 # 静态资源
│   ├── favicon.svg         # SVG 图标
│   ├── manifest.json       # PWA 配置
│   └── icons-readme.md     # 图标说明
├── scripts/               # 工具脚本
│   └── generate-icons.html # 图标生成器
├── .github/               # GitHub配置
│   └── workflows/         # CI/CD
├── vite.config.js         # Vite配置
├── package.json
└── README.md
```

---

## 🎨 设计特色

### 神经网络主题设计
- **NeuroFlex Logo** - 三层神经网络节点设计，象征认知训练过程
- **品牌色彩** - 青色 (#00d4ff) 到紫色 (#7b2cbf) 渐变
- **脉冲效果** - 动态神经信号传递视觉效果
- **专业视觉** - 符合认知科学主题的现代化设计

### 玻璃拟态风格
- 半透明背景 + 毛玻璃模糊
- 精致光影效果
- 渐变色彩搭配
- 现代化视觉体验

### 流畅动画
- 页面切换动画（slide/fade）
- 交互反馈动画
- 加载状态动画
- 60fps流畅体验

### 响应式设计
- **移动端优先** - 完美适配手机和平板
- **PC端优化** - 充分利用大屏幕空间
- **自适应布局** - 智能调整元素大小

### PWA 特性
- **离线使用** - 支持无网络环境下训练
- **桌面安装** - 可安装到设备主屏幕
- **原生体验** - 接近原生应用的使用体验

---

## 📊 数据管理

### 本地存储
所有数据存储在浏览器 LocalStorage，包括：
- 用户配置（用户名、头像、偏好设置）
- 训练记录（每次训练的详细数据）
- 统计信息（总训练次数、时长、平均分数）

### 数据结构
```javascript
{
  profile: {
    id: "uuid",
    name: "训练者",
    avatar: "base64...",
    createdAt: "2024-01-18T20:00:00"
  },
  trainingHistory: [
    {
      id: "uuid",
      moduleName: "schulte",
      difficulty: "5x5",
      score: 85,
      duration: 26000,
      accuracy: 1.0,
      completedAt: "2024-01-18T20:00:00",
      details: { /* 模块特定数据 */ }
    }
  ],
  preferences: {
    theme: "dark",
    soundEnabled: true,
    vibrationEnabled: true
  }
}
```

---

## 🚀 部署

### 自动部署 (推荐)

项目配置了 GitHub Actions 自动部署到 Cloudflare Pages：

1. Fork 本项目到你的 GitHub
2. 在 Cloudflare Pages 连接 GitHub 仓库
3. 每次推送到 `main` 分支自动触发部署
4. 支持预览部署（Pull Request）

### 手动部署

#### Cloudflare Pages

1. Fork 本项目
2. 在 Cloudflare Pages 创建新项目
3. 连接 GitHub 仓库
4. 构建配置：
   - 构建命令：`pnpm build`
   - 输出目录：`dist`
5. 部署完成

#### Vercel / Netlify

```bash
# 构建
pnpm build

# Vercel
vercel --prod

# Netlify
netlify deploy --prod --dir=dist
```

### PWA 部署注意事项

- 确保 HTTPS 部署（PWA 要求）
- 配置正确的 `manifest.json`
- 设置合适的缓存策略
- 测试离线功能

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 开发流程
1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

### 代码规范
- 遵循 ESLint 和 Prettier 配置
- 组件命名使用 PascalCase
- 文件命名使用 kebab-case
- 提交信息遵循 Conventional Commits

---

## 📝 开发计划

### 近期计划
- [x] PWA 支持和离线功能
- [x] NeuroFlex 品牌设计和 Logo
- [x] 用户头像系统
- [x] 数据分析集成
- [ ] 云端数据同步
- [ ] 训练计划定制
- [ ] 成就系统
- [ ] 多语言支持（英文）

### 长期规划
- [ ] AI 个性化训练推荐
- [ ] 训练数据可视化分析
- [ ] 社区排行榜
- [ ] 更多训练模块
- [ ] VR/AR 训练模式

---

## � 致谢

- [Vue.js](https://vuejs.org/) - 渐进式JavaScript框架
- [Vite](https://vitejs.dev/) - 下一代前端构建工具
- [Cloudflare Pages](https://pages.cloudflare.com/) - 全球CDN部署
- [Umami Analytics](https://umami.is/) - 隐私友好的网站分析
- [PWA](https://web.dev/progressive-web-apps/) - 渐进式Web应用技术

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐️ 支持一下！**

Made with ❤️ by [Your Name]

</div>
