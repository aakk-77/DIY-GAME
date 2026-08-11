[app]

# 应用元信息
title = 植物大战僵尸·杂交版
package.name = pvzhybrid
package.domain = org.pvzhybrid

# 源码目录（mobile/ 下的 main.py 为入口）
source.dir = mobile
# 包含 otf 字体（NotoSansSC-Regular.otf 由 CI 下载到 mobile/）
source.include_exts = py,png,jpg,ttf,ttc,otf,txt

# 版本
version = 1.0.0

# 依赖：仅 kivy（图形由 Kivy Canvas 程序化绘制，无需 pygame/外部素材）
requirements = python3,kivy

# 横屏
orientation = landscape

# 全屏
fullscreen = 1

# Android 权限：本游戏无需任何特殊权限
android.permissions =

# Android API 版本（自动下载对应 SDK/NDK）
android.api = 34
android.minapi = 21
android.accept_sdk_license = True

# 减少 ABI 以加快构建：只打 arm64（绝大多数现代手机）
android.archs = arm64-v8a

# 关闭无用服务
services =

# 日志
log_level = 2

# presplash / icon 可选；留空使用默认
# presplash.filename = %(source.dir)s/presplash.png
# icon.filename = %(source.dir)s/icon.png

[buildozer]
log_level = 2
warn_on_root = 1
