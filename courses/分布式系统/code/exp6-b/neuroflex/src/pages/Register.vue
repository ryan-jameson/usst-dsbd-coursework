<template>
  <div class="register-page">
    <!-- 移动端返回按钮 -->
    <header v-if="!isPCDevice" class="mobile-header">
      <button class="back-button" @click="goBack">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>
    </header>

    <!-- 主要内容区域 -->
    <main class="main-content">
      <!-- PC端左侧装饰区域 -->
      <div v-if="isPCDevice" class="decoration-section">
        <div class="floating-elements">
          <div class="floating-circle circle-1"></div>
          <div class="floating-circle circle-2"></div>
          <div class="floating-circle circle-3"></div>
        </div>
        <div class="brand-content">
          <h1 class="brand-title">NeuroFlex</h1>
          <p class="brand-subtitle">科学认知训练平台</p>
          <div class="feature-highlights">
            <div class="highlight-item">
              <div class="highlight-icon">🧠</div>
              <span>提升认知能力</span>
            </div>
            <div class="highlight-item">
              <div class="highlight-icon">📊</div>
              <span>科学数据分析</span>
            </div>
            <div class="highlight-item">
              <div class="highlight-icon">🎯</div>
              <span>个性化训练</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 注册表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 移动端标题 -->
          <div v-if="!isPCDevice" class="mobile-title-section">
            <h2 class="form-title">加入 NeuroFlex</h2>
            <p class="form-subtitle">开始您的认知训练之旅</p>
          </div>

          <!-- PC端标题 -->
          <div v-if="isPCDevice" class="pc-title-section">
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle">填写信息完成注册</p>
          </div>

          <!-- 注册表单 -->
          <form class="register-form" @submit.prevent="handleRegister">
            <!-- 邮箱输入 -->
            <div class="input-group">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <input
                  v-model="formData.email"
                  type="email"
                  class="form-input"
                  placeholder="邮箱地址"
                  :class="{ 'error': errors.email }"
                  @blur="validateEmail"
                  @input="clearError('email')"
                  required
                />
              </div>
              <div v-if="errors.email" class="error-text">{{ errors.email }}</div>
            </div>

            <!-- 昵称输入 -->
            <div class="input-group">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <input
                  v-model="formData.nickname"
                  type="text"
                  class="form-input"
                  placeholder="昵称（3-20个字符）"
                  :class="{ 'error': errors.nickname }"
                  maxlength="20"
                  @blur="validateNickname"
                  @input="clearError('nickname')"
                  required
                />
              </div>
              <div v-if="errors.nickname" class="error-text">{{ errors.nickname }}</div>
            </div>

            <!-- 密码输入 -->
            <div class="input-group">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <circle cx="12" cy="16" r="1"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                  </svg>
                </div>
                <input
                  v-model="formData.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="密码（至少8位，包含字母和数字）"
                  :class="{ 'error': errors.password }"
                  @blur="validatePassword"
                  @input="clearError('password')"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showPassword = !showPassword"
                >
                  <svg v-if="showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <div v-if="errors.password" class="error-text">{{ errors.password }}</div>
            </div>

            <!-- 确认密码输入 -->
            <div class="input-group">
              <div class="input-wrapper">
                <div class="input-icon">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                    <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
                    <polyline points="9 12 11 14 15 10"/>
                  </svg>
                </div>
                <input
                  v-model="formData.confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  class="form-input"
                  placeholder="确认密码"
                  :class="{ 'error': errors.confirmPassword }"
                  @blur="validateConfirmPassword"
                  @input="clearError('confirmPassword')"
                  required
                />
                <button
                  type="button"
                  class="password-toggle"
                  @click="showConfirmPassword = !showConfirmPassword"
                >
                  <svg v-if="showConfirmPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                    <line x1="1" y1="1" x2="23" y2="23"/>
                  </svg>
                  <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
              </div>
              <div v-if="errors.confirmPassword" class="error-text">{{ errors.confirmPassword }}</div>
            </div>

            <!-- 密码强度指示器 -->
            <div v-if="formData.password" class="password-strength">
              <div class="strength-bar">
                <div 
                  class="strength-fill" 
                  :class="passwordStrength.level"
                  :style="{ width: passwordStrength.percentage + '%' }"
                ></div>
              </div>
              <span class="strength-text">密码强度：{{ passwordStrength.text }}</span>
            </div>

            <!-- 用户协议 -->
            <div class="agreement-section">
              <label class="checkbox-wrapper">
                <input v-model="formData.agreeToTerms" type="checkbox" class="checkbox-input">
                <div class="checkbox-custom"></div>
                <span class="checkbox-label">
                  我已阅读并同意
                  <button type="button" class="link-button" @click="showTerms = true">用户协议</button>
                  和
                  <button type="button" class="link-button" @click="showPrivacy = true">隐私政策</button>
                </span>
              </label>
              <div v-if="errors.agreeToTerms" class="error-text">
                {{ errors.agreeToTerms }}
              </div>
            </div>

            <!-- 错误消息 -->
            <div v-if="generalError" class="general-error">
              {{ generalError }}
            </div>

            <!-- 成功消息 -->
            <div v-if="successMessage" class="success-message">
              {{ successMessage }}
            </div>

            <!-- 注册按钮 -->
            <button
              type="submit"
              class="register-button"
              :disabled="isLoading || !isFormValid"
            >
              <span v-if="isLoading" class="loading-spinner"></span>
              {{ isLoading ? '注册中...' : '注册账号' }}
            </button>
          </form>

          <!-- 登录链接 -->
          <div class="login-section">
            <span class="login-text">已有账号？</span>
            <button class="login-link" @click="goToLogin">立即登录</button>
          </div>
        </div>
      </div>
    </main>

    <!-- 用户协议弹窗 -->
    <van-popup
      v-model:show="showTerms"
      position="bottom"
      round
      closeable
      close-icon-position="top-right"
      :close-on-click-overlay="false"
      :safe-area-inset-bottom="true"
      :style="{ height: '70%' }"
    >
      <div class="terms-popup">
        <div class="popup-header">
          <h3 class="popup-title">用户协议</h3>
        </div>
        <div class="popup-content">
          <div class="terms-content">
            <h4>欢迎使用 NeuroFlex</h4>
            <p>感谢您选择 NeuroFlex 认知训练应用。在使用我们的服务之前，请仔细阅读以下用户协议。</p>
            
            <h4>服务说明</h4>
            <p>NeuroFlex 是一款专业的认知训练应用，旨在通过科学的训练方法帮助用户提升认知能力。</p>
            
            <h4>用户责任</h4>
            <p>用户应当合理使用本应用，不得进行任何违法或有害的活动。</p>
            
            <h4>隐私保护</h4>
            <p>我们承诺保护用户的个人信息和隐私安全。</p>
          </div>
        </div>
      </div>
    </van-popup>

    <!-- 隐私政策弹窗 -->
    <van-popup
      v-model:show="showPrivacy"
      position="bottom"
      round
      closeable
      close-icon-position="top-right"
      :close-on-click-overlay="false"
      :safe-area-inset-bottom="true"
      :style="{ height: '70%' }"
    >
      <div class="privacy-popup">
        <div class="popup-header">
          <h3 class="popup-title">隐私政策</h3>
        </div>
        <div class="popup-content">
          <div class="privacy-content">
            <h4>信息收集</h4>
            <p>我们只收集为您提供服务所必需的信息，包括邮箱地址、昵称和训练记录。</p>
            
            <h4>信息使用</h4>
            <p>您的个人信息仅用于提供和改善我们的服务，不会用于其他商业目的。</p>
            
            <h4>信息保护</h4>
            <p>我们采用行业标准的安全措施保护您的个人信息。</p>
            
            <h4>信息共享</h4>
            <p>除法律要求外，我们不会与第三方共享您的个人信息。</p>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth.js'
