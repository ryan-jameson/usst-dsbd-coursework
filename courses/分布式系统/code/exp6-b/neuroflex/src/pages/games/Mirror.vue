<template>
  <div class="mirror-page">
    <!-- 顶部导航 -->
    <header class="page-header">
      <button class="back-button" @click="goBack">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </button>
      <h1 class="page-title">双侧神经协调</h1>
      <button v-if="!isDrawing" class="help-button" @click="showGuide = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
          <circle cx="12" cy="12" r="10" stroke-width="2" />
          <path d="M12 16v-4M12 8h.01" stroke-width="2" stroke-linecap="round" />
        </svg>
        <span>规则</span>
      </button>
      <button v-if="isDrawing" class="clear-button" @click="clearCanvas">重置</button>
    </header>

    <!-- 游戏说明弹窗 -->
    <GameGuide
      :visible="showGuide"
      title="双侧神经协调"
      :how-to-play="guideContent.howToPlay"
      :benefits="guideContent.benefits"
      :tips="guideContent.tips"
      @close="showGuide = false"
    />

    <!-- PC端禁用提示 -->
    <Modal 
      :visible="showPCWarning" 
      :show-close="false" 
      :show-footer="false" 
      :close-on-click-overlay="false"
    >
      <div class="pc-warning-content">
        <div class="warning-icon">📱</div>
        <h2>请使用移动设备</h2>
        <p class="warning-text">本训练依赖多点触控（Multitouch）技术<br>PC端无法实现双侧独立控制</p>
        <button class="primary-button" @click="goBack">返回首页</button>
      </div>
    </Modal>

    <!-- 1. 配置界面 -->
    <div v-if="!isDrawing && !showResult && !isPC" class="config-screen">
      <div class="config-card">
        <div class="section-title">训练模式 (Coordination Mode)</div>
        <div class="mode-list">
          <button
            v-for="mode in trainingModes"
            :key="mode.value"
            :class="['mode-item', { active: selectedMode === mode.value }]"
            @click="selectedMode = mode.value"
          >
            <div class="mode-icon">{{ mode.icon }}</div>
            <div class="mode-info">
              <div class="mode-header">
                <span class="name">{{ mode.name }}</span>
                <div class="stars">
                  <span v-for="n in 3" :key="n" :class="{ filled: n <= mode.difficulty }">★</span>
                </div>
              </div>
              <div class="desc">{{ mode.desc }}</div>
            </div>
          </button>
        </div>

        <div class="section-title mt-6">任务类型 (Task Type)</div>
        <div class="task-tabs">
          <button 
            v-for="task in taskTypes"
            :key="task.value"
            :class="['task-tab', { active: selectedTask === task.value }]"
            @click="selectedTask = task.value"
          >
            {{ task.label }}
          </button>
        </div>

        <div class="hint-box">
          <p v-if="selectedTask === 'trace'">🎯 目标：双手沿着虚线轨迹精准描摹</p>
          <p v-else>🎨 目标：双手在空白画板自由创作，保持运动不停</p>
        </div>

        <button class="start-button" @click="startDrawing">开始神经激活</button>
      </div>
    </div>

    <!-- 2. 绘图训练界面 -->
    <div v-if="isDrawing && !isPC" class="drawing-screen">
      <div class="instruction-banner">
        <span class="icon">🧠</span>
        <span>{{ currentInstruction }}</span>
      </div>

      <!-- 画布容器：核心交互区域 -->
      <div 
        class="canvas-container" 
        ref="canvasContainer"
        @touchstart.prevent="handleGlobalTouch('start', $event)"
        @touchmove.prevent="handleGlobalTouch('move', $event)"
        @touchend.prevent="handleGlobalTouch('end', $event)"
        @touchcancel.prevent="handleGlobalTouch('end', $event)"
      >
        <!-- 左画板 -->
        <div class="canvas-panel left-panel">
          <div class="panel-tag">Left</div>
          <canvas ref="leftCanvas"></canvas>
        </div>

        <!-- 中轴线 -->
        <div class="divider">
          <div class="line"></div>
          <div class="divider-icon">⚡</div>
          <div class="line"></div>
        </div>

        <!-- 右画板 -->
        <div class="canvas-panel right-panel">
          <div class="panel-tag">Right</div>
          <canvas ref="rightCanvas"></canvas>
        </div>
      </div>

      <div class="drawing-controls">
        <div class="timer">{{ formatTime(drawingDuration) }}</div>
        <button class="finish-button" @click="finishDrawing">完成训练</button>
      </div>
    </div>

    <!-- 3. 结果结算界面 -->
    <GameResult
      :visible="showResult"
      :type="resultType"
      :title="resultTitle"
      :subtitle="resultSubtitle"
      :stats="resultStats"
      :show-retry="true"
      close-text="返回菜单"
      @retry="handleRetry"
      @close="handleClose"
    />
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useTrainingStore } from '@/stores/training'
import GameResult from '@/components/GameResult.vue'
import GameGuide from '@/components/GameGuide.vue'
import Modal from '@/components/Modal.vue'
import {trainingModes,taskTypes} from '@/config/mirror.js'

