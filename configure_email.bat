@echo off
echo ========================================
echo Email Configuration Setup
echo ========================================
echo.

REM Check if .env already exists
if exist .env (
    echo .env file already exists
    echo Opening for editing...
    echo.
    notepad .env
) else (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo ========================================
    echo .env file created!
    echo ========================================
    echo.
    echo Opening for editing...
    echo.
    echo PLEASE UPDATE:
    echo   1. EMAIL_HOST_USER - Your email address
    echo   2. EMAIL_HOST_PASSWORD - Your app password
    echo   3. DEFAULT_FROM_EMAIL - Your clinic email
    echo.
    echo For Gmail users:
    echo   - Generate App Password at: https://myaccount.google.com/apppasswords
    echo   - Use that password in EMAIL_HOST_PASSWORD
    echo.
    notepad .env
)

echo.
echo After saving, the email configuration will be ready!
echo.
pause
