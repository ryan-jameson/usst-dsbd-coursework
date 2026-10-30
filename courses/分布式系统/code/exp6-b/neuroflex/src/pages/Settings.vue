<template>
  <div class="settings-page">
    <header class="page-header">
      <button class="back-button" @click="goBack">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="page-title">设置</h1>
      <div class="header-spacer"></div>
    </header>

    <main class="page-content">
      <div class="settings-section">
        <h2 class="section-title">通用设置</h2>

        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">声音效果</div>
            <div class="setting-description">训练过程中的音效反馈</div>
          </div>
          <label class="toggle-switch">
            <input
              v-model="configStore.appConfig.soundEnabled"
              type="checkbox"
              @change="saveConfig"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">震动反馈</div>
            <div class="setting-description">触觉反馈（需设备支持）</div>
          </div>
          <label class="toggle-switch">
            <input
              v-model="configStore.appConfig.vibrationEnabled"
              type="checkbox"
              @change="saveConfig"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>

        <div class="setting-item">
          <div class="setting-info">
            <div class="setting-label">动画效果</div>
            <div class="setting-description">页面切换和交互动画</div>
          </div>
          <label class="toggle-switch">
            <input
              v-model="configStore.appConfig.animationEnabled"
              type="checkbox"
              @change="saveConfig"
            />
            <span class="toggle-slider"></span>
          </label>
        </div>
      </div>

      <div class="settings-section">
        <h2 class="section-title">隐私与权限</h2>

        <button class="action-button info" @click="showPrivacyDialog">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" />
            <path d="M9 12l2 2 4-4" />
          </svg>
          查看隐私协议
        </button>

        <button class="action-button info" @click="checkPermissions">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
            <circle cx="12" cy="16" r="1" />
            <path d="M7 11V7a5 5 0 0 1 10 0v4" />
          </svg>
          权限管理
        </button>
      </div>

      <div class="settings-section">
        <h2 class="section-title">数据管理</h2>

        <button class="action-button" @click="clearHistory">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="3 6 5 6 21 6" />
            <path
              d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"
            />
          </svg>
          清除训练记录
        </button>

        <button class="action-button" @click="resetSettings">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          恢复默认设置
        </button>
      </div>

      <div class="settings-section">
        <h2 class="section-title">关于</h2>
        
        <button class="action-button info" @click="checkForUpdates">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="7 10 12 15 17 10" />
            <line x1="12" y1="15" x2="12" y2="3" />
          </svg>
          检查版本更新
        </button>
        
        <div class="about-info">
          <p><strong>版本:</strong> {{ currentVersion }}</p>
          <p><strong>应用名称:</strong> NeuroFlex 认知训练系统</p>
          <p><strong>描述:</strong> 专业的认知与大脑训练</p>
        </div>
      </div>
    </main>

    <!-- 隐私协议对话框 -->
    <PrivacyDialog 
      ref="privacyDialog"
      @accepted="handlePrivacyAccepted"
      @declined="handlePrivacyDeclined"
    />

    <!-- 权限状态对话框 -->
    <van-popup
      v-model:show="showPermissionDialog"
      position="center"
      :style="{ width: '90%', maxWidth: '400px', background: 'var(--bg-secondary)' }"
      round
      :close-on-click-overlay="false"
      class="permission-dialog"
    >
      <div class="permission-content">
        <div class="permission-header">
          <div class="permission-icon">🔐</div>
          <h2 class="permission-title">权限状态</h2>
        </div>

        <div class="permission-body">
          <div v-for="(permission, key) in permissionStatus" :key="key" class="permission-item">
            <div class="permission-info">
              <div class="permission-name">{{ getPermissionName(key) }}</div>
              <div class="permission-desc">{{ permission.description }}</div>
            </div>
            <div class="permission-status" :class="{ granted: permission.granted }">
              <svg v-if="permission.granted" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M9 12l2 2 4-4" />
                <circle cx="12" cy="12" r="10" />
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
              <span>{{ permission.granted ? '已授权' : '未授权' }}</span>
            </div>
          </div>
        </div>

        <div class="permission-actions">
          <van-button @click="showPermissionDialog = false">
            关闭
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Capacitor } from '@capacitor/core'
import { useConfigStore } from '@/stores/config'
import { useUserStore } from '@/stores/user'
import { useVersionCheck } from '@/composables/useVersionCheck'
import { Popup as VanPopup, Button as VanButton } from 'vant'
import 'vant/lib/popup/style'
import 'vant/lib/button/style'
import PrivacyDialog from '@/components/PrivacyDialog.vue'
import permissionManager from '@/utils/permissions'