const router = useRouter()
const userStore = useUserStore()
const trainingStore = useTrainingStore()

const isPC = ref(false)
const showPCWarning = ref(false)
const selectedMode = ref('mirror')
const selectedTask = ref('trace')

// 游戏说明
const showGuide = ref(false)
const guideContent = {
  howToPlay: `
    <p>这是一个<strong>双手协调训练</strong>游戏，需要在移动设备上使用多点触控。</p>
    <ul>
      <li>选择训练模式（镜像/平行/分离）</li>
      <li>选择任务类型（描摹/自由）</li>
      <li>双手同时在左右画板上绘制</li>
      <li>保持双手运动的协调性</li>
    </ul>
  `,
  benefits: `
    <p>双侧神经协调训练可以有效提升：</p>
    <ul>
      <li><strong>左右脑协调</strong> - 增强大脑半球间的连接</li>
      <li><strong>双侧运动控制</strong> - 提高双手独立操作能力</li>
      <li><strong>神经可塑性</strong> - 促进大脑神经网络发展</li>
      <li><strong>注意力分配</strong> - 训练同时处理多任务的能力</li>
    </ul>
  `,
  tips: `
    <p>训练技巧：</p>
    <ul>
      <li>从<em>镜像模式</em>开始，逐步提升难度</li>
      <li>保持双手运动速度一致</li>
      <li>分离模式最具挑战性，需要更多练习</li>
      <li>描摹模式可以帮助建立运动模式</li>
    </ul>
  `
}

const isDrawing = ref(false)
const showResult = ref(false)
const drawingDuration = ref(0)
const strokeCountLeft = ref(0)
const strokeCountRight = ref(0) // 分别记录以计算同步率

const leftCanvas = ref(null)
const rightCanvas = ref(null)
const leftCanvasImage = ref(null)
const rightCanvasImage = ref(null)

let leftCtx = null
let rightCtx = null
let timerInterval = null
let startTime = 0
let leftPaths = []
let rightPaths = []

// --- 计算属性 ---
const currentInstruction = computed(() => {
  const map = {
    mirror: '双手对称动作，保持速度一致',
    parallel: '双手向同一方向移动',
    dissociation: '左手画圆，右手画方，互不干扰'
  }
  return map[selectedMode.value]
})

const resultType = computed(() => 'success')
const resultTitle = computed(() => '神经激活完成')
const resultSubtitle = computed(() => {
  if (syncScore.value > 90) return '太棒了！你的左右脑配合完美无缺'
  if (syncScore.value > 70) return '表现不错，继续加强弱侧训练'
  return '协调性有待提高，请放慢速度再试一次'
})

