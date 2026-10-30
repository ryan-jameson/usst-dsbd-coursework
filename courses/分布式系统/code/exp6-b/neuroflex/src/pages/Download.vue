<template>
  <div class="download-page" :class="{ 'pc-layout': isPCDevice }">
    <!-- 返回按钮（H5环境） -->
    <button v-if="!isPCDevice" class="back-button" @click="goBack">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M19 12H5M12 19l-7-7 7-7" />
      </svg>
    </button>

    <!-- PC端布局 -->
    <div v-if="isPCDevice" class="download-container">
      <!-- PC端左侧内容 -->
      <div class="content-section">
        <!-- App 图标和名称 -->
        <div class="app-header">
          <div class="app-icon">
            <img src="/favicon.svg" alt="NeuroFlex">
          </div>
          <div class="app-info">
            <h1 class="app-name">NeuroFlex</h1>
            <p class="app-desc">认知训练系统</p>
          </div>
        </div>

        <!-- 功能特性 -->
        <div class="features">
          <h3>功能特性</h3>
          <div class="features-grid">
            <div class="feature-item">
              <div class="feature-icon">🧠</div>
              <span>科学认知训练</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <span>多维能力提升</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🎯</div>
              <span>个性化训练计划</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📈</div>
              <span>详细数据分析</span>
            </div>
          </div>
        </div>

        <!-- 安装说明 -->
        <div class="install-tips">
          <h3>安装说明</h3>
          <div class="tips-list">
            <div class="tip-item">
              <div class="tip-number">1</div>
              <span>点击下载按钮获取 APK 文件</span>
            </div>
            <div class="tip-item">
              <div class="tip-number">2</div>
              <span>打开下载的文件进行安装</span>
            </div>
            <div class="tip-item">
              <div class="tip-number">3</div>
              <span>如提示风险，请选择「仍要安装」</span>
            </div>
            <div class="tip-item">
              <div class="tip-number">4</div>
              <span>首次使用需授予相关权限</span>
            </div>
          </div>
        </div>
      </div>

      <!-- PC端右侧下载区域 -->
      <div class="download-section">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="spinner" />
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <p>{{ error }}</p>
          <button class="retry-btn" @click="fetchAppInfo">
            重试
          </button>
        </div>

        <!-- 版本信息和下载 -->
        <div v-else class="version-info">
          <div class="version-badge">
            <span class="version-label">最新版本</span>
            <span class="version-number">v{{ appInfo.version }}</span>
          </div>

          <div v-if="appInfo.releaseDate" class="release-date">
            发布于 {{ formatDate(appInfo.releaseDate) }}
          </div>

          <!-- 下载按钮 -->
          <button
            class="download-btn"
            :class="{ 'is-downloading': downloading }"
            :disabled="!appInfo.downloadUrl || downloading"
            @click="handleDownload"
          >
            <svg v-if="!downloading" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <div v-else class="btn-spinner" />
            <span>{{ downloading ? '下载中...' : '下载 APK' }}</span>
          </button>

          <!-- 更新日志 -->
          <div v-if="appInfo.changelog" class="changelog">
            <h3>更新内容</h3>
            <p>{{ appInfo.changelog }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动端布局 -->
    <div v-else class="mobile-container">
      <!-- 移动端头部 -->
      <div class="mobile-header">
        <div class="app-icon-mobile">
          <img src="/favicon.svg" alt="NeuroFlex">
        </div>
        <div class="app-title-section">
          <h1 class="app-name-mobile">NeuroFlex</h1>
          <p class="app-desc-mobile">认知训练系统</p>
        </div>
      </div>

      <!-- 移动端主要内容 -->
      <div class="mobile-content">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state-mobile">
          <div class="spinner" />
          <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state-mobile">
          <p>{{ error }}</p>
          <button class="retry-btn" @click="fetchAppInfo">
            重试
          </button>
        </div>

        <!-- 版本信息和下载 -->
        <div v-else class="version-section-mobile">
          <!-- 版本信息卡片 -->
          <div class="version-card-mobile">
            <div class="version-header-mobile">
              <div class="version-badge-mobile">
                <span class="version-label-mobile">最新版本</span>
                <span class="version-number-mobile">v{{ appInfo.version }}</span>
              </div>
              <div v-if="appInfo.releaseDate" class="release-date-mobile">
                发布于 {{ formatDate(appInfo.releaseDate) }}
              </div>
            </div>
          </div>

          <!-- 功能亮点 -->
          <div class="features-mobile">
            <div class="feature-item-mobile">
              <div class="feature-icon-mobile">🧠</div>
              <span>科学认知训练</span>
            </div>
            <div class="feature-item-mobile">
              <div class="feature-icon-mobile">📊</div>
              <span>多维能力提升</span>
            </div>
            <div class="feature-item-mobile">
              <div class="feature-icon-mobile">🎯</div>
              <span>个性化训练</span>
            </div>
          </div>

          <!-- 下载按钮 -->
          <button
            class="download-btn-mobile"
            :class="{ 'is-downloading': downloading }"
            :disabled="!appInfo.downloadUrl || downloading"
            @click="handleDownload"
          >
            <svg v-if="!downloading" class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="7 10 12 15 17 10" />
              <line x1="12" y1="15" x2="12" y2="3" />
            </svg>
            <div v-else class="btn-spinner" />
            <span>{{ downloading ? '下载中...' : '立即下载' }}</span>
          </button>

          <!-- 更新日志 -->
          <div v-if="appInfo.changelog" class="changelog-mobile">
            <h3>更新内容</h3>
            <p>{{ appInfo.changelog }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { isPC } from '@/utils/device'

const router = useRouter()
const isPCDevice = ref(isPC())

const appInfo = ref({
  version: '',
  versionCode: 0,
  downloadUrl: '',
  changelog: '',
  releaseDate: '',
})
const loading = ref(true)
const downloading = ref(false)
const error = ref(null)

// 检测是否为移动设备
function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

// 返回上一页
function goBack() {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/main/home')
  }
}

// 获取版本信息
async function fetchAppInfo() {
  try {
    const response = await fetch('/app-version.json')
    if (!response.ok)
      throw new Error('获取版本信息失败')
    appInfo.value = await response.json()
  }
  catch (e) {
    error.value = e.message
  }
  finally {
    loading.value = false
  }
}

// 下载 APK
async function handleDownload() {
  if (!appInfo.value.downloadUrl || downloading.value)
    return

  downloading.value = true
  try {
    // 优先使用 CDN 下载链接，如果失败则降级到 GitHub
    let downloadUrl = appInfo.value.downloadUrl
    let githubUrl = appInfo.value.githubUrl || downloadUrl
    
    // 移动端直接使用 window.location.href，不通过 blob
    // 因为移动浏览器不支持通过 JavaScript 触发的 download 属性
    if (isMobileDevice()) {
      // 移动端：先尝试CDN，失败则使用GitHub
      try {
        // 先测试CDN是否可用
        const testResponse = await fetch(downloadUrl, { method: 'HEAD' })
        if (testResponse.ok) {
          window.location.href = downloadUrl
        } else {
          throw new Error('CDN不可用')
        }
      } catch (cdnError) {
        console.warn('CDN下载失败，使用GitHub直链:', cdnError.message)
        window.location.href = githubUrl
      }

      // 延迟重置状态，给浏览器时间处理下载
      setTimeout(() => {
        downloading.value = false
      }, 1000)
      return
    }

    // 桌面端：使用 blob 方式下载（支持自定义文件名）
    let downloadSource = 'CDN'
    
    try {
      // 先尝试CDN下载
      const response = await fetch(downloadUrl)
      if (!response.ok) {
        throw new Error(`CDN响应错误: ${response.status}`)
      }

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `NeuroFlex-v${appInfo.value.version}.apk`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
      
      console.log(`✅ 通过${downloadSource}下载成功`)
      downloading.value = false
    } catch (cdnError) {
      console.warn('CDN下载失败，尝试GitHub直链:', cdnError.message)
      
      try {
        // 降级到GitHub直链
        downloadSource = 'GitHub'
        
        const response = await fetch(githubUrl)
        if (!response.ok) {
          throw new Error(`GitHub响应错误: ${response.status}`)
        }

        const blob = await response.blob()
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `NeuroFlex-v${appInfo.value.version}.apk`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        console.log(`✅ 通过${downloadSource}下载成功`)
        downloading.value = false
      } catch (githubError) {
        console.error('GitHub下载也失败:', githubError.message)
        
        // 最终降级：直接跳转
        console.log('使用浏览器直接下载...')
        window.location.href = githubUrl
        downloading.value = false
      }
    }
  }
  catch (error) {
    console.error('下载过程出错:', error)
    // 最终兜底：直接跳转GitHub下载
    const fallbackUrl = appInfo.value.githubUrl || appInfo.value.downloadUrl
    console.log('使用兜底方案:', fallbackUrl)
    window.location.href = fallbackUrl
    downloading.value = false
  }
}

// 格式化日期
function formatDate(dateStr) {
  if (!dateStr)
    return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

onMounted(() => {
  fetchAppInfo()
})
</script>

<style lang="scss" scoped>
.download-page {
  min-height: 100vh;
  min-height: 100dvh;
  background: $bg-primary;
  position: relative;
  overflow: hidden;

  // PC端布局
  &.pc-layout {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: $spacing-xl;
  }

  // 移动端布局
  &:not(.pc-layout) {
    padding: $spacing-md;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

.back-button {
  position: fixed;
  top: $spacing-lg;
  left: $spacing-lg;
  z-index: 100;
  width: 44px;
  height: 44px;
  border-radius: $radius-full;
  background: $glass-bg;
  backdrop-filter: $glass-backdrop;
  border: 1px solid $glass-border;
  color: $text-primary;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all $transition-base;
  box-shadow: $glass-shadow;

  &:hover {
    background: rgba(255, 255, 255, 0.1);
    transform: translateY(-2px);
  }

  &:active {
    transform: translateY(0);
  }

  svg {
    stroke-width: 2;
  }
}

/* ===== PC端样式 ===== */
.download-container {
  max-width: 1000px;
  width: 100%;
  background: $glass-bg;
  backdrop-filter: $glass-backdrop;
  border: 1px solid $glass-border;
  border-radius: $radius-lg;
  box-shadow: $glass-shadow;
  overflow: hidden;
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 0;
  height: auto;
  max-height: 80vh;
}

.content-section {
  padding: $spacing-2xl;
  overflow-y: auto;
  @include custom-scrollbar;
}

.download-section {
  background: rgba(255, 255, 255, 0.02);
  border-left: 1px solid $glass-border;
  padding: $spacing-2xl;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.app-header {
  margin-bottom: $spacing-xl;
  text-align: left;
  display: flex;
  align-items: center;
  gap: $spacing-lg;
}

.app-icon {
  width: 96px;
  height: 96px;
  margin: 0;
  flex-shrink: 0;
  border-radius: $radius-lg;
  overflow: hidden;
  background: $glass-bg;
  border: 1px solid $glass-border;
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 80px;
    height: 80px;
    object-fit: cover;
  }
}

.app-info {
  flex: 1;
  min-width: 0;
}

.app-name {
  font-size: $font-3xl;
  font-weight: $font-bold;
  color: $text-primary;
  margin-bottom: $spacing-sm;
  background: linear-gradient(135deg, $accent-primary, $accent-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-desc {
  font-size: $font-lg;
  color: $text-secondary;
  margin: 0;
}

/* ===== 移动端样式 ===== */
.mobile-container {
  max-width: 400px;
  width: 100%;
  height: calc(100vh - #{$spacing-lg});
  height: calc(100dvh - #{$spacing-lg});
  background: $glass-bg;
  backdrop-filter: $glass-backdrop;
  border: 1px solid $glass-border;
  border-radius: $radius-lg;
  box-shadow: $glass-shadow;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.mobile-header {
  text-align: center;
  padding: $spacing-xl $spacing-lg $spacing-lg;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(102, 126, 234, 0.05) 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-lg;
  flex-shrink: 0;
  
  // 限制最大高度，避免在长屏手机上占用过多空间
  max-height: 220px;
  
  // 在超长屏幕上进一步压缩
  @media (min-height: 800px) {
    padding: $spacing-lg $spacing-lg $spacing-md;
    gap: $spacing-md;
    max-height: 180px;
  }
  
  // 在非常长的屏幕上使用最小间距
  @media (min-height: 900px) {
    padding: $spacing-md $spacing-lg $spacing-sm;
    gap: $spacing-sm;
    max-height: 160px;
  }
}

.app-icon-mobile {
  width: 64px;
  height: 64px;
  border-radius: $radius-md;
  overflow: hidden;
  background: $glass-bg;
  border: 1px solid $glass-border;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.2);

  img {
    width: 48px;
    height: 48px;
    object-fit: cover;
  }
  
  // 在长屏手机上进一步缩小
  @media (min-height: 800px) {
    width: 56px;
    height: 56px;
    
    img {
      width: 40px;
      height: 40px;
    }
  }
  
  @media (min-height: 900px) {
    width: 48px;
    height: 48px;
    
    img {
      width: 36px;
      height: 36px;
    }
  }
}

.app-title-section {
  text-align: center;
}

.app-name-mobile {
  font-size: $font-lg;
  font-weight: $font-bold;
  color: $text-primary;
  margin: 0 0 $spacing-xs 0;
  background: linear-gradient(135deg, $accent-primary, $accent-secondary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.app-desc-mobile {
  font-size: $font-sm;
  color: $text-secondary;
  margin: 0;
}

.mobile-content {
  flex: 1;
  padding: $spacing-md $spacing-lg;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  overflow-y: auto;
  @include custom-scrollbar;
  min-height: 0;
}

.version-section-mobile {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.version-card-mobile {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid $glass-border;
  border-radius: $radius-md;
  padding: $spacing-md;
  text-align: center;
}

.version-header-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
}

.version-badge-mobile {
  display: inline-flex;
  align-items: center;
  gap: $spacing-xs;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(102, 126, 234, 0.1));
  border: 1px solid rgba(0, 212, 255, 0.2);
  padding: $spacing-xs $spacing-md;
  border-radius: $radius-full;
}

.version-label-mobile {
  font-size: $font-xs;
  color: $text-secondary;
}

.version-number-mobile {
  font-size: $font-sm;
  font-weight: $font-bold;
  color: $accent-primary;
}

.release-date-mobile {
  font-size: $font-xs;
  color: $text-tertiary;
}

.features-mobile {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: $spacing-xs;
}

.feature-item-mobile {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid $glass-border;
  border-radius: $radius-sm;
  padding: $spacing-sm;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: $spacing-xs;
  text-align: center;
  transition: all $transition-base;

  &:hover {
    background: rgba(255, 255, 255, 0.05);
    border-color: rgba(0, 212, 255, 0.3);
    transform: translateY(-1px);
  }

  .feature-icon-mobile {
    font-size: $font-base;
  }

  span {
    font-size: 10px;
    color: $text-secondary;
    line-height: 1.2;
  }
}

.download-btn-mobile {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-xs;
  width: 100%;
  padding: $spacing-md $spacing-lg;
  background: linear-gradient(135deg, $accent-primary, $accent-secondary);
  color: white;
  border: none;
  border-radius: $radius-md;
  cursor: pointer;
  transition: all $transition-base;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.4);
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.5);

    &::before {
      left: 100%;
    }
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.is-downloading {
    background: linear-gradient(135deg, $accent-secondary, $accent-primary);
  }

  .icon {
    width: 18px;
    height: 18px;
  }

  span {
    font-size: $font-base;
    font-weight: $font-bold;
  }
}

.changelog-mobile {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid $glass-border;
  border-radius: $radius-md;
  padding: $spacing-md;
  text-align: left;

  h3 {
    font-size: $font-sm;
    font-weight: $font-semibold;
    color: $text-primary;
    margin: 0 0 $spacing-xs 0;
  }

  p {
    font-size: $font-xs;
    color: $text-secondary;
    line-height: 1.4;
    margin: 0;
    white-space: pre-line;
  }
}

/* ===== 共用样式 ===== */
.loading-state,
.error-state,
.loading-state-mobile,
.error-state-mobile {
  text-align: center;
  padding: $spacing-xl 0;
  color: $text-secondary;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.spinner,
.btn-spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: $accent-primary;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto $spacing-md;
}

.btn-spinner {
  width: 20px;
  height: 20px;
  border-width: 2px;
  margin: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.retry-btn {
  margin-top: $spacing-md;
  padding: $spacing-sm $spacing-lg;
  background: $glass-bg;
  color: $accent-primary;
  border: 1px solid $accent-primary;
  border-radius: $radius-md;
  font-size: $font-sm;
  cursor: pointer;
  transition: all $transition-base;

  &:hover {
    background: rgba(0, 212, 255, 0.1);
  }
}

.version-info {
  text-align: center;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  gap: $spacing-sm;
  background: $glass-bg;
  border: 1px solid $glass-border;
  padding: $spacing-sm $spacing-md;
  border-radius: $radius-full;
  margin-bottom: $spacing-sm;
}

.version-label {
  font-size: $font-sm;
  color: $text-secondary;
}

.version-number {
  font-size: $font-sm;
  font-weight: $font-semibold;
  color: $accent-primary;
}

.release-date {
  font-size: $font-sm;
  color: $text-tertiary;
  margin-bottom: $spacing-lg;
}

.download-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  width: 100%;
  padding: $spacing-md $spacing-lg;
  background: linear-gradient(135deg, $accent-primary, $accent-secondary);
  color: white;
  border: none;
  border-radius: $radius-md;
  font-size: $font-base;
  font-weight: $font-semibold;
  cursor: pointer;
  transition: all $transition-base;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);

  .icon {
    width: 20px;
    height: 20px;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
  }

  &:active:not(:disabled) {
    transform: translateY(0);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &.is-downloading {
    background: linear-gradient(135deg, $accent-secondary, $accent-primary);
  }
}

.changelog {
  margin-top: $spacing-lg;
  padding: $spacing-md;
  background: $glass-bg;
  border: 1px solid $glass-border;
  border-radius: $radius-md;
  text-align: left;

  h3 {
    font-size: $font-base;
    font-weight: $font-semibold;
    color: $text-primary;
    margin: 0 0 $spacing-sm 0;
  }

  p {
    font-size: $font-sm;
    color: $text-secondary;
    line-height: 1.5;
    margin: 0;
    white-space: pre-line;
  }
}

.features {
  margin-top: $spacing-xl;
  padding-top: $spacing-lg;
  border-top: 1px solid $glass-border;

  h3 {
    font-size: $font-xl;
    font-weight: $font-semibold;
    color: $text-primary;
    margin: 0 0 $spacing-lg 0;
    text-align: left;
  }
}

.features-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: $spacing-lg;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: $spacing-md;
  padding: $spacing-md;
  background: $glass-bg;
  border: 1px solid $glass-border;
  border-radius: $radius-sm;
  font-size: $font-base;
  color: $text-secondary;

  .feature-icon {
    font-size: $font-xl;
    flex-shrink: 0;
  }
}

.install-tips {
  margin-top: $spacing-xl;
  padding-top: $spacing-lg;
  border-top: 1px solid $glass-border;

  h3 {
    font-size: $font-xl;
    font-weight: $font-semibold;
    color: $text-primary;
    margin: 0 0 $spacing-lg 0;
    text-align: left;
  }
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: $spacing-md;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: $spacing-md;
  font-size: $font-sm;
  color: $text-secondary;
  line-height: 1.5;

  .tip-number {
    width: 24px;
    height: 24px;
    background: linear-gradient(135deg, $accent-primary, $accent-secondary);
    color: white;
    border-radius: 50%;
    font-size: $font-xs;
    font-weight: $font-semibold;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }
}

// 响应式调整
@media (max-width: $breakpoint-sm) {
  .download-page:not(.pc-layout) {
    padding: $spacing-sm;
  }

  .mobile-container {
    padding: $spacing-md;
  }
}
</style>