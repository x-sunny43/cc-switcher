@echo off
chcp 65001 >nul
echo ========================================
echo Claude Config Switcher Build Tool
echo ========================================

echo Running build script...
python build_exe.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Build completed successfully!
    echo Executable file is in the dist directory
    pause
) else (
    echo.
    echo Build process encountered an error
    pause
)