// 计算同步率 (简单的算法：基于左右手笔画数量和时间的差异)
const syncScore = computed(() => {
  const total = strokeCountLeft.value + strokeCountRight.value
  if (total === 0) return 0
  const diff = Math.abs(strokeCountLeft.value - strokeCountRight.value)
  // 基础分100，每差一个采样点扣分，最低0分
  return Math.max(0, Math.round(100 - (diff / total) * 100))
})

const resultStats = computed(() => [
  { label: '双侧同步率', value: `${syncScore.value}%`, highlight: true },
  { label: '训练时长', value: formatTime(drawingDuration.value), highlight: false },
  { label: '训练模式', value: trainingModes.find(m => m.value === selectedMode.value)?.name, highlight: false }
])

// --- 核心逻辑 ---

function detectPC() {
  const isMobile = /android|webos|iphone|ipad|ipod|blackberry|iemobile|opera mini/i.test(navigator.userAgent.toLowerCase())
  const isTablet = /ipad|android(?!.*mobile)/i.test(navigator.userAgent.toLowerCase())
  isPC.value = !isMobile && !isTablet && window.innerWidth > 1024
  return isPC.value
}

function startDrawing() {
  isDrawing.value = true
  showResult.value = false
  strokeCountLeft.value = 0
  strokeCountRight.value = 0
  drawingDuration.value = 0
  leftPaths = []
  rightPaths = []
  
  trainingStore.startTraining('mirror')
  
  nextTick(() => {
    initCanvas()
    startTime = Date.now()
    timerInterval = setInterval(() => {
      drawingDuration.value = Date.now() - startTime
    }, 1000)
  })
}

function initCanvas() {
  if (!leftCanvas.value || !rightCanvas.value) return

  // 获取容器实际像素大小
  const width = leftCanvas.value.parentElement.offsetWidth
  const height = leftCanvas.value.parentElement.offsetHeight

  // 设置物理像素
  ;[leftCanvas.value, rightCanvas.value].forEach(c => {
    c.width = width
    c.height = height
  })

  leftCtx = leftCanvas.value.getContext('2d', { willReadFrequently: false })
  rightCtx = rightCanvas.value.getContext('2d', { willReadFrequently: false })
  
  // 设置画笔样式
  ;[leftCtx, rightCtx].forEach(ctx => {
    ctx.strokeStyle = '#00d4ff'
    ctx.lineWidth = 4
    ctx.lineCap = 'round'
    ctx.lineJoin = 'round'
  })

  // 如果是描摹模式，绘制背景虚线
  if (selectedTask.value === 'trace') {
    drawTemplates(width, height)
  }
}

// 智能模版绘制系统
function drawTemplates(w, h) {
  const pad = 20
  const midX = w / 2
  const midY = h / 2
  const size = Math.min(w, h) / 2 - pad

  // 辅助函数：绘制虚线
  const drawGuide = (ctx, drawFn) => {
    ctx.save()
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)'
    ctx.setLineDash([8, 8])
    ctx.lineWidth = 3
    ctx.beginPath()
    drawFn(ctx)
    ctx.stroke()
    ctx.restore()
  }

  // 1. 左侧画板永远是基准 (例如画三角形)
  drawGuide(leftCtx, (ctx) => {
    if (selectedMode.value === 'dissociation') {
      // 分离模式：左圆
      ctx.arc(midX, midY, size, 0, Math.PI * 2)
    } else {
      // 其他模式：左三角
      ctx.moveTo(midX, midY - size)
      ctx.lineTo(midX - size, midY + size)
      ctx.lineTo(midX + size, midY + size)
      ctx.closePath()
    }
  })

  // 2. 右侧画板根据模式变化
  drawGuide(rightCtx, (ctx) => {
    if (selectedMode.value === 'mirror') {
      // 镜像模式：左右对称 (三角形翻转或保持对称中心)
      // 对于等腰三角形，镜像后看起来一样，为了明显，我们画直角三角形或者波浪更好
      // 这里演示简单的镜像逻辑：
      ctx.moveTo(midX, midY - size)
      ctx.lineTo(midX - size, midY + size) // 注意：这里视觉上其实是一样的
      ctx.lineTo(midX + size, midY + size)
      ctx.closePath()
    } else if (selectedMode.value === 'parallel') {
      // 平行模式：完全复制左侧 (同向)
      ctx.moveTo(midX, midY - size)
      ctx.lineTo(midX - size, midY + size)
      ctx.lineTo(midX + size, midY + size)
      ctx.closePath()
    } else if (selectedMode.value === 'dissociation') {
      // 分离模式：右方 (与左圆不同)
      ctx.rect(midX - size, midY - size, size * 2, size * 2)
    }
  })
}