import { 
  Popup as VanPopup
} from 'vant'
import 'vant/lib/popup/style'
import { isPC } from '@/utils/device'

const router = useRouter()
const { register, isLoading } = useAuth()

// 检测设备类型
const isPCDevice = ref(isPC())

// 表单数据
const formData = reactive({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: false
})

// 表单错误
const errors = reactive({
  email: '',
  nickname: '',
  password: '',
  confirmPassword: '',
  agreeToTerms: ''
})

// 界面状态
const showPassword = ref(false)
const showConfirmPassword = ref(false)
const showTerms = ref(false)
const showPrivacy = ref(false)
const successMessage = ref('')
const generalError = ref('')

// 表单验证
const validateEmail = () => {
  const emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/
  if (!formData.email) {
    errors.email = '请输入邮箱地址'
  } else if (!emailRegex.test(formData.email)) {
    errors.email = '邮箱格式不正确'
  } else {
    errors.email = ''
  }
}

const validateNickname = () => {
  if (!formData.nickname) {
    errors.nickname = '请输入昵称'
  } else if (formData.nickname.length < 3) {
    errors.nickname = '昵称至少需要3个字符'
  } else if (formData.nickname.length > 20) {
    errors.nickname = '昵称不能超过20个字符'
  } else if (!/^[a-zA-Z0-9\u4e00-\u9fa5_-]+$/.test(formData.nickname)) {
    errors.nickname = '昵称只能包含字母、数字、中文、下划线和连字符'
  } else {
    errors.nickname = ''
  }
}

