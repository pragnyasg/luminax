@echo off
set "PATH=C:\src\flutter\bin;%PATH%"
cd /d "%~dp0"
echo ============================================================
echo   LUMI Caregiver Mobile Application - Quick Launcher
echo ============================================================
echo.
echo [1/3] Checking Flutter environment...
call flutter --version
echo.
echo [2/3] Resolving dependencies...
call flutter pub get
echo.
echo [3/3] Launching LUMI Caregiver App on Chrome...
echo (You can also run "flutter run -d windows" for Windows native)
echo.
call flutter run -d chrome
pause
