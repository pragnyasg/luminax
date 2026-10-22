@echo off
set "PATH=C:\src\flutter\bin;%PATH%"
cd /d "%~dp0"
echo ============================================================
echo   Running LUMI Caregiver Mobile Application Test Suite
echo ============================================================
echo.
call flutter test
echo.
pause