const validatePassword = () => {
  if (!formData.password) {
    errors.password = 'REDACTED_CONFIGURE_LOCALLY'
  } else if (formData.password.length < 8) {
    errors.password = 'REDACTED_CONFIGURE_LOCALLY'
  } else if (!/[A-Za-z]/.test(formData.password)) {
    errors.password = 'REDACTED_CONFIGURE_LOCALLY'
  } else if (!/\d/.test(formData.password)) {
    errors.password = 'REDACTED_CONFIGURE_LOCALLY'
  } else {
    errors.password = ''
  }
}

const validateConfirmPassword = () => {
  if (!formData.confirmPassword) {
    errors.confirmPassword = 'REDACTED_CONFIGURE_LOCALLY'
  } else if (formData.password !== formData.confirmPassword) {
    errors.confirmPassword = 'REDACTED_CONFIGURE_LOCALLY'
  } else {
    errors.confirmPassword = ''
  }
}

// 密码强度计算
const passwordStrength = computed(() => {
  const password = formData.password
  if (!password) return { level: '', percentage: 0, text: '' }

  let score = 0
  let feedback = []

  // 长度检查
  if (password.length >= 8) score += 25
  else feedback.push('至少8位')

  // 包含小写字母
  if (/[a-z]/.test(password)) score += 25
  else feedback.push('包含小写字母')

  // 包含大写字母
  if (/[A-Z]/.test(password)) score += 25
  else feedback.push('包含大写字母')

  // 包含数字
  if (/\d/.test(password)) score += 25
  else feedback.push('包含数字')

  // 包含特殊字符（额外加分）
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) score += 10

  let level, text
  if (score < 50) {
    level = 'weak'
    text = '弱'
  } else if (score < 75) {
    level = 'medium'
    text = '中等'
  } else {
    level = 'strong'
    text = '强'
  }

  return { level, percentage: Math.min(score, 100), text }
})

// 表单有效性检查
const isFormValid = computed(() => {
  return formData.email &&
         formData.nickname &&
         formData.password &&
         formData.confirmPassword &&
         formData.agreeToTerms &&
         !errors.email &&
         !errors.nickname &&
         !errors.password &&
         !errors.confirmPassword
})

// 清除错误
const clearError = (field) => {
  errors[field] = ''
  generalError.value = ''
}

// 处理注册
const handleRegister = async () => {
  // 验证所有字段
  validateEmail()
  validateNickname()
  validatePassword()
  validateConfirmPassword()

  if (!formData.agreeToTerms) {
    errors.agreeToTerms = '请同意用户协议和隐私政策'
  }

  // 如果有错误，不提交
  if (!isFormValid.value) {
    return
  }

  try {
    generalError.value = ''
    
    // 临时幽默提示 😄
    generalError.value = '你什么身份？还想注册？想的美！！！😏 你瞅啥，说的就是你 🫵'
    return
    
    const result = await register(
      formData.email,
      formData.password,
      formData.nickname
    )

    if (result.success) {
      successMessage.value = result.message || '注册成功！请检查邮箱进行验证。'
      
      // 3秒后跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
  } catch (error) {
    console.error('Registration error:', error)
    generalError.value = error.message || '注册失败，请重试'
  }
}

// 导航方法
const goBack = () => {
  router.back()
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<style lang="scss" scoped>
@use "sass:color";

.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, $bg-primary 0%, $bg-secondary 100%);
  position: relative;
  overflow: hidden;
}

