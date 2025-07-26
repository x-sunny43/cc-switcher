#!/usr/bin/env python3
"""
Claude Config Switcher打包脚本
使用PyInstaller将cc_switcher.py打包成exe文件
"""

import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller

        print(f"✓ PyInstaller已安装 (版本: {PyInstaller.__version__})")
        return True
    except ImportError:
        print("✗ PyInstaller未安装")
        return False


def install_pyinstaller():
    """安装PyInstaller"""
    print("正在安装PyInstaller...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pyinstaller"], check=True, capture_output=True, text=True
        )
        print("✓ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ PyInstaller安装失败: {e}")
        return False


def build_exe():
    """打包exe文件"""
    script_dir = Path(__file__).parent
    script_path = script_dir / "cc_switcher.py"

    if not script_path.exists():
        print(f"✗ 找不到脚本文件: {script_path}")
        return False

    print(f"正在打包: {script_path}")

    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 无控制台窗口
        "--name",
        "ClaudeConfigSwitcher",  # 输出文件名
        "--distpath",
        str(script_dir / "dist"),  # 输出目录
        "--workpath",
        str(script_dir / "build"),  # 临时文件目录
        "--specpath",
        str(script_dir),  # spec文件目录
        str(script_path),
    ]

    try:
        print("开始打包...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)

        if result.returncode == 0:
            exe_path = script_dir / "dist" / "ClaudeConfigSwitcher.exe"
            if exe_path.exists():
                print("✓ 打包成功!")
                print(f"  可执行文件位置: {exe_path}")
                print(f"  文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
                return True
            else:
                print("✗ 打包完成但找不到exe文件")
                return False
        else:
            print("✗ 打包失败:")
            print(result.stderr)
            return False

    except subprocess.CalledProcessError as e:
        print(f"✗ 打包过程出错: {e}")
        return False
    except FileNotFoundError:
        print("✗ 找不到pyinstaller命令，请确保PyInstaller已正确安装")
        return False


def clean_build_files():
    """清理构建文件"""
    script_dir = Path(__file__).parent

    # 要清理的目录和文件
    cleanup_paths = [script_dir / "build", script_dir / "__pycache__", script_dir / "ClaudeConfigSwitcher.spec"]

    print("清理构建文件...")
    for path in cleanup_paths:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
                print(f"  删除目录: {path}")
            else:
                path.unlink()
                print(f"  删除文件: {path}")


def main():
    """主函数"""
    print("=" * 50)
    print("Claude Config Switcher 打包工具")
    print("=" * 50)

    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python版本: {python_version}")

    # 检查并安装PyInstaller
    if not check_pyinstaller():
        if not install_pyinstaller():
            print("无法安装PyInstaller，请手动安装:")
            print("pip install pyinstaller")
            return 1

    # 检查依赖
    print("\n检查依赖包...")
    required_packages = ["customtkinter"]
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (缺失)")
            missing_packages.append(package)

    if missing_packages:
        print("\n需要安装缺失的包:")
        for package in missing_packages:
            print(f"pip install {package}")

        answer = input("\n是否现在安装这些包? (y/n): ").lower().strip()
        if answer in ['y', 'yes']:
            for package in missing_packages:
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", package], check=True, capture_output=True, text=True
                    )
                    print(f"✓ {package} 安装成功")
                except subprocess.CalledProcessError:
                    print(f"✗ {package} 安装失败")
                    return 1
        else:
            print("请先安装缺失的包再重新运行此脚本")
            return 1

    # 开始打包
    print("\n" + "=" * 30)
    success = build_exe()

    # 询问是否清理构建文件
    if success:
        print("\n" + "=" * 30)
        answer = input("是否清理构建文件? (y/n): ").lower().strip()
        if answer in ['y', 'yes']:
            clean_build_files()

    print("\n完成!")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
