@echo off
echo ============================================
echo  PDF Email Support Installation
echo ============================================
echo.
echo This will install xhtml2pdf for PDF generation
echo (Alternative: weasyprint - better quality but requires GTK)
echo.
pause

echo Installing xhtml2pdf...
pip install xhtml2pdf>=0.2.11

echo.
echo ============================================
if %ERRORLEVEL% EQU 0 (
    echo ✓ Installation successful!
    echo.
    echo You can now send prescriptions as PDF attachments.
    echo.
    echo To test:
    echo   python manage.py test_email youremail@gmail.com
    echo.
) else (
    echo ✗ Installation failed!
    echo.
    echo Try manually:
    echo   pip install xhtml2pdf
    echo.
)
echo ============================================
pause