.mobile-header {
  position: fixed;
  top: env(safe-area-inset-top, 0px);
  left: 0;
  right: 0;
  z-index: 100;
  padding: $spacing-md $spacing-lg;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);

  .back-button {
    @include button-reset;
    @include click-feedback;
    width: 40px;
    height: 40px;
    border-radius: $radius-full;
    background: rgba(255, 255, 255, 0.05);
    color: $text-primary;
    @include flex-center;
    transition: all $transition-base;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
      transform: scale(1.05);
    }
  }
}

.main-content {
  min-height: 100vh;
  display: flex;
  
  // 移动端布局
  @include mobile {
    flex-direction: column;
    padding-top: 80px;
  }
}

// PC端左侧装饰区域 - 2:1布局中的2
.decoration-section {
  flex: 2; // 2:1 比例中的 2
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, rgba(123, 44, 191, 0.05) 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-2xl;
  overflow: hidden;
  min-height: 100vh;
  
  // 快速入场动画
  animation: slideInLeft 0.3s ease-out;

  .floating-elements {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;

    .floating-circle {
      position: absolute;
      border-radius: 50%;
      background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1));
      backdrop-filter: blur(20px);
      animation: float 6s ease-in-out infinite;

      &.circle-1 {
        width: 200px;
        height: 200px;
        top: 10%;
        left: 10%;
        animation-delay: 0s;
      }

      &.circle-2 {
        width: 150px;
        height: 150px;
        top: 60%;
        right: 20%;
        animation-delay: 2s;
      }

      &.circle-3 {
        width: 100px;
        height: 100px;
        bottom: 20%;
        left: 30%;
        animation-delay: 4s;
      }
    }
  }

  .brand-content {
    text-align: center;
    z-index: 1;
    // 快速品牌内容入场动画
    animation: fadeInUp 0.4s ease-out 0.1s both;

    .brand-title {
      font-size: 4rem;
      font-weight: $font-bold;
      background: linear-gradient(135deg, $accent-primary, $accent-secondary);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: $spacing-md;
      // 标题特殊动画
      animation: titleGlow 2s ease-in-out infinite alternate;
    }

    .brand-subtitle {
      font-size: $font-xl;
      color: $text-secondary;
      margin-bottom: $spacing-2xl;
    }

    .feature-highlights {
      display: flex;
      flex-direction: column;
      gap: $spacing-lg;

      .highlight-item {
        display: flex;
        align-items: center;
        gap: $spacing-md;
        padding: $spacing-lg;
        background: rgba(255, 255, 255, 0.03);
        border-radius: $radius-lg;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        // 快速特性项目依次入场
        animation: slideInLeft 0.3s ease-out both;
        
        &:nth-child(1) { animation-delay: 0.2s; }
        &:nth-child(2) { animation-delay: 0.25s; }
        &:nth-child(3) { animation-delay: 0.3s; }

        .highlight-icon {
          font-size: $font-2xl;
        }

        span {
          font-size: $font-base;
          color: $text-primary;
        }
      }
    }
  }
}

// 表单区域 - 2:1布局中的1
.form-section {
  flex: 1; // 2:1 比例中的 1
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-2xl;
  min-height: 100vh;
  
  // 快速入场动画
  animation: slideInRight 0.3s ease-out;
  
  @include mobile {
    padding: $spacing-lg $spacing-lg;
    min-height: calc(100vh - 80px);
    justify-content: flex-start;
    padding-top: $spacing-sm;
    animation: slideInUp 0.3s ease-out;
  }

  .form-container {
    width: 100%;
    max-width: 400px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(20px);
    border-radius: $radius-lg;
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: $spacing-2xl;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    // 快速表单容器入场动画
    animation: scaleIn 0.3s ease-out 0.2s both;

    @include mobile {
      padding: $spacing-xl;
      border-radius: $radius-lg;
      background: rgba(255, 255, 255, 0.05);
      margin-top: 0;
      animation: slideInUp 0.3s ease-out 0.1s both;
    }
  }
}

