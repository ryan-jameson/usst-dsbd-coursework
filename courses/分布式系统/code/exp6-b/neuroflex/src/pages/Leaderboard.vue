<template>
  <div class="leaderboard-page">
    <!-- 标题栏 -->
    <header class="page-header">
      <h1 class="page-title">排行榜</h1>
    </header>

    <!-- 筛选器 -->
    <div class="filters-section">
      <div class="filter-group">
        <label>训练模块</label>
        <ButtonGroupSelect v-model="selectedModule" :options="moduleOptions" />
      </div>
      
      <div class="filter-group">
        <label>时间范围</label>
        <ButtonGroupSelect v-model="timeRange" :options="timeRangeOptions" />
      </div>
    </div>

    <!-- 排行榜内容 -->
    <main class="page-content">
      <!-- 未登录提示 -->
      <div v-if="!isLoggedIn" class="login-required-notice">
        <div class="notice-icon">🔐</div>
        <h3>登录查看排行榜</h3>
        <p>登录后可查看全国排行榜数据</p>
        <p class="notice-hint">与全国玩家一较高下</p>
        <div class="login-actions">
          <button class="login-button primary" @click="goToLogin">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4" />
              <polyline points="10 17 15 12 10 7" />
              <line x1="15" y1="12" x2="3" y2="12" />
            </svg>
            立即登录
          </button>
          <button class="login-button secondary" @click="goToRegister">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="8.5" cy="7" r="4" />
              <line x1="20" y1="8" x2="20" y2="14" />
              <line x1="23" y1="11" x2="17" y2="11" />
            </svg>
            注册账号
          </button>
        </div>
      </div>

      <!-- 云端同步未启用提示 -->
      <div v-else-if="!isCloudEnabled" class="cloud-disabled-notice">
        <div class="notice-icon">☁️</div>
        <h3>排行榜功能即将上线</h3>
        <p>云端同步功能正在开发中，敬请期待！</p>
        <p class="notice-hint">届时您可以与全国玩家一较高下</p>
      </div>

      <!-- 加载中 -->
      <div v-else-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载排行榜数据...</p>
      </div>

      <!-- 排行榜列表 -->
      <div v-else-if="leaderboardData.length > 0" class="leaderboard-list">
        <!-- 前三名特殊展示 -->
        <div v-if="topThree.length > 0" class="top-three">
          <div 
            v-for="(entry, index) in topThree" 
            :key="entry.userId"
            class="top-entry"
            :class="`rank-${index + 1}`"
          >
            <div class="rank-badge">
              <span class="rank-icon">{{ getRankIcon(index + 1) }}</span>
            </div>
            <div class="user-avatar">
              {{ entry.userName.charAt(0) }}
            </div>
            <div class="user-info">
              <div class="user-name">{{ entry.userName }}</div>
              <div class="user-score">{{ entry.score }}分</div>
            </div>
          </div>
        </div>

        <!-- 其他排名 -->
        <div class="rank-list">
          <div 
            v-for="entry in otherRanks" 
            :key="entry.userId"
            class="rank-entry"
            :class="{ 'is-current-user': entry.userId === currentUserId }"
          >
            <div class="rank-number">{{ entry.rank }}</div>
            <div class="user-avatar small">
              {{ entry.userName.charAt(0) }}
            </div>
            <div class="entry-info">
              <div class="user-name">{{ entry.userName }}</div>
              <div class="entry-stats">
                <span class="stat">{{ entry.score }}分</span>
                <span class="stat">{{ (entry.accuracy * 100).toFixed(0) }}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <div class="empty-icon">🏆</div>
        <p>暂无排行榜数据</p>
        <p class="empty-hint">完成训练后即可上榜</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAuth } from '@/composables/useAuth.js'
// import { getLeaderboard, getDatabaseConfig } from '@/utils/database'
import ButtonGroupSelect from '@/components/ButtonGroupSelect.vue'

const router = useRouter()
const userStore = useUserStore()
const { isLoggedIn } = useAuth()

const selectedModule = ref('schulte')
const timeRange = ref('all')
const loading = ref(false)
const leaderboardData = ref([])

const moduleOptions = [
  { label: '舒尔特', value: 'schulte' },
  { label: 'Stroop', value: 'stroop' },
  { label: '序列', value: 'sequence' },
  { label: '听觉', value: 'audio' },
  { label: '镜像', value: 'mirror' },
  { label: '分类', value: 'categorize' },
  { label: '情景', value: 'memory-story' }
]

