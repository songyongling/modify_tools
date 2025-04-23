@echo off
echo Building File Renaming Tool...

echo 1. Terminating any running processes
taskkill /F /IM "文件重命名工具.exe" 2>nul
timeout /t 2 /nobreak >nul

echo 2. Cleaning up directories
rd /s /q "dist" 2>nul
rd /s /q "build" 2>nul
rd /s /q "__pycache__" 2>nul
timeout /t 1 /nobreak >nul

echo 3. Running PyInstaller build
pyinstaller --clean --noconfirm 文件重命名工具.spec

echo Done!
echo Build results are in the dist\文件重命名工具 directory
pause 