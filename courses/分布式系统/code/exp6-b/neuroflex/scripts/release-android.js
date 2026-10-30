#!/usr/bin/env node
/**
 * Android 发布脚本
 * 自动更新版本、提交、打 tag 并推送
 * 
 * 用法：
 *   node scripts/release-android.js 1.0.3        # 发布指定版本
 *   node scripts/release-android.js --patch      # 自动升级 patch 版本
 *   node scripts/release-android.js --minor      # 自动升级 minor 版本
 */

import { execSync } from 'node:child_process'
import process from 'node:process'

function execCommand(command, options = {}) {
  console.log(`🔧 执行: ${command}`)
  try {
    const result = execSync(command, { 
      encoding: 'utf-8', 
      stdio: 'inherit',
      ...options 
    })
    return result
  } catch (error) {
    console.error(`❌ 命令执行失败: ${command}`)
    console.error(error.message)
    process.exit(1)
  }
}

function main() {
  const args = process.argv.slice(2)
  
  if (args.length === 0) {
    console.log('❌ 请指定版本号或升级类型')
    console.log('用法:')
    console.log('  node scripts/release-android.js 1.0.3')
    console.log('  node scripts/release-android.js --patch')
    console.log('  node scripts/release-android.js --minor')
    process.exit(1)
  }

  const arg = args[0]
  let syncCommand = 'node scripts/sync-version.js'

  if (arg === '--patch') {
    syncCommand += ' --bump patch --app-only'
  } else if (arg === '--minor') {
    syncCommand += ' --bump minor --app-only'
  } else if (arg === '--major') {
    syncCommand += ' --bump major --app-only'
  } else {
    // 指定版本号
    syncCommand += ` ${arg} --app-only`
  }

  console.log('🚀 开始 Android 发布流程...\n')

  // 1. 更新版本
  console.log('📝 步骤 1: 更新版本号')
  execCommand(syncCommand)

  // 2. 获取更新后的版本号
  const versionOutput = execSync('node -p "JSON.parse(require(\'fs\').readFileSync(\'android/app/build.gradle\', \'utf-8\').match(/versionName\\s+\\"([^"]+)\\"/)[1])"', { encoding: 'utf-8' }).trim()
  const version = versionOutput.replace(/"/g, '')
  
  console.log(`\n📦 当前版本: ${version}`)

  // 3. 提交更改
  console.log('\n📝 步骤 2: 提交版本更改')
  execCommand('git add android/app/build.gradle public/app-version.json')
  execCommand(`git commit -m "chore: bump Android version to ${version}"`)

  // 4. 创建并推送 tag
  console.log('\n🏷️ 步骤 3: 创建并推送 tag')
  const tagName = `android-v${version}`
  execCommand(`git tag ${tagName}`)
  execCommand(`git push origin main`)
  execCommand(`git push origin ${tagName}`)

  console.log(`\n✅ 发布完成！`)
  console.log(`   版本: ${version}`)
  console.log(`   Tag: ${tagName}`)
  console.log(`   GitHub Actions 将自动构建并发布 APK`)
  console.log(`\n🔗 查看构建状态: https://github.com/IT-NuanxinPro/NeuroFlex/actions`)
}

main()