const timeRangeOptions = [
  { label: '今日', value: 'day' },
  { label: '本周', value: 'week' },
  { label: '本月', value: 'month' },
  { label: '全部', value: 'all' }
]

const isCloudEnabled = computed(() => {
  // const config = getDatabaseConfig()
  // return config.enabled
  return false // 暂时禁用云端功能
})

const currentUserId = computed(() => userStore.profile.id)

const topThree = computed(() => {
  return leaderboardData.value.slice(0, 3)
})

const otherRanks = computed(() => {
  return leaderboardData.value.slice(3)
})

function getRankIcon(rank) {
  const icons = {
    1: '🥇',
    2: '🥈',
    3: '🥉'
  }
  return icons[rank] || rank
}

function goToLogin() {
  router.push('/login')
}

function goToRegister() {
  router.push('/register')
}

async function loadLeaderboard() {
  loading.value = true
  
  try {
    // const result = await getLeaderboard({
    //   moduleName: selectedModule.value,
    //   timeRange: timeRange.value,
    //   limit: 100
    // })
    
    // if (result.success) {
    //   leaderboardData.value = result.data || []
    // }
    
    // 模拟数据
    leaderboardData.value = []
  } catch (error) {
    console.error('加载排行榜失败:', error)
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.back()
}

onMounted(() => {
  if (isLoggedIn.value && isCloudEnabled.value) {
    loadLeaderboard()
  }
})
</script>

<style lang="scss" scoped>
@use "sass:color";

.leaderboard-page {
  height: 100%;
  background: $bg-primary;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md $spacing-lg;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);

  .page-title {
    font-size: $font-xl;
    font-weight: $font-semibold;
    margin: 0;
  }
}

.filters-section {
  padding: $spacing-lg;
  background: $bg-primary;

  .filter-group {
    margin-bottom: $spacing-md;

    &:last-child {
      margin-bottom: 0;
    }

    label {
      display: block;
      font-size: $font-sm;
      font-weight: $font-medium;
      color: $text-secondary;
      margin-bottom: $spacing-sm;
    }
  }
}

.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 0 $spacing-lg $spacing-lg;
  @include custom-scrollbar;
}

.cloud-disabled-notice {
  @include glass-card;
  padding: $spacing-2xl;
  text-align: center;
  margin-top: $spacing-xl;

  .notice-icon {
    font-size: 64px;
    margin-bottom: $spacing-lg;
  }

  h3 {
    font-size: $font-xl;
    font-weight: $font-semibold;
    margin: 0 0 $spacing-md;
    color: $text-primary;
  }

  p {
    color: $text-secondary;
    margin: $spacing-sm 0;
  }

  .notice-hint {
    font-size: $font-sm;
    color: $accent-primary;
  }
}

.login-required-notice {
  @include glass-card;
  padding: $spacing-2xl;
  text-align: center;
  margin-top: $spacing-xl;
  
  @include mobile {
    padding: $spacing-xl;
    margin-top: $spacing-lg;
  }

  .notice-icon {
    font-size: 56px;
    margin-bottom: $spacing-lg;
    
    @include mobile {
      font-size: 48px;
      margin-bottom: $spacing-md;
    }
  }

  h3 {
    font-size: $font-xl;
    font-weight: $font-semibold;
    margin: 0 0 $spacing-md;
    color: $text-primary;
    
    @include mobile {
      font-size: $font-lg;
      margin-bottom: $spacing-sm;
    }
  }

  p {
    color: $text-secondary;
    margin: $spacing-sm 0;
    font-size: $font-base;
    
    @include mobile {
      font-size: $font-sm;
      margin: $spacing-xs 0;
    }
  }

  .notice-hint {
    font-size: $font-sm;
    color: $accent-primary;
    margin-bottom: $spacing-xl;
    
    @include mobile {
      font-size: $font-sm;
      margin-bottom: $spacing-lg;
    }
  }

  .login-actions {
    display: flex;
    gap: $spacing-md;
    justify-content: center;
    flex-wrap: wrap;

    @media (max-width: $breakpoint-sm) {
      gap: $spacing-sm;
    }
  }

  .login-button {
    @include button-reset;
    @include click-feedback;
    display: inline-flex;
    align-items: center;
    gap: $spacing-xs;
    padding: $spacing-md $spacing-xl;
    border-radius: $radius-md;
    font-weight: $font-medium;
    font-size: $font-base;
    transition: all $transition-base;
    min-width: 120px;
    justify-content: center;
    
    @include mobile {
      padding: $spacing-md $spacing-lg;
      font-size: $font-sm;
      min-width: 100px;
      
      svg {
        width: 16px;
        height: 16px;
      }
    }

    &.primary {
      background: linear-gradient(135deg, $accent-primary, $accent-secondary);
      border: none;
      color: $text-primary;

      &:hover {
        background: linear-gradient(135deg, color.adjust($accent-primary, $lightness: -5%), color.adjust($accent-secondary, $lightness: -5%));
        transform: translateY(-1px);
      }
    }

    &.secondary {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: $text-primary;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: $accent-primary;
      }
    }
  }
}

