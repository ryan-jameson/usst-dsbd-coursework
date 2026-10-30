#!/usr/bin/env node
/**
 * Android 版本管理脚本
 * 支持 Web/H5 和 Android APP 独立版本管理
 *
 * 用法：
 *   node scripts/sync-version.js [version] [--bump patch|minor|major] [--app-only]
 *
 * 示例：
 *   node scripts/sync-version.js                    # 同步 package.json 版本到 Android
 *   node scripts/sync-version.js 1.0.0              # 设置指定版本（同时更新 package.json 和 Android）
 *   node scripts/sync-version.js 1.0.0 --app-only   # 仅设置 Android 版本，不更新 package.json
 *   node scripts/sync-version.js --bump patch       # 升级 package.json 并同步到 Android
 *   node scripts/sync-version.js --bump patch --app-only  # 仅升级 Android 版本
 */

import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT_DIR = path.resolve(__dirname, '..')

const PACKAGE_JSON_PATH = path.join(ROOT_DIR, 'package.json')
const BUILD_GRADLE_PATH = path.join(ROOT_DIR, 'android/app/build.gradle')
const APP_VERSION_PATH = path.join(ROOT_DIR, 'public/app-version.json')

/**
 * 解析版本号
 */
function parseVersion(version) {
  const match = version.match(/^(\d+)\.(\d+)\.(\d+)$/)
  if (!match) {
    throw new Error(`无效的版本号格式: ${version}，应为 x.y.z`)
  }
  return {
    major: Number.parseInt(match[1], 10),
    minor: Number.parseInt(match[2], 10),
    patch: Number.parseInt(match[3], 10),
  }
}

/**
 * 版本号升级
 */
function bumpVersion(version, type) {
  const { major, minor, patch } = parseVersion(version)

  switch (type) {
    case 'major':
      return `${major + 1}.0.0`
    case 'minor':
      return `${major}.${minor + 1}.0`
    case 'patch':
      return `${major}.${minor}.${patch + 1}`
    default:
      throw new Error(`无效的升级类型: ${type}`)
  }
}

/**
 * 计算 Android versionCode
 * 规则：major * 10000 + minor * 100 + patch
 * 例如：1.2.3 -> 10203
 */
function calculateVersionCode(version) {
  const { major, minor, patch } = parseVersion(version)
  return major * 10000 + minor * 100 + patch
}

/**
 * 读取 package.json 版本
 */
function getPackageVersion() {
  const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf-8'))
  return pkg.version
}

/**
 * 读取当前 Android 版本
 */
function getAndroidVersion() {
  if (!fs.existsSync(BUILD_GRADLE_PATH)) {
    return null
  }

  const content = fs.readFileSync(BUILD_GRADLE_PATH, 'utf-8')
  const versionNameMatch = content.match(/versionName\s+"([^"]+)"/)
  return versionNameMatch ? versionNameMatch[1] : null
}

/**
 * 读取 app-version.json 中的版本
 */
function getAppVersionJson() {
  if (!fs.existsSync(APP_VERSION_PATH)) {
    return null
  }

  try {
    const content = JSON.parse(fs.readFileSync(APP_VERSION_PATH, 'utf-8'))
    return content.version
  } catch {
    return null
  }
}

/**
 * 更新 package.json 版本
 */
function updatePackageVersion(newVersion) {
  const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON_PATH, 'utf-8'))
  pkg.version = newVersion
  fs.writeFileSync(PACKAGE_JSON_PATH, `${JSON.stringify(pkg, null, 2)}\n`)
  console.log(`✅ package.json 版本已更新为 ${newVersion}`)
}

/**
 * 更新 build.gradle 版本
 */