const router = useRouter()
const configStore = useConfigStore()
const userStore = useUserStore()
const { currentVersion, hasUpdate, updateInfo, checkForUpdates: checkVersionUpdates, goToDownload } = useVersionCheck()

const privacyDialog = ref(null)
const showPermissionDialog = ref(false)
const permissionStatus = ref({})

function goBack() {
  router.back()
}

function saveConfig() {
  configStore.saveConfig()
}

// 显示隐私协议
function showPrivacyDialog() {
  privacyDialog.value?.show()
}

// 处理隐私协议同意
function handlePrivacyAccepted() {
  alert('感谢您同意隐私协议！')
}

// 处理隐私协议拒绝
function handlePrivacyDeclined() {
  // 在设置页面中，用户可以选择不同意，但不会影响应用使用
}

// 检查权限状态
async function checkPermissions() {
  try {
    const permissions = await permissionManager.getPermissionsSummary()
    permissionStatus.value = permissions
    showPermissionDialog.value = true
  } catch (error) {
    console.error('获取权限状态失败:', error)
    alert('获取权限状态失败，请重试')
  }
}

function clearHistory() {
  if (confirm('确定要清除所有训练记录吗？此操作不可恢复。')) {
    userStore.clearHistory()
    alert('训练记录已清除')
  }
}

function resetSettings() {
  if (confirm('确定要恢复默认设置吗？')) {
    configStore.resetConfig()
    alert('设置已恢复默认')
  }
}

// 检查版本更新
async function checkForUpdates() {
  try {
    await checkVersionUpdates()
    
    if (hasUpdate.value) {
      const confirmUpdate = confirm(
        `发现新版本 v${updateInfo.value?.version || '未知'}！\n\n` +
        `当前版本：v${currentVersion.value}\n` +
        `最新版本：v${updateInfo.value?.version || '未知'}\n\n` +
        `是否立即下载更新？`
      )
      
      if (confirmUpdate) {
        // 在 APP 环境下，打开外部浏览器下载
        if (Capacitor.isNativePlatform()) {
          if (updateInfo.value?.downloadUrl) {
            window.open(updateInfo.value.downloadUrl, '_system')
          } else {
            window.open('/download', '_system')
          }
        } else {
          goToDownload()
        }
      }
    } else {
      alert('当前已是最新版本！')
    }
  } catch (error) {
    console.error('检查更新失败:', error)
    alert('检查更新失败，请稍后重试')
  }
}

// 获取权限名称
function getPermissionName(key) {
  const names = {
    storage: '存储权限',
    network: '网络权限'
  }
  return names[key] || key
}
</script>