.loading-state {
  @include flex-center;
  flex-direction: column;
  gap: $spacing-lg;
  padding: $spacing-2xl;
  color: $text-secondary;

  .loading-spinner {
    width: 48px;
    height: 48px;
    border: 4px solid rgba(0, 212, 255, 0.2);
    border-top-color: $accent-primary;
    border-radius: $radius-full;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-state {
  @include flex-center;
  flex-direction: column;
  gap: $spacing-md;
  padding: $spacing-2xl;
  text-align: center;
  color: $text-secondary;

  .empty-icon {
    font-size: 64px;
    opacity: 0.5;
  }

  .empty-hint {
    font-size: $font-sm;
    color: $accent-primary;
  }
}

.leaderboard-list {
  .top-three {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: $spacing-md;
    margin-bottom: $spacing-xl;

    @include mobile {
      grid-template-columns: 1fr;
    }

    .top-entry {
      @include glass-card;
      padding: $spacing-lg;
      text-align: center;
      position: relative;
      overflow: hidden;

      &.rank-1 {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.1), rgba(255, 215, 0, 0.05));
        border-color: rgba(255, 215, 0, 0.3);
      }

      &.rank-2 {
        background: linear-gradient(135deg, rgba(192, 192, 192, 0.1), rgba(192, 192, 192, 0.05));
        border-color: rgba(192, 192, 192, 0.3);
      }

      &.rank-3 {
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.1), rgba(205, 127, 50, 0.05));
        border-color: rgba(205, 127, 50, 0.3);
      }

      .rank-badge {
        font-size: $font-3xl;
        margin-bottom: $spacing-sm;
      }

      .user-avatar {
        width: 64px;
        height: 64px;
        border-radius: $radius-full;
        background: linear-gradient(135deg, $accent-primary, $accent-secondary);
        color: $text-primary;
        font-size: $font-2xl;
        font-weight: $font-bold;
        @include flex-center;
        margin: 0 auto $spacing-md;
      }

      .user-info {
        .user-name {
          font-size: $font-base;
          font-weight: $font-semibold;
          margin-bottom: $spacing-xs;
        }

        .user-score {
          font-size: $font-xl;
          font-weight: $font-bold;
          color: $accent-primary;
        }
      }
    }
  }

  .rank-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;

    .rank-entry {
      @include glass-card;
      padding: $spacing-md;
      display: flex;
      align-items: center;
      gap: $spacing-md;
      transition: all $transition-base;

      &:hover {
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
      }

      &.is-current-user {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(0, 212, 255, 0.05));
        border-color: $accent-primary;
      }

      .rank-number {
        width: 32px;
        height: 32px;
        border-radius: $radius-md;
        background: rgba(255, 255, 255, 0.05);
        @include flex-center;
        font-weight: $font-bold;
        color: $text-secondary;
        flex-shrink: 0;
      }

      .user-avatar.small {
        width: 40px;
        height: 40px;
        border-radius: $radius-full;
        background: linear-gradient(135deg, $accent-primary, $accent-secondary);
        color: $text-primary;
        font-weight: $font-bold;
        @include flex-center;
        flex-shrink: 0;
      }

      .entry-info {
        flex: 1;
        min-width: 0;

        .user-name {
          font-weight: $font-medium;
          margin-bottom: 4px;
        }

        .entry-stats {
          display: flex;
          gap: $spacing-md;
          font-size: $font-sm;
          color: $text-secondary;

          .stat {
            &:first-child {
              color: $accent-primary;
              font-weight: $font-semibold;
            }
          }
        }
      }
    }
  }
}
</style>
