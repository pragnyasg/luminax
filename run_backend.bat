@echo off
setlocal
cd /d "%~dp0"

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting LUMI Caregiver Backend using %PYTHON_EXE%...
"%PYTHON_EXE%" -m lumi_backend.run_server %*
endlocal
