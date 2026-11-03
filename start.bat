@echo off
setlocal enabledelayedexpansion

title RAINFALL ATLAS - 3D Climate Intelligence Platform

echo ===============================================================================
echo            RAINFALL ATLAS - 3D CLIMATE INTELLIGENCE PLATFORM
echo          Natural Rainfall Regime Discovery from Historical Patterns
echo ===============================================================================
echo.

:: Check for python in PATH
where python >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=python"
    goto :RUN_APP
)

:: Check for py launcher
where py >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :RUN_APP
)

:: Fallback check common Python installation paths
if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    goto :RUN_APP
)

if exist "%ProgramFiles%\Python310\python.exe" (
    set "PYTHON_CMD=%ProgramFiles%\Python310\python.exe"
    goto :RUN_APP
)

echo [ERROR] Python was not found in your system PATH or standard folders!
echo Please make sure Python 3.10+ is installed and check "Add Python to PATH".
echo.
pause
exit /b 1

:RUN_APP
echo Starting Rainfall Atlas using: %PYTHON_CMD%
echo.
%PYTHON_CMD% run.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] The application exited with an error.
    pause
)
