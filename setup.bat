@echo off
setlocal enabledelayedexpansion

if "%~1"=="" (
  set "WORKSPACE_ROOT=%CD%"
) else (
  set "WORKSPACE_ROOT=%~1"
)

cd /d "%~dp0"
set "REPO_ROOT=%CD%"

where python >nul 2>&1
if errorlevel 1 (
  where py >nul 2>&1
  if errorlevel 1 (
    echo ERROR: Python is not available on PATH.
    exit /b 1
  ) else (
    set "PYTHON_CMD=py -3"
  )
) else (
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python virtual environment in .venv...
  %PYTHON_CMD% -m venv ".venv"
)

if not exist ".venv\Scripts\python.exe" (
  echo ERROR: Virtual environment python not found at .venv\Scripts\python.exe
  exit /b 1
)

set "VENV_PYTHON=.venv\Scripts\python.exe"

echo Upgrading pip, setuptools, and wheel...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel

if exist "requirements.txt" (
  echo Installing required dependencies...
  "%VENV_PYTHON%" -m pip install -r "requirements.txt"
)

echo Installing PECS-PRO in editable mode...
"%VENV_PYTHON%" -m pip install -e "%REPO_ROOT%"

echo Bootstrapping workspace: %WORKSPACE_ROOT%
"%VENV_PYTHON%" -m workspace_bridge_cli bootstrap-workspace "%WORKSPACE_ROOT%" --repo-root "%REPO_ROOT%" --upgrade

echo PECS onboarding completed successfully.
echo Run: "%VENV_PYTHON%" -m workspace_bridge_cli status "%WORKSPACE_ROOT%"
