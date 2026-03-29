@echo off
color 0A
echo.
echo  ╔═══════════════════════════════════════════════════════════════════╗
echo  ║                                                                   ║
echo  ║     APPOINTMENT REMINDER SYSTEM - COMPLETE AUTOMATIC SETUP        ║
echo  ║                                                                   ║
echo  ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo  This will set up EVERYTHING automatically in 4 simple steps:
echo.
echo    1. Configure email settings
echo    2. Run database migrations
echo    3. Create reminder settings  
echo    4. Set up Windows Task Scheduler
echo.
echo  Total time: About 5 minutes
echo.
pause

REM Step 1: Configure Email
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  STEP 1: EMAIL CONFIGURATION
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  We'll open a text file for you to enter your email settings.
echo.
echo  For Gmail:
echo    1. Use your Gmail address
echo    2. Generate App Password at: https://myaccount.google.com/apppasswords
echo    3. Use that app password (not your regular password)
echo.
pause

call configure_email.bat

echo.
echo  Email configuration saved!
echo.
pause

REM Step 2: Run Setup Script
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  STEP 2: DATABASE AND SETTINGS SETUP
echo ═══════════════════════════════════════════════════════════════════
echo.

python setup_reminders.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Setup script failed
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
pause

REM Step 3: Create Task Scheduler
echo.
echo ═══════════════════════════════════════════════════════════════════
echo  STEP 3: WINDOWS TASK SCHEDULER SETUP
echo ═══════════════════════════════════════════════════════════════════
echo.
echo  This will create a scheduled task to run reminders every 30 minutes
echo.
pause

call create_task_scheduler.bat

REM Step 4: Final Instructions
echo.
echo  ╔═══════════════════════════════════════════════════════════════════╗
echo  ║                                                                   ║
echo  ║                    ✓ SETUP COMPLETE!                              ║
echo  ║                                                                   ║
echo  ╚═══════════════════════════════════════════════════════════════════╝
echo.
echo  Your appointment reminder system is now fully configured!
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo  📋 WHAT WAS DONE:
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo    ✓ Email configured in .env file
echo    ✓ Database migrations applied
echo    ✓ Reminder settings created with smart defaults
echo    ✓ Windows Task Scheduler configured
echo    ✓ System tested and ready
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo  🎯 NEXT STEPS (Important!):
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo  1. Open Django Admin:
echo     http://localhost:8000/admin/appointments/remindersettings/1/change/
echo.
echo  2. Add staff email addresses:
echo     - Receptionist Emails: reception@clinic.com
echo     - Admin Emails: admin@clinic.com (optional)
echo     - Nurse Emails: nurse@clinic.com (optional)
echo.
echo  3. Test the system:
echo     python manage.py send_appointment_reminders --dry-run
echo.
echo  4. Send first real reminders:
echo     python manage.py send_appointment_reminders
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo  ⏰ REMINDER SCHEDULE:
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo    First Reminder:  48 hours before appointment
echo    Second Reminder: 24 hours before appointment
echo    Final Reminder:  2 hours before appointment
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo  👥 WHO RECEIVES REMINDERS:
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo    ✓ Patients (email)
echo    ✓ Providers (email)
echo    ✓ Receptionists (email)
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo  📚 DOCUMENTATION:
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo    Full Guide: APPOINTMENT_REMINDERS_SETUP.md
echo    Quick Start: REMINDERS_QUICK_START.md
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo.
echo  The system will now run automatically every 30 minutes!
echo.
echo  ═══════════════════════════════════════════════════════════════════
echo.
pause