// 全局触摸事件分发 (核心修复逻辑)
function handleGlobalTouch(type, event) {
  if (!leftCanvas.value || !rightCanvas.value) return

  const leftRect = leftCanvas.value.getBoundingClientRect()
  const rightRect = rightCanvas.value.getBoundingClientRect()
  const touches = event.changedTouches
  
  for (let i = 0; i < touches.length; i++) {
    const touch = touches[i]
    const cx = touch.clientX
    const cy = touch.clientY
    
    let target = null
    let rect = null
    
    // 判定触点属于哪个区域
    if (cx >= leftRect.left && cx <= leftRect.right && cy >= leftRect.top && cy <= leftRect.bottom) {
      target = 'left'
      rect = leftRect
    } else if (cx >= rightRect.left && cx <= rightRect.right && cy >= rightRect.top && cy <= rightRect.bottom) {
      target = 'right'
      rect = rightRect
    }

    if (!target) continue

    const x = cx - rect.left
    const y = cy - rect.top
    const ctx = target === 'left' ? leftCtx : rightCtx
    const pathArray = target === 'left' ? leftPaths : rightPaths

    if (type === 'start') {
      target === 'left' ? strokeCountLeft.value++ : strokeCountRight.value++
      ctx.beginPath()
      ctx.moveTo(x, y)
      pathArray.push({ x, y, t: Date.now() })
    } else if (type === 'move') {
      ctx.lineTo(x, y)
      ctx.stroke()
      ctx.beginPath()
      ctx.moveTo(x, y)
      pathArray.push({ x, y, t: Date.now() })
    } else if (type === 'end') {
      ctx.beginPath()
    }
  }
}

function clearCanvas() {
  if (leftCtx && rightCtx) {
    leftCtx.clearRect(0, 0, leftCanvas.value.width, leftCanvas.value.height)
    rightCtx.clearRect(0, 0, rightCanvas.value.width, rightCanvas.value.height)
    leftPaths = []
    rightPaths = []
    strokeCountLeft.value = 0
    strokeCountRight.value = 0
    // 如果是描摹模式，清除后要重绘模版
    initCanvas()
  }
}

function finishDrawing() {
  clearInterval(timerInterval)
  
  if (leftCanvas.value) leftCanvasImage.value = leftCanvas.value.toDataURL()
  if (rightCanvas.value) rightCanvasImage.value = rightCanvas.value.toDataURL()

  isDrawing.value = false
  trainingStore.endTraining()

  nextTick(() => {
    showResult.value = true
  })
  
  saveRecord()
}

function saveRecord() {
  // 计算新的评分系统分数
  const score = calculateMirrorScore()
  
  userStore.addTrainingRecord({
    moduleName: 'mirror',
    difficulty: trainingModes.find(m => m.value === selectedMode.value)?.name,
    score: Math.round(score),
    duration: drawingDuration.value,
    details: {
      mode: selectedMode.value,
      syncRate: syncScore.value,
      strokeCountLeft: strokeCountLeft.value,
      strokeCountRight: strokeCountRight.value
    }
  })
}