.mobile-title-section,
.pc-title-section {
  text-align: center;
  margin-bottom: $spacing-2xl;
  // 快速标题入场动画
  animation: fadeInUp 0.3s ease-out 0.3s both;

  .form-title {
    font-size: $font-2xl;
    font-weight: $font-bold;
    color: $text-primary;
    margin-bottom: $spacing-sm;
    
    @include mobile {
      font-size: $font-xl;
    }
  }

  .form-subtitle {
    font-size: $font-base;
    color: $text-secondary;
    margin: 0;
    
    @include mobile {
      font-size: $font-sm;
    }
  }
}

.register-form {
  // 快速表单整体入场动画
  animation: fadeInUp 0.3s ease-out 0.4s both;
  
  .input-group {
    margin-bottom: $spacing-lg;
    // 快速输入框依次入场
    animation: slideInUp 0.2s ease-out both;
    
    &:nth-child(1) { animation-delay: 0.5s; }
    &:nth-child(2) { animation-delay: 0.55s; }
    &:nth-child(3) { animation-delay: 0.6s; }
    &:nth-child(4) { animation-delay: 0.65s; }

    .input-wrapper {
      position: relative;
      display: flex;
      align-items: center;
    }

    .form-input {
      width: 100%;
      height: 56px;
      padding: 0 50px 0 50px;
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: $radius-lg;
      color: $text-primary;
      font-size: $font-base;
      transition: all $transition-base;
      backdrop-filter: blur(10px);

      @include mobile {
        height: 52px;
        font-size: $font-sm;
      }

      &::placeholder {
        color: $text-tertiary;
      }

      &:focus {
        outline: none;
        border-color: $accent-primary;
        background: rgba(0, 212, 255, 0.05);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
      }

      &.error {
        border-color: $accent-error;
        background: rgba(255, 51, 102, 0.05);
      }
    }

    .input-icon {
      position: absolute;
      left: $spacing-md;
      color: $text-secondary;
      pointer-events: none;
      z-index: 1;
    }

    .password-toggle {
      @include button-reset;
      position: absolute;
      right: $spacing-md;
      color: $text-secondary;
      padding: $spacing-xs;
      border-radius: $radius-sm;
      transition: all $transition-base;

      &:hover {
        color: $text-primary;
        background: rgba(255, 255, 255, 0.05);
      }
    }

    .error-text {
      color: $accent-error;
      font-size: $font-sm;
      margin-top: $spacing-xs;
      margin-left: $spacing-sm;
    }
  }
}

.password-strength {
  margin: $spacing-md 0;
  // 快速密码强度入场动画
  animation: fadeInUp 0.2s ease-out 0.7s both;

  .strength-bar {
    height: 4px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: $spacing-xs;
  }

  .strength-fill {
    height: 100%;
    transition: all 0.3s ease;

    &.weak {
      background-color: $accent-error;
    }

    &.medium {
      background-color: #f59e0b;
    }

    &.strong {
      background-color: #10b981;
    }
  }

  .strength-text {
    font-size: $font-xs;
    color: $text-secondary;
  }
}