function updateBuildGradle(versionName, versionCode) {
  if (!fs.existsSync(BUILD_GRADLE_PATH)) {
    console.log(`⚠️ build.gradle 文件不存在: ${BUILD_GRADLE_PATH}`)
    return
  }

  let content = fs.readFileSync(BUILD_GRADLE_PATH, 'utf-8')

  // 更新 versionCode
  content = content.replace(
    /versionCode\s+\d+/,
    `versionCode ${versionCode}`,
  )

  // 更新 versionName
  content = content.replace(
    /versionName\s+"[^"]+"/,
    `versionName "${versionName}"`,
  )

  fs.writeFileSync(BUILD_GRADLE_PATH, content)
  console.log(`✅ build.gradle 已更新：versionName="${versionName}", versionCode=${versionCode}`)
}

/**
 * 更新 app-version.json
 */
function updateAppVersionJson(version, versionCode) {
  if (!fs.existsSync(APP_VERSION_PATH)) {
    console.log(`⚠️ app-version.json 文件不存在，跳过更新`)
    return
  }

  try {
    const content = JSON.parse(fs.readFileSync(APP_VERSION_PATH, 'utf-8'))
    content.version = version
    content.versionCode = versionCode
    
    // 更新下载链接
    const baseUrl = 'https://download-neuroflex.061129.xyz'
    const githubUrl = 'https://github.com/IT-NuanxinPro/NeuroFlex/releases/download'
    content.downloadUrl = `${baseUrl}/android-v${version}/NeuroFlex-v${version}.apk`
    content.githubUrl = `${githubUrl}/android-v${version}/NeuroFlex-v${version}.apk`
    
    fs.writeFileSync(APP_VERSION_PATH, `${JSON.stringify(content, null, 2)}\n`)
    console.log(`✅ app-version.json 已更新为 ${version}`)
  } catch (error) {
    console.log(`⚠️ 更新 app-version.json 失败: ${error.message}`)
  }
}

/**
 * 主函数
 */
function main() {
  const args = process.argv.slice(2)

  let newVersion = null
  let bumpType = null
  let appOnly = false

  // 解析参数
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--bump' && args[i + 1]) {
      bumpType = args[i + 1]
      i++
    } else if (args[i] === '--app-only') {
      appOnly = true
    } else if (!args[i].startsWith('-')) {
      newVersion = args[i]
    }
  }

  // 获取当前版本信息
  const packageVersion = getPackageVersion()
  const androidVersion = getAndroidVersion()
  const appVersionJson = getAppVersionJson()

  console.log(`📦 Package.json 版本: ${packageVersion}`)
  console.log(`🤖 Android 版本: ${androidVersion || '未设置'}`)
  console.log(`📱 App-version.json 版本: ${appVersionJson || '未设置'}`)

  // 确定目标版本
  if (newVersion) {
    // 使用指定版本
    parseVersion(newVersion) // 验证格式
  } else if (bumpType) {
    // 自动升级
    const baseVersion = appOnly ? (androidVersion || packageVersion) : packageVersion
    newVersion = bumpVersion(baseVersion, bumpType)
    console.log(`🚀 版本升级 (${bumpType}): ${baseVersion} -> ${newVersion}`)
  } else {
    // 仅同步 package.json 版本到 Android
    newVersion = packageVersion
    console.log('🔄 同步 package.json 版本到 Android...')
  }

  // 计算 versionCode
  const versionCode = calculateVersionCode(newVersion)
  console.log(`📱 Android versionCode: ${versionCode}`)

  // 更新文件
  if (!appOnly && newVersion !== packageVersion) {
    updatePackageVersion(newVersion)
  }
  
  updateBuildGradle(newVersion, versionCode)
  updateAppVersionJson(newVersion, versionCode)

  console.log('\n✨ 版本同步完成!')
  console.log(`   ${appOnly ? 'Android' : 'Web/Android'} 版本号: ${newVersion}`)
  console.log(`   versionCode: ${versionCode}`)
  
  if (appOnly) {
    console.log(`   Package.json 版本保持: ${packageVersion}`)
  }
}

main()