function calculateMirrorScore() {
  // 协调准确率分数 (70%) - 基于同步率
  const coordinationScore = syncScore.value

  // 反应速度分数 (20%) - 基于训练模式的标准反应时间
  const standardReactionTime = selectedMode.value === 'sync' ? 600 : 
                              selectedMode.value === 'mirror' ? 800 : 1000 // ms
  // 估算平均反应时间（基于笔画数和训练时长）
  const totalStrokes = strokeCountLeft.value + strokeCountRight.value
  const avgReactionTime = totalStrokes > 0 ? drawingDuration.value / totalStrokes : standardReactionTime
  const speedRatio = standardReactionTime / avgReactionTime
  const speedScore = Math.min(100, speedRatio * 100)

  // 协调稳定性分数 (10%) - 基于左右手笔画数量的一致性
  const total = strokeCountLeft.value + strokeCountRight.value
  const diff = Math.abs(strokeCountLeft.value - strokeCountRight.value)
  const stabilityScore = total > 0 ? Math.max(0, 100 - (diff / total) * 200) : 0

  // 最终分数
  const finalScore = coordinationScore * 0.7 + speedScore * 0.2 + stabilityScore * 0.1
  return Math.max(0, Math.min(100, finalScore))
}

function handleRetry() {
  showResult.value = false
  startDrawing()
}

function handleClose() {
  showResult.value = false
  goBack()
}

function goBack() {
  if (timerInterval) clearInterval(timerInterval)
  router.back()
}

function formatTime(ms) {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  const rs = s % 60
  return `${m}:${rs.toString().padStart(2, '0')}`
}

onMounted(() => {
  if (detectPC()) showPCWarning.value = true
})

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval)
})
</script>

<style lang="scss" scoped>
.mirror-page {
  min-height: 100vh;
  background: $bg-primary;
  color: $text-primary;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  touch-action: none;
}

// 头部样式
.page-header {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: $spacing-md $spacing-lg;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  position: fixed;
  top: env(safe-area-inset-top, 0px);
  left: 0;
  right: 0;
  z-index: 100;
  
  .back-button {
    @include button-reset;
    @include click-feedback;
    width: 40px;
    height: 40px;
    border-radius: $radius-full;
    background: rgba(255, 255, 255, 0.05);
    color: $text-primary;
    @include flex-center;
    position: absolute;
    left: $spacing-lg;
  }
  
  .page-title {
    font-size: $font-xl;
    font-weight: $font-semibold;
    margin: 0;
    text-align: center;
  }
  
  .help-button {
    @include button-reset;
    @include click-feedback;
    height: 40px;
    padding: 0 $spacing-md;
    border-radius: $radius-full;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: $accent-primary;
    display: flex;
    align-items: center;
    gap: $spacing-xs;
    position: absolute;
    right: $spacing-lg;
    transition: all $transition-base;
    font-size: $font-sm;
    font-weight: $font-medium;

    &:hover {
      background: rgba(0, 212, 255, 0.2);
      border-color: $accent-primary;
      transform: scale(1.05);
    }

    svg {
      flex-shrink: 0;
    }

    span {
      white-space: nowrap;
    }
  }

  .clear-button {
    @include button-reset;
    @include click-feedback;
    position: absolute;
    right: $spacing-lg;
    padding: $spacing-xs $spacing-md;
    border-radius: $radius-md;
    background: rgba(255, 51, 102, 0.1);
    border: 1px solid rgba(255, 51, 102, 0.3);
    color: $accent-error;
    font-size: $font-sm;
    font-weight: $font-medium;
    transition: all $transition-base;

    &:hover {
      background: rgba(255, 51, 102, 0.2);
      border-color: $accent-error;
    }
  }
}