<style lang="scss" scoped>
.settings-page {
  height: 100%;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  position: fixed;
  top: env(safe-area-inset-top, 0px);
  left: 0;
  right: 0;
  z-index: $z-fixed;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md $spacing-lg;
  background: rgba(26, 26, 46, 0.95);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);

  .back-button {
    @include button-reset;
    @include click-feedback;
    width: 40px;
    height: 40px;
    border-radius: $radius-full;
    background: rgba(255, 255, 255, 0.05);
    color: $text-primary;
    @include flex-center;
  }

  .page-title {
    font-size: $font-xl;
    font-weight: $font-semibold;
    margin: 0;
    color: $text-primary;
  }

  .header-spacer {
    width: 40px;
  }
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: calc($spacing-md + 60px) $spacing-lg $spacing-lg;
  padding-bottom: calc($spacing-lg + 70px + env(safe-area-inset-bottom));
  @include custom-scrollbar;
  min-height: 0; // 重要：让flex子元素可以收缩

  // PC端布局调整
  &.pc-layout {
    padding: $spacing-lg;
    padding-bottom: $spacing-lg;
  }
}

.settings-section {
  margin-bottom: $spacing-2xl;

  .section-title {
    font-size: $font-lg;
    font-weight: $font-semibold;
    margin-bottom: $spacing-lg;
    color: $text-secondary;
  }
}

.setting-item {
  @include glass-card;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md $spacing-lg;
  margin-bottom: $spacing-md;

  .setting-info {
    flex: 1;

    .setting-label {
      font-size: $font-sm;
      font-weight: $font-medium;
      margin-bottom: $spacing-xs;
    }

    .setting-description {
      font-size: $font-xs;
      color: $text-secondary;
    }
  }
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;

  input {
    opacity: 0;
    width: 0;
    height: 0;

    &:checked + .toggle-slider {
      background-color: $accent-primary;

      &:before {
        transform: translateX(20px);
      }
    }
  }

  .toggle-slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.1);
    transition: $transition-base;
    border-radius: 24px;

    &:before {
      position: absolute;
      content: '';
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: $transition-base;
      border-radius: 50%;
    }
  }
}

.action-button {
  @include button-reset;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  width: 100%;
  padding: $spacing-md $spacing-lg;
  margin-bottom: $spacing-md;
  border-radius: $radius-md;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: $text-primary;
  font-weight: $font-medium;
  font-size: $font-sm;

  &:focus {
    outline: none;
  }

  &.info {
    // info 类型也保持相同样式
  }
}

.about-info {
  @include glass-card;
  padding: $spacing-lg;

  p {
    margin-bottom: $spacing-sm;
    font-size: $font-sm;
    color: $text-secondary;

    strong {
      color: $text-primary;
      margin-right: $spacing-xs;
    }

    &:last-child {
      margin-bottom: 0;
    }
  }
}

// 权限对话框样式
.permission-dialog {
  :deep(.van-popup) {
    background: $bg-secondary;
    border: 1px solid $glass-border;
    box-shadow: $glass-shadow;
  }
}

.permission-content {
  padding: $spacing-xl;
}

.permission-header {
  text-align: center;
  margin-bottom: $spacing-lg;

  .permission-icon {
    font-size: 48px;
    margin-bottom: $spacing-md;
  }

  .permission-title {
    font-size: $font-xl;
    font-weight: $font-bold;
    color: $text-primary;
    margin: 0;
  }
}

.permission-body {
  margin-bottom: $spacing-lg;
}

.permission-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: $spacing-md;
  margin-bottom: $spacing-sm;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid $glass-border;
  border-radius: $radius-md;

  .permission-info {
    flex: 1;

    .permission-name {
      font-size: $font-base;
      font-weight: $font-semibold;
      color: $text-primary;
      margin-bottom: $spacing-xs;
    }

    .permission-desc {
      font-size: $font-sm;
      color: $text-secondary;
    }
  }

  .permission-status {
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    color: $accent-error;

    &.granted {
      color: $accent-success;
    }

    span {
      font-size: $font-sm;
      font-weight: $font-medium;
    }
  }
}

.permission-actions {
  text-align: center;

  :deep(.van-button) {
    background: linear-gradient(135deg, $accent-primary, $accent-secondary);
    border: none;
    color: $text-primary;
    border-radius: $radius-md;
    padding: $spacing-md $spacing-xl;
  }
}
</style>
