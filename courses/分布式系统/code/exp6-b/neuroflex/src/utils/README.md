# 前端工具模块

本目录包含 NeuroFlex 前端应用的核心工具模块。

## 模块说明

### � storage.js - 本地存储管理器
使用 localStorage 进行数据持久化，支持移动端。

**主要功能:**
- 训练记录本地存储
- 数据过滤和查询
- 同步状态管理
- 存储空间优化
- 数据导入导出

**使用示例:**
```javascript
import storageManager from '@/utils/storage.js';

// 保存训练记录
const recordId = storageManager.saveTrainingRecord({
  moduleName: 'schulte',
  difficulty: 'easy',
  score: 85,
  accuracy: 0.95,
  duration: 120000,
  completedAt: new Date().toISOString(),
  details: {}
});

// 获取未同步记录
const unsyncedRecords = storageManager.getUnsyncedRecords();

// 标记记录为已同步
storageManager.markRecordSynced(recordId);
```

## 服务层

### 🔑 supabaseAuthService.js - 认证服务
使用 Supabase 内置认证的统一服务接口。

**主要功能:**
- 用户注册和登录
- 邮箱验证和密码重置
- 本地数据同步
- 训练记录上传
- 排行榜数据获取
- 用户信息管理

**使用示例:**
```javascript
import supabaseAuthService from '@/services/supabaseAuthService.js';

// 初始化服务
await supabaseAuthService.initialize();

// 用户注册
const result = await supabaseAuthService.register(email, password, nickname);

// 用户登录
const loginResult = await supabaseAuthService.login(email, password);

// 检查登录状态
const isLoggedIn = supabaseAuthService.isLoggedIn();

// 同步本地数据
const syncResult = await supabaseAuthService.syncLocalData();

// 用户登出
await supabaseAuthService.logout();
```

### 🎯 useAuth.js - Vue 组合式函数
为 Vue 组件提供认证功能的响应式接口。

**使用示例:**
```javascript
import { useAuth } from '@/composables/useAuth.js';

const { 
  user, 
  isLoggedIn, 
  isLoading, 
  login, 
  logout, 
  initialize 
} = useAuth();

// 在组件中使用
await initialize();
await login(email, password);
```

## 数据流程

### 注册流程
```
用户输入 → 数据验证 → Supabase 注册 → 邮箱验证 → 创建用户资料
```

### 登录流程
```
用户输入 → 数据验证 → Supabase 登录 → 获取会话 → 检查本地数据同步
```

### 数据同步流程
```
检测未同步记录 → 用户确认 → 批量上传 → 标记已同步 → 更新本地状态
```

## 安全特性

### Supabase 内置安全
- HTTPS 加密传输
- bcrypt 密码哈希
- JWT 会话管理
- Row Level Security (RLS)
- 自动会话刷新

### 本地数据保护
- 同步状态追踪
- 数据完整性验证
- 自动清理机制

## 性能优化

### 存储优化
- 记录数量限制（1000条）
- 自动清理旧数据
- 压缩存储格式

### 网络优化
- 批量数据上传
- 智能重试机制
- 离线状态处理

## 事件系统

### 自定义事件

#### authStateChanged
认证状态变化时触发
```javascript
window.addEventListener('authStateChanged', (event) => {
  console.log('Auth state changed:', event.detail);
  // 处理认证状态变化
});
```

#### localDataFound
发现本地未同步数据时触发
```javascript
window.addEventListener('localDataFound', (event) => {
  console.log('Found unsynced records:', event.detail.count);
  // 显示同步提示
});
```

## 配置选项

### 存储配置
```javascript
// 最大记录数量
const maxRecords = 1000;

// 数据清理周期（天）
const cleanupDays = 90;

// 存储前缀
const storagePrefix = 'neuroflex_';
```

### Supabase 配置
```env
# 环境变量
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

## 调试工具

### 存储调试
```javascript
// 获取存储统计
const stats = storageManager.getStorageStats();
console.log('Storage stats:', stats);

// 导出所有数据
const exportData = storageManager.exportData();
console.log('Exported data:', exportData);
```

### 认证调试
```javascript
// 获取认证状态
const authStatus = supabaseAuthService.getAuthStatus();
console.log('Auth status:', authStatus);

// 获取当前会话
const session = await supabaseAuthService.getSession();
console.log('Current session:', session);
```

## 最佳实践

### 初始化
```javascript
// 在应用启动时初始化认证服务
import { initializeAuth } from '@/composables/useAuth.js';

async function initializeApp() {
  try {
    await initializeAuth();
    console.log('Auth service initialized');
  } catch (error) {
    console.error('Failed to initialize auth service:', error);
  }
}
```

### 错误处理
```javascript
// 统一错误处理
try {
  const result = await supabaseAuthService.login(email, password);
  // 处理成功结果
} catch (error) {
  // 显示用户友好的错误消息
  showErrorMessage(error.message);
}
```

### 数据同步
```javascript
// 在登录后检查数据同步
supabaseAuthService.login(email, password).then(() => {
  // 监听本地数据发现事件
  window.addEventListener('localDataFound', async (event) => {
    const shouldSync = await confirmSync(event.detail.count);
    if (shouldSync) {
      await supabaseAuthService.syncLocalData();
    }
  });
});
```

## 依赖关系

```
useAuth (Vue 组合式函数)
└── supabaseAuthService (认证服务)
    ├── @supabase/supabase-js (Supabase 客户端)
    └── storageManager (本地存储)
```

## 更新日志

### v2.0.0 (2024-01-01)
- 简化架构，使用 Supabase 内置认证
- 移除 RSA 加密和 Cloudflare Worker 依赖
- 添加 Vue 组合式函数支持
- 优化本地存储管理