// 配置界面样式
.config-screen {
  flex: 1;
  @include flex-center;
  padding: calc($spacing-md + 60px) $spacing-lg $spacing-md;
  overflow-y: auto;
  @include custom-scrollbar;
  touch-action: auto;

  @include mobile {
    padding: calc($spacing-md + 60px) $spacing-md $spacing-md;
  }
  
  .config-card {
    @include glass-card;
    padding: $spacing-2xl;
    max-width: 600px;
    width: 100%;
    box-shadow:
      0 20px 60px rgba(0, 0, 0, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);

    @include mobile {
      padding: $fluid-spacing-lg;
      max-width: 90vw;
    }
  }
  
  .section-title {
    font-size: $font-sm;
    color: $text-secondary;
    margin-bottom: $spacing-md;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: $font-medium;
    
    &.mt-6 { 
      margin-top: $spacing-xl; 
    }
  }
  
  // 模式列表
  .mode-list {
    display: flex;
    flex-direction: column;
    gap: $spacing-sm;
  }
  
  .mode-item {
    @include button-reset;
    @include click-feedback;
    display: flex;
    align-items: center;
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: $radius-md;
    padding: $spacing-md;
    color: $text-primary;
    text-align: left;
    transition: all $transition-base;
    
    &.active {
      background: rgba(0, 212, 255, 0.1);
      border-color: $accent-primary;
      box-shadow:
        0 0 20px rgba(0, 212, 255, 0.3),
        inset 0 0 20px rgba(0, 212, 255, 0.1);
    }

    &:hover:not(.active) {
      background: rgba(255, 255, 255, 0.1);
      border-color: rgba(0, 212, 255, 0.3);
    }
    
    .mode-icon {
      font-size: $font-2xl;
      margin-right: $spacing-md;
      flex-shrink: 0;
    }
    
    .mode-info {
      flex: 1;
      
      .mode-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: $spacing-xs;
        
        .name { 
          font-weight: $font-semibold;
          font-size: $font-base;
        }
        
        .stars {
          color: rgba(255, 255, 255, 0.2);
          font-size: $font-sm;
          
          .filled { 
            color: $accent-warning;
          }
        }
      }
      
      .desc {
        font-size: $font-sm;
        color: $text-secondary;
        line-height: 1.4;
      }
    }
  }
  
  // 任务切换
  .task-tabs {
    display: flex;
    background: rgba(0, 0, 0, 0.3);
    padding: $spacing-xs;
    border-radius: $radius-md;
    gap: $spacing-xs;
    
    .task-tab {
      @include button-reset;
      @include click-feedback;
      flex: 1;
      background: transparent;
      color: $text-secondary;
      padding: $spacing-sm;
      font-size: $font-sm;
      font-weight: $font-medium;
      border-radius: $radius-sm;
      transition: all $transition-base;
      
      &.active {
        background: rgba(255, 255, 255, 0.1);
        color: $text-primary;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      }
    }
  }
  
  .hint-box {
    margin-top: $spacing-lg;
    padding: $spacing-md;
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: $radius-md;
    color: $accent-primary;
    font-size: $font-sm;
    text-align: center;
    line-height: 1.5;
  }
  
  .start-button {
    @include button-reset;
    @include click-feedback;
    width: 100%;
    margin-top: $spacing-2xl;
    padding: $spacing-lg;
    background: linear-gradient(135deg, $accent-primary, $accent-secondary);
    border-radius: $radius-md;
    color: $text-primary;
    font-size: $font-lg;
    font-weight: $font-bold;
    box-shadow:
      0 8px 24px rgba(0, 212, 255, 0.3),
      0 0 40px rgba(0, 212, 255, 0.1);
    transition: all $transition-base;
    position: relative;
    overflow: hidden;

    @include mobile {
      padding: $spacing-md;
      font-size: $font-base;
    }

    &::before {
      content: '';
      position: absolute;
      top: 50%;
      left: 50%;
      width: 0;
      height: 0;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.3);
      transform: translate(-50%, -50%);
      transition:
        width 0.6s,
        height 0.6s;
    }

    &:hover {
      box-shadow:
        0 12px 32px rgba(0, 212, 255, 0.5),
        0 0 60px rgba(0, 212, 255, 0.3);

      &::before {
        width: 300px;
        height: 300px;
      }
    }
  }
}

