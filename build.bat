@echo off
echo ========================================
echo Claude Config Switcher 快速打包工具
echo ========================================

echo 正在运行打包脚本...
python build_exe.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo 打包完成！
    echo 可执行文件位于 dist 目录中
    pause
) else (
    echo.
    echo 打包过程中出现错误
    pause
)
