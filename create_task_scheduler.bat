@echo off
echo ========================================
echo Creating Windows Task Scheduler Task
echo ========================================
echo.
echo This will create a scheduled task to run reminders every 30 minutes
echo.
echo Task Details:
echo   Name: Appointment Reminders
echo   Schedule: Every 30 minutes, all day
echo   Start: 6:00 AM daily
echo.

set PYTHON_PATH=C:\Users\it.sm\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\python.exe
set WORKING_DIR=%~dp0
set SCRIPT_PATH=%WORKING_DIR%manage.py

echo Creating task with:
echo   Python: %PYTHON_PATH%
echo   Script: %SCRIPT_PATH%
echo   Working Directory: %WORKING_DIR%
echo.

REM Create the task
schtasks /Create /TN "Appointment Reminders" /TR "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\" send_appointment_reminders" /SC DAILY /ST 06:00 /RI 30 /DU 24:00 /F /RU "%USERNAME%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Task created successfully
    echo ========================================
    echo.
    echo The task will:
    echo   - Run every 30 minutes
    echo   - Start at 6:00 AM daily
    echo   - Send appointment reminders automatically
    echo.
    echo To view/edit the task:
    echo   1. Open Task Scheduler
    echo   2. Look for "Appointment Reminders"
    echo.
    echo To test immediately:
    echo   schtasks /Run /TN "Appointment Reminders"
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR: Failed to create task
    echo ========================================
    echo.
    echo Please run this script as Administrator
    echo Right-click and select "Run as administrator"
    echo.
)

pause
