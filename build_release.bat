@echo off
setlocal
cd /d "%~dp0"

echo.
echo === Building YT Archiver CLI ===
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --console ^
    --name yt-archiver ^
    --paths src ^
    --distpath dist\release ^
    --workpath build\pyinstaller-cli ^
    src\yt_archiver\cli.py

if errorlevel 1 (
    echo.
    echo CLI build failed.
    exit /b 1
)

echo.
echo === Building YT Archiver GUI ===
python -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name yt-archiver-gui ^
    --paths src ^
    --distpath dist\release ^
    --workpath build\pyinstaller-gui ^
    src\yt_archiver\ui\app.py

if errorlevel 1 (
    echo.
    echo GUI build failed.
    exit /b 1
)

echo.
echo === Build complete ===
echo Your executables are in dist\release\
dir dist\release\*.exe