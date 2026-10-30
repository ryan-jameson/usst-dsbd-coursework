# 📁 NeuroFlex APK 项目结构

## 🏗️ 完整项目结构

```
neuroflex/
├── 📱 APK 构建相关
│   ├── capacitor.config.js          # Capacitor 主配置文件
│   ├── android/                     # Android 原生项目 (自动生成)
│   │   ├── app/
│   │   │   ├── src/main/
│   │   │   │   ├── AndroidManifest.xml
│   │   │   │   ├── res/             # Android 资源文件
│   │   │   │   └── assets/          # Web 资源 (自动同步)
│   │   │   └── build.gradle         # 应用级构建配置
│   │   ├── gradle/                  # Gradle 包装器
│   │   ├── build.gradle             # 项目级构建配置
│   │   └── gradlew                  # Gradle 执行脚本
│   └── scripts/
│       └── build-apk.js             # 自动化构建脚本
│
├── 🌐 Web 应用核心
│   ├── src/
│   │   ├── main.js                  # 应用入口 (已集成APK适配)
│   │   ├── App.vue                  # 根组件 (已优化视口高度)
│   │   ├── components/
│   │   │   ├── GameResult.vue       # 游戏结果组件 (已优化移动端)
│   │   │   ├── Modal.vue            # 模态框组件 (已优化移动端)
│   │   │   ├── MobileTestPage.vue   # 移动端测试页面
│   │   │   └── APKTestPage.vue      # APK 环境测试页面
│   │   ├── utils/
│   │   │   ├── viewport.js          # 视口高度修复工具
│   │   │   └── apk-adapter.js       # APK 环境适配工具
│   │   └── styles/
│   │       ├── variables.scss       # 样式变量 (已添加视口高度)
│   │       ├── mixins.scss          # 样式混入 (已添加移动端适配)
│   │       ├── global.scss          # 全局样式 (已优化移动端)
│   │       └── mobile.scss          # 移动端专用样式 (新增)
│   ├── public/
│   │   ├── manifest.json            # PWA 清单文件
│   │   ├── icon-192.png             # 应用图标 (192x192)
│   │   ├── icon-512.png             # 应用图标 (512x512)
│   │   └── apple-touch-icon.png     # iOS 图标
│   └── index.html                   # HTML 入口 (已优化视口)
│
├── 📋 配置文件
│   ├── package.json                 # 项目依赖 (已添加 Capacitor)
│   ├── vite.config.js               # Vite 构建配置
│   ├── .eslintrc.cjs                # ESLint 配置
│   └── .prettierrc.json             # Prettier 配置
│
├── 📚 文档
│   ├── APK_READINESS_ASSESSMENT.md  # APK 准备评估报告
│   ├── APK_BUILD_GUIDE.md           # 详细构建指南
│   ├── QUICK_START_APK.md           # 快速开始指南
│   ├── SAFE_AREA_TEST_CHECKLIST.md # 安全区域测试清单
│   ├── APK_PROJECT_STRUCTURE.md    # 项目结构说明 (本文件)
│   └── MOBILE_OPTIMIZATION.md      # 移动端优化说明
│
└── 🔧 构建输出
    ├── dist/                        # Web 构建输出
    └── android/app/build/outputs/apk/ # APK 输出目录
```

## 🔄 构建流程图

```mermaid
graph TD
    A[源代码] --> B[npm run build]
    B --> C[Web 构建 (dist/)]
    C --> D[npx cap sync]
    D --> E[同步到 Android 项目]
    E --> F[./gradlew assembleDebug]
    F --> G[生成 APK]
    G --> H[android/app/build/outputs/apk/]
    
    I[capacitor.config.js] --> D
    J[Android 资源] --> F
    K[签名配置] --> F
```

## 📱 APK 特定文件说明

### 核心配置文件

#### `capacitor.config.js`
```javascript
// Capacitor 主配置文件
// 定义应用ID、名称、插件配置等
// 控制状态栏、启动画面、键盘行为
```

#### `scripts/build-apk.js`
```javascript
// 自动化构建脚本
// 检查环境、构建Web应用、同步Capacitor、生成APK
// 支持调试和发布版本构建
```

### 适配工具

#### `src/utils/apk-adapter.js`
```javascript
// APK 环境检测和适配
// 设备信息获取、状态栏控制、触觉反馈
// 安全区域动态检测、性能优化
```

#### `src/utils/viewport.js`
```javascript
// 视口高度修复工具
// 解决移动端浏览器地址栏问题
// 支持 iOS Safari、Android Chrome、微信浏览器
```

### 样式适配

#### `src/styles/mobile.scss`
```scss
// 移动端专用样式
// APK 安全区域适配、刘海屏支持
// 触摸优化、性能优化类
```

