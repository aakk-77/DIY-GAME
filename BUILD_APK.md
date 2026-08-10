# 植物大战僵尸·杂交版 —— 手机版 APK 打包说明

本项目包含两个版本：

| 版本 | 入口 | 框架 | 运行平台 |
|------|------|------|----------|
| 桌面版 | `main.py` | pygame | Windows / macOS / Linux |
| 手机版 | `mobile/main.py` | Kivy | Android（可打包 APK） |

> **关于“安装包”**：Python 跨平台应用打包成 Android APK 需要 Linux 环境下的
> `buildozer` 工具链（依赖 Android SDK/NDK，体量很大，无法在 Windows 上直接生成
> 真机 APK）。下面给出**三种**从代码得到手机安装包的方式，任选其一。

---

## 方式一：Buildozer（官方推荐，产出 `.apk`）

> 需要一台 Linux 机器（或 WSL2 / Docker / GitHub Actions，Windows 原生不支持）。

1. 安装 buildozer 依赖（Ubuntu/Debian 示例）：

   ```bash
   sudo apt update
   sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool \
       pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 \
       cmake libffi-dev libssl-dev
   pip3 install --user buildozer cython==0.29.36
   ```

2. 进入项目根目录（`buildozer.spec` 所在处）：

   ```bash
   cd pvz_hybrid
   ```

3. 一键构建 APK（首次会自动下载 Android SDK/NDK，耗时较长）：

   ```bash
   buildozer -v android debug
   ```

4. 构建完成后，APK 位于：

   ```
   bin/pvzhybrid-1.0.0-debug.apk
   ```

5. 把该 `.apk` 传到手机安装即可（需在手机设置里允许“未知来源安装”）。

### 签名发布版

```bash
buildozer -v android release
```

会生成未签名 release apk，再用 `keytool` + `jarsigner`（或 `apksigner`）签名。
详见 https://buildozer.readthedocs.io

---

## 方式二：GitHub Actions 云端打包（无需本地 Linux，推荐）

本项目已自带 workflow 文件 `.github/workflows/build-apk.yml`，开箱即用：

1. 在 GitHub 新建一个仓库，把本项目推送上去（保证仓库根目录能看到
   `buildozer.spec` 与 `mobile/` 目录，或把整个 `pvz_hybrid/` 文件夹作为仓库根）。
2. 进入仓库的 **Actions** 标签页，选择 **Build Android APK** 工作流。
3. 点 **Run workflow** 手动触发，或在推送 / 打 `v*` 标签时自动触发。
4. 构建完成后（首次约 20–30 分钟），在该次运行页面底部的 **Artifacts** 区
   下载 `pvzhybrid-apk`，解压即得到 `*.apk` 安装包。

workflow 做了什么：

- 自动下载开源中文字体 **Noto Sans SC**（思源黑体子集）并打进 APK，避免中文变方块
- 用 `ArtemSBulgakov/buildozer-action` 调用官方 Buildozer Docker 镜像构建
- 缓存 `.buildozer` 工具链加速二次构建
- 打 `v*` 标签时自动把 APK 发布到 GitHub Release

> 仅打 `arm64-v8a` 一个架构以减小体积、加快速度；如需兼容老 32 位手机，
> 把 `buildozer.spec` 的 `android.archs` 改为 `armeabi-v7a,arm64-v8a`。

---

## 方式三：桌面先跑 Kivy 版验证（Windows 可直接运行）

安装 Kivy 后可在电脑上预览手机版效果（触屏逻辑用鼠标模拟）：

```bash
pip install kivy
cd pvz_hybrid
python mobile/main.py
```

确认无误后再按方式一/二打包真机 APK。

---

## 打包中文字体（重要）

Kivy 默认字体不含中文，APK 内中文会变方块。两种解决：

- **A（推荐）**：把一个开源中文字体（如 `SourceHanSansSC-Regular.otf` 或
  `wqy-microhei.ttc`）放到 `mobile/` 目录，然后编辑 `mobile/main.py` 顶部：
  ```python
  CJK_FONT = "wqy-microhei.ttc"   # 改成你的字体文件名
  ```
  并确认 `buildozer.spec` 里 `source.include_exts` 包含 `ttf,ttc,otf`（已默认包含）。

- **B**：直接复制 Windows 的 `C:\Windows\Fonts\msyh.ttc` 到 `mobile/` 并改名引用。

---

## buildozer.spec 关键配置说明

| 字段 | 值 | 说明 |
|------|----|------|
| `source.dir` | `mobile` | 入口 `main.py` 所在目录 |
| `requirements` | `python3,kivy` | 仅依赖 kivy |
| `orientation` | `landscape` | 横屏（PvZ 经典视角） |
| `android.archs` | `arm64-v8a` | 只打 64 位，体积更小 |

如需兼容老旧 32 位手机，把 `android.archs` 改为
`armeabi-v7a,arm64-v8a`。

---

## 手机版操作

- 点击顶部植物卡片选中 → 点击草地空格种植
- 点击天上/地上的阳光收集
- 点击铲子 → 点植物可移除
- 屏蔽返回键：暂停/继续；游戏结束后点屏幕重开
