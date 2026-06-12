@echo off
REM ============================================================
REM  動画2分割ツール - Windows用ビルドスクリプト
REM  ffmpeg を自動ダウンロードして同梱し、単体の .exe を作ります。
REM  このファイルをダブルクリックするか、コマンドプロンプトで実行してください。
REM ============================================================
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo === 動画2分割ツール ビルド開始 ===

REM --- Python の確認 ---
where python >nul 2>nul
if errorlevel 1 (
    echo [エラー] Python が見つかりません。https://www.python.org/ からインストールし、
    echo         インストール時に "Add Python to PATH" にチェックを入れてください。
    pause
    exit /b 1
)

REM --- PyInstaller のインストール ---
echo --- PyInstaller を準備中 ---
python -m pip install --upgrade pip >nul
python -m pip install pyinstaller || (
    echo [エラー] PyInstaller のインストールに失敗しました。
    pause
    exit /b 1
)

REM --- ffmpeg / ffprobe の用意（bin\ に無ければダウンロード）---
if not exist "bin" mkdir "bin"
if exist "bin\ffmpeg.exe" if exist "bin\ffprobe.exe" goto have_ffmpeg

echo --- ffmpeg をダウンロード中（数十MB、少し時間がかかります）---
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ErrorActionPreference='Stop';" ^
  "$url='https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip';" ^
  "$zip=Join-Path $env:TEMP 'ffmpeg_dl.zip';" ^
  "$ex=Join-Path $env:TEMP 'ffmpeg_ex';" ^
  "Write-Host 'downloading...';" ^
  "Invoke-WebRequest -Uri $url -OutFile $zip;" ^
  "if (Test-Path $ex) { Remove-Item -Recurse -Force $ex };" ^
  "Expand-Archive -Path $zip -DestinationPath $ex -Force;" ^
  "$fm=Get-ChildItem -Path $ex -Recurse -Filter ffmpeg.exe | Select-Object -First 1;" ^
  "$fp=Get-ChildItem -Path $ex -Recurse -Filter ffprobe.exe | Select-Object -First 1;" ^
  "Copy-Item $fm.FullName 'bin\ffmpeg.exe' -Force;" ^
  "Copy-Item $fp.FullName 'bin\ffprobe.exe' -Force;" ^
  "Remove-Item $zip -Force; Remove-Item -Recurse -Force $ex;" ^
  "Write-Host 'ffmpeg ready';"
if errorlevel 1 (
    echo [エラー] ffmpeg のダウンロードに失敗しました。
    echo         手動で ffmpeg.exe と ffprobe.exe を bin\ フォルダに置いてから再実行してください。
    pause
    exit /b 1
)

:have_ffmpeg
echo --- ffmpeg を同梱して .exe をビルド中 ---

REM 既存のビルド成果物を掃除
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

pyinstaller --noconfirm --onefile --windowed --name VideoSplitter ^
  --add-binary "bin\ffmpeg.exe;bin" ^
  --add-binary "bin\ffprobe.exe;bin" ^
  app.py
if errorlevel 1 (
    echo [エラー] ビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  ビルド完了！
echo  dist\VideoSplitter.exe を相手に渡してください。
echo  （Python も ffmpeg も不要で、ダブルクリックで動きます）
echo ============================================================
echo.
pause
endlocal