.agreement-section {
  margin: $spacing-lg 0;
  // 快速协议区域入场动画
  animation: fadeInUp 0.2s ease-out 0.75s both;

  .checkbox-wrapper {
    display: flex;
    align-items: flex-start;
    gap: $spacing-sm;
    cursor: pointer;

    .checkbox-input {
      display: none;
    }

    .checkbox-custom {
      width: 20px;
      height: 20px;
      border: 2px solid rgba(255, 255, 255, 0.2);
      border-radius: $radius-sm;
      background: rgba(255, 255, 255, 0.05);
      position: relative;
      transition: all $transition-base;
      flex-shrink: 0;
      margin-top: 2px;

      &::after {
        content: '';
        position: absolute;
        top: 2px;
        left: 6px;
        width: 6px;
        height: 10px;
        border: solid $text-primary;
        border-width: 0 2px 2px 0;
        transform: rotate(45deg);
        opacity: 0;
        transition: opacity $transition-base;
      }
    }

    .checkbox-input:checked + .checkbox-custom {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(255, 255, 255, 0.3);

      &::after {
        opacity: 1;
      }
    }

    .checkbox-label {
      color: $text-secondary;
      font-size: $font-sm;
      line-height: 1.5;
      font-weight: $font-medium;
    }
  }

  .link-button {
    @include button-reset;
    color: $text-secondary;
    font-weight: $font-medium;
    text-decoration: none;
    transition: color $transition-base;

    &:hover {
      color: $accent-primary;
      text-decoration: underline;
    }
  }

  .error-text {
    color: $accent-error;
    font-size: $font-sm;
    margin-top: $spacing-xs;
    margin-left: 28px;
  }
}

.general-error {
  background: rgba(255, 51, 102, 0.1);
  color: $accent-error;
  padding: $spacing-md;
  border-radius: $radius-md;
  font-size: $font-sm;
  text-align: center;
  margin-bottom: $spacing-lg;
  border: 1px solid rgba(255, 51, 102, 0.2);
}

.success-message {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
  padding: $spacing-md;
  border-radius: $radius-md;
  font-size: $font-sm;
  text-align: center;
  margin-bottom: $spacing-lg;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.register-button {
  @include button-reset;
  @include click-feedback;
  width: 100%;
  height: 56px;
  border-radius: $radius-lg;
  background: linear-gradient(135deg, $accent-primary, $accent-secondary);
  color: $text-primary;
  font-weight: $font-semibold;
  font-size: $font-base;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: $spacing-sm;
  margin-bottom: $spacing-xl;
  box-shadow: 0 4px 15px rgba(0, 212, 255, 0.2);
  // 快速注册按钮入场动画
  animation: scaleIn 0.2s ease-out 0.8s both;

  @include mobile {
    height: 52px;
    font-size: $font-sm;
  }

  &:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
  }

  &:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
  }

  .loading-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: $text-primary;
    border-radius: $radius-full;
    animation: spin 1s linear infinite;
  }
}

.login-section {
  text-align: center;
  // 快速登录链接入场动画
  animation: fadeInUp 0.2s ease-out 0.85s both;

  .login-text {
    color: $text-secondary;
    font-size: $font-sm;
    margin-right: $spacing-xs;
  }

  .login-link {
    @include button-reset;
    color: $accent-primary;
    font-size: $font-sm;
    font-weight: $font-semibold;
    transition: color $transition-base;

    &:hover {
      color: color.adjust($accent-primary, $lightness: 10%);
    }
  }
}

// 动画
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// 快速入场动画
@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(15px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes titleGlow {
  from {
    filter: brightness(1);
  }
  to {
    filter: brightness(1.2);
  }
}

// 弹窗样式
.terms-popup,
.privacy-popup {
  padding: $spacing-lg 0;

  .popup-header {
    padding: 0 $spacing-lg $spacing-md;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .popup-title {
      font-size: $font-lg;
      font-weight: $font-semibold;
      color: $text-primary;
      margin: 0;
      text-align: center;
    }
  }

  .popup-content {
    padding: $spacing-lg;
    height: calc(100% - 60px);
    overflow-y: auto;
    @include custom-scrollbar;
  }

  .terms-content,
  .privacy-content {
    h4 {
      color: $text-primary;
      font-size: $font-base;
      font-weight: $font-semibold;
      margin: $spacing-lg 0 $spacing-sm 0;

      &:first-child {
        margin-top: 0;
      }
    }

    p {
      color: $text-secondary;
      font-size: $font-sm;
      line-height: 1.6;
      margin: 0 0 $spacing-md 0;
    }
  }
}

// Vant 组件样式覆盖
:deep(.van-popup) {
  background: $bg-secondary;
  border-top-left-radius: $radius-lg;
  border-top-right-radius: $radius-lg;

  .van-popup__close-icon {
    color: $text-secondary;
    font-size: 18px;

    &:hover {
      color: $text-primary;
    }
  }
}
</style>