// 绘图界面样式
.drawing-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: calc($spacing-md + 60px) $spacing-md $spacing-md;
  
  @include mobile {
    padding: calc($spacing-md + 60px) $spacing-sm $spacing-sm;
  }
  
  .instruction-banner {
    @include flex-center;
    gap: $spacing-sm;
    padding: $spacing-sm $spacing-md;
    color: $text-secondary;
    font-size: $font-sm;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: $radius-md;
    margin-bottom: $spacing-md;
    backdrop-filter: blur(10px);
    
    .icon {
      font-size: $font-lg;
    }
  }
  
  .canvas-container {
    flex: 1;
    display: flex;
    background: rgba(0, 0, 0, 0.3);
    border-radius: $radius-lg;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
    touch-action: none;
    transform: rotate(90deg);
    transform-origin: center center;
    box-shadow:
      0 8px 32px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.05);
    
    .divider {
      width: 2px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: $spacing-md;
      z-index: 5;
      background: linear-gradient(
        to bottom,
        transparent,
        rgba(0, 212, 255, 0.2),
        transparent
      );
      
      .line {
        width: 1px;
        flex: 1;
        background: linear-gradient(
          to bottom,
          transparent,
          rgba(255, 255, 255, 0.15),
          transparent
        );
      }
      
      .divider-icon {
        font-size: $font-sm;
        color: $accent-primary;
        text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
      }
    }
    
    .canvas-panel {
      flex: 1;
      position: relative;
      
      .panel-tag {
        position: absolute;
        top: $spacing-md;
        left: 0;
        right: 0;
        text-align: center;
        font-size: $font-xs;
        color: rgba(255, 255, 255, 0.2);
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: $font-semibold;
        pointer-events: none;
      }
      
      canvas {
        width: 100%;
        height: 100%;
        display: block;
      }
    }
  }
  
  .drawing-controls {
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 $spacing-sm;
    
    .timer {
      font-family: monospace;
      font-size: $font-xl;
      font-weight: $font-bold;
      color: $accent-primary;
      background: rgba(0, 212, 255, 0.1);
      border: 1px solid rgba(0, 212, 255, 0.3);
      padding: $spacing-sm $spacing-lg;
      border-radius: $radius-md;
      min-width: 80px;
      text-align: center;
    }
    
    .finish-button {
      @include button-reset;
      @include click-feedback;
      background: linear-gradient(135deg, $accent-primary, $accent-secondary);
      color: $text-primary;
      padding: $spacing-sm $spacing-xl;
      border-radius: $radius-md;
      font-weight: $font-semibold;
      font-size: $font-base;
      box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
      transition: all $transition-base;

      &:hover {
        box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
      }
    }
  }
}

// PC警告弹窗
.pc-warning-content {
  text-align: center;
  padding: $spacing-xl;
  color: $text-primary;
  
  .warning-icon {
    font-size: 48px;
    margin-bottom: $spacing-lg;
  }
  
  h2 { 
    font-size: $font-xl;
    font-weight: $font-bold;
    margin-bottom: $spacing-md;
    color: $text-primary;
  }
  
  .warning-text { 
    color: $text-secondary;
    margin-bottom: $spacing-xl;
    line-height: 1.6;
    font-size: $font-base;
  }
  
  .primary-button {
    @include button-reset;
    @include click-feedback;
    background: linear-gradient(135deg, $accent-primary, $accent-secondary);
    color: $text-primary;
    padding: $spacing-md $spacing-2xl;
    border-radius: $radius-md;
    font-size: $font-base;
    font-weight: $font-semibold;
    box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
    transition: all $transition-base;

    &:hover {
      box-shadow: 0 6px 20px rgba(0, 212, 255, 0.5);
    }
  }
}
</style>