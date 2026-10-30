/**
 * 调试工具：验证视口和APK适配器是否正常工作
 */

export function debugViewportFix() {
  console.log('🔍 调试视口修复工具...')
  
  try {
    // 检查CSS变量是否设置
    const vh = document.documentElement.style.getPropertyValue('--vh')
    const viewportHeight = document.documentElement.style.getPropertyValue('--viewport-height')
    
    console.log('✅ CSS变量设置:', {
      '--vh': vh || '未设置',
      '--viewport-height': viewportHeight || '未设置'
    })
    
    // 检查body类名
    const bodyClasses = Array.from(document.body.classList)
    console.log('✅ Body类名:', bodyClasses)
    
    // 检查视口信息
    console.log('✅ 视口信息:', {
      innerWidth: window.innerWidth,
      innerHeight: window.innerHeight,
      devicePixelRatio: window.devicePixelRatio
    })
    
    return true
  } catch (error) {
    console.error('❌ 视口修复工具调试失败:', error)
    return false
  }
}

export function debugAPKAdapter() {
  console.log('🔍 调试APK适配器...')
  
  try {
    // 检查设备检测
    const userAgent = navigator.userAgent.toLowerCase()
    const isAndroid = /android/.test(userAgent)
    const isIOS = /iphone|ipad|ipod/.test(userAgent)
    const isMobile = isAndroid || isIOS || window.innerWidth <= 768
    
    console.log('✅ 设备检测:', {
      userAgent: userAgent.substring(0, 50) + '...',
      isAndroid,
      isIOS,
      isMobile,
      screenSize: `${window.screen.width}x${window.screen.height}`
    })
    
    // 检查安全区域
    const safeAreaInsets = {
      top: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-top'),
      right: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-right'),
      bottom: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-bottom'),
      left: getComputedStyle(document.documentElement).getPropertyValue('--safe-area-inset-left')
    }
    
    console.log('✅ 安全区域:', safeAreaInsets)
    
    return true
  } catch (error) {
    console.error('❌ APK适配器调试失败:', error)
    return false
  }
}

// 自动运行调试（仅在开发环境）
if (process.env.NODE_ENV === 'development') {
  // 延迟执行，确保DOM加载完成
  setTimeout(() => {
    console.log('🚀 开始调试移动端适配...')
    debugViewportFix()
    debugAPKAdapter()
  }, 1000)
}