#### 安全区域适配类
```scss
.apk-safe-area          // APK 基础安全区域
.notch-adaptation       // 刘海屏适配
.landscape-safe-area    // 横屏安全区域
.game-safe-area         // 游戏模式安全区域
.mobile-button-group    // 移动端按钮组
```

## 🛠️ 开发工作流

### 1. 日常开发
```bash
npm run dev              # Web 开发服务器
npm run android:dev      # Android 实时预览
```

### 2. 测试构建
```bash
npm run build           # 构建 Web 应用
npm run cap:sync        # 同步到 Android
npm run cap:run:android # 运行 Android 应用
```

### 3. 发布构建
```bash
npm run build:apk       # 自动化 APK 构建
# 或
npm run android:build   # 手动构建流程
```

## 📦 依赖关系

### 核心依赖
```json
{
  "dependencies": {
    "vue": "^3.4.0",           // Vue.js 框架
    "vue-router": "^4.2.5",    // 路由管理
    "pinia": "^2.1.7",         // 状态管理
    "gsap": "^3.12.5",         // 动画库
    "vant": "^4.9.22"          // UI 组件库
  },
  "devDependencies": {
    "@capacitor/cli": "^6.0.0",        // Capacitor CLI
    "@capacitor/core": "^6.0.0",       // Capacitor 核心
    "@capacitor/android": "^6.0.0",    // Android 平台
    "@capacitor/status-bar": "^6.0.0", // 状态栏插件
    "@capacitor/splash-screen": "^6.0.0", // 启动画面插件
    "vite": "^5.0.0",                  // 构建工具
    "vite-plugin-pwa": "^0.19.0"       // PWA 插件
  }
}
```

### 插件生态
```
Capacitor 插件:
├── @capacitor/status-bar      # 状态栏控制
├── @capacitor/splash-screen   # 启动画面
├── @capacitor/keyboard        # 键盘管理
├── @capacitor/device          # 设备信息
├── @capacitor/haptics         # 触觉反馈
└── @capacitor/screen-orientation # 屏幕方向
```

## 🎯 关键集成点

### 1. 应用启动流程
```
index.html → main.js → App.vue
     ↓
initViewportFix()    # 视口修复
     ↓
initAPKAdapter()     # APK 适配
     ↓
Vue 应用挂载
```

### 2. 安全区域适配流程
```
CSS 环境变量 → SCSS 变量 → 组件样式
     ↓              ↓         ↓
env(safe-area-*) → mixins → .apk-safe-area
```

### 3. 构建同步流程
```
Web 构建 (dist/) → Capacitor 同步 → Android 项目
     ↓                    ↓              ↓
  HTML/CSS/JS → android/app/src/main/assets/ → APK
```

## 🔍 调试和测试

### 开发调试
- **Web 调试**: Chrome DevTools
- **Android 调试**: chrome://inspect
- **原生调试**: Android Studio
- **网络调试**: Capacitor DevTools

### 测试页面
- **MobileTestPage.vue**: 移动端适配测试
- **APKTestPage.vue**: APK 环境功能测试
- **各游戏页面**: 实际使用场景测试

### 测试设备
- **模拟器**: Android Studio AVD
- **真实设备**: 各种 Android 设备
- **特殊屏幕**: 刘海屏、挖孔屏、瀑布屏

## 📊 性能监控

### 构建性能
- **Web 构建时间**: Vite 构建统计
- **APK 大小**: 构建脚本自动显示
- **启动时间**: Android Studio 性能分析

### 运行时性能
- **内存使用**: APKTestPage 实时监控
- **渲染性能**: Chrome DevTools 性能面板
- **网络请求**: Capacitor 网络插件

## 🚀 部署策略

### 开发环境
```bash
npm run android:dev     # 开发版本，支持热重载
```

### 测试环境
```bash
npm run build:apk       # 调试版本，包含调试信息
```

### 生产环境
```bash
BUILD_TYPE=release npm run build:apk  # 发布版本，已签名优化
```

## 📈 版本管理

### 版本号同步
- `package.json` version
- `capacitor.config.js` 配置
- `android/app/build.gradle` versionName/versionCode

### 更新流程
1. 更新 Web 应用代码
2. 运行 `npm run build:apk`
3. 测试 APK 功能
4. 发布到应用商店

---

## 🎯 总结

这个项目结构提供了：
- ✅ **完整的 APK 构建能力**
- ✅ **全面的安全区域适配**
- ✅ **自动化的构建流程**
- ✅ **丰富的测试工具**
- ✅ **详细的文档支持**

**现在你可以轻松地将 NeuroFlex Web 应用打包成原生 Android APK！** 📱🚀