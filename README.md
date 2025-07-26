# Claude Code 配置切换器

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-orange.svg" alt="GUI">
</p>

一个现代化、用户友好的桌面应用程序，用于管理多个 Claude CLI 配置文件，轻松在不同的 Claude Code 配置之间切换。

## ✨ 主要功能

- 🔄 **轻松切换配置** - 一键切换 Claude Code 配置文件
- 👁️ **实时预览** - 切换前预览配置内容
- 🎯 **智能识别** - 可视化指示器显示活动和同步状态
- 🗂️ **有序管理** - 简洁现代的界面管理多个配置
- 🌙 **深色主题** - 专业的深色主题与现代样式
- 💨 **轻量快速** - 快速响应的桌面应用程序


## 🚀 快速开始

### 下载运行

1. **下载** 最新版本 [发布页面](../../releases)
2. **运行** `cc-switcher.exe`

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/x-sunny43/cc-switcher.git
cd claude-config-switcher

# 安装依赖
uv sync

# 运行应用
python cc_switcher.py
```

## 📦 从源码构建

我们提供多种构建可执行文件的方式：

### 方法一：自动构建脚本（推荐）
```bash
python build_exe.py
```

### 方法二：批处理脚本（Windows）
```bash
# 双击运行或命令行执行
build.bat
```

### 方法三：手动构建
```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ClaudeConfigSwitcher cc_switcher.py
```

生成的可执行文件位于 `dist/` 目录中。

## 🎯 工作原理

1. **扫描**：应用自动扫描 `~/.claude` 目录中的配置文件
2. **预览**：点击任意配置文件预览其内容
3. **切换**：点击"切换"按钮激活选中的配置
4. **备份**：自动备份之前的设置并添加时间戳

## 🔧 系统要求

- **Python 3.11+**（从源码运行时需要）
- **Windows 10/11**（主要支持平台）
- **~/.claude 目录** 包含 Claude CLI 配置文件

### 开发依赖
- `customtkinter >= 5.2.2` - 现代化 GUI 框架
- `pyinstaller >= 6.14.2` - 构建可执行文件

## 📁 项目结构

```
claude-config-switcher/
├── cc_switcher.py          # 主应用程序
├── build_exe.py            # 构建脚本
├── build.bat               # Windows 构建包装器
├── pyproject.toml          # 项目配置
├── README.md               # 本文件
└── CLAUDE.md               # 开发指南
```

## 🤝 参与贡献

欢迎贡献代码！以下是参与方式：

1. **Fork** 本仓库
2. **创建** 功能分支（`git checkout -b feature/amazing-feature`）
3. **提交** 更改（`git commit -m 'Add amazing feature'`）
4. **推送** 到分支（`git push origin feature/amazing-feature`）
5. **创建** Pull Request

### 开发环境设置

```bash
# 克隆你的 fork
git clone https://github.com/your-username/claude-config-switcher.git
cd claude-config-switcher

# 安装开发依赖
pip install -e .

# 运行应用
python cc_switcher.py
```

## 🐛 Bug 报告与功能请求

发现 Bug 或有功能建议？请 [提交 Issue](../../issues)：

- **Bug 报告**：复现步骤、预期行为、相关截图
- **功能请求**：详细描述建议功能和使用场景

## 📄 开源协议

本项目采用 MIT 协议 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - 提供现代化 GUI 框架
- [Claude CLI](https://claude.ai) - 本工具支持的优秀 AI 助手
- 所有帮助改进项目的贡献者

## 📊 项目统计

- **开发语言**：Python
- **GUI 框架**：CustomTkinter
- **构建工具**：PyInstaller
- **目标平台**：Windows（跨平台代码）
