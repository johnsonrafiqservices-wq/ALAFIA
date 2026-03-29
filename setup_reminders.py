"""
Automated Setup Script for Appointment Reminders System
Run this script to automatically set up the reminder system
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings
from appointments.models import ReminderSettings


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_success(text):
    """Print success message"""
    print(f"✓ {text}")


def print_error(text):
    """Print error message"""
    print(f"✗ {text}")


def print_warning(text):
    """Print warning message"""
    print(f"⚠ {text}")


def run_migrations():
    """Run database migrations"""
    print_header("STEP 1: Running Database Migrations")
    try:
        print("Creating migrations for appointments app...")
        call_command('makemigrations', 'appointments', interactive=False)
        print_success("Migrations created")
        
        print("\nApplying migrations...")
        call_command('migrate', interactive=False)
        print_success("Migrations applied successfully")
        return True
    except Exception as e:
        print_error(f"Migration failed: {str(e)}")
        return False


def check_twilio_available():
    """Check if Twilio is available"""
    try:
        import twilio
        return True
    except ImportError:
        return False


def create_reminder_settings():
    """Create initial reminder settings"""
    print_header("STEP 2: Creating Reminder Settings")
    
    # Check if Twilio is available
    twilio_available = check_twilio_available()
    
    try:
        settings_obj, created = ReminderSettings.objects.get_or_create(
            pk=1,
            defaults={
                'first_reminder_hours': 48,
                'second_reminder_hours': 24,
                'final_reminder_hours': 2,
                'email_enabled': True,
                'sms_enabled': False,  # Disabled by default until Twilio is configured
                'notify_patient': True,
                'notify_provider': True,
                'notify_admin': False,
                'notify_nurse': False,
                'notify_receptionist': True,
                'is_active': True,
            }
        )
        
        if created:
            print_success("Reminder settings created with default values:")
            print("   - First reminder: 48 hours before appointment")
            print("   - Second reminder: 24 hours before appointment")
            print("   - Final reminder: 2 hours before appointment")
            print("   - Email: Enabled ✓")
            if twilio_available:
                print("   - SMS: Disabled (Twilio installed, configure in admin to enable)")
            else:
                print("   - SMS: Not available (Twilio not installed - optional)")
            print("   - Recipients: Patient, Provider, Receptionist")
        else:
            print_warning("Reminder settings already exist - skipping creation")
            print("   Current settings preserved")
        
        return True, settings_obj
    except Exception as e:
        print_error(f"Failed to create settings: {str(e)}")
        return False, None


def check_email_configuration():
    """Check if email is configured"""
    print_header("STEP 3: Checking Email Configuration")
    
    email_backend = getattr(settings, 'EMAIL_BACKEND', None)
    email_host = getattr(settings, 'EMAIL_HOST', None)
    default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None)
    
    if email_backend and 'smtp' in email_backend.lower():
        print_success("Email backend configured: " + email_backend)
        if email_host:
            print_success(f"Email host configured: {email_host}")
        if default_from_email:
            print_success(f"From email configured: {default_from_email}")
        
        if email_host and default_from_email:
            return True
        else:
            print_warning("Email partially configured - some settings missing")
            return False
    else:
        print_error("Email not configured for production")
        print("\nAdd to settings.py:")
        print("""
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Clinic <your-email@gmail.com>'
        """)
        return False


def test_reminder_system():
    """Test the reminder system with dry run"""
    print_header("STEP 4: Testing Reminder System")
    try:
        print("Running dry-run test (won't send actual reminders)...")
        call_command('send_appointment_reminders', '--dry-run')
        print_success("Reminder system test completed")
        return True
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


def print_next_steps(email_configured, settings_obj):
    """Print next steps for user"""
    print_header("SETUP COMPLETE!")
    
    print("\n📋 WHAT WAS DONE:")
    print("  ✓ Database migrations applied")
    print("  ✓ Reminder settings created")
    print("  ✓ System tested with dry-run")
    
    print("\n🎯 NEXT STEPS:")
    
    step = 1
    
    if not email_configured:
        print(f"\n{step}. Configure Email (REQUIRED for email reminders)")
        print("   Add to clinic_system/settings.py:")
        print("""
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'  # Generate at myaccount.google.com/apppasswords
   DEFAULT_FROM_EMAIL = 'Physio Clinic <your-email@gmail.com>'
        """)
        step += 1
    
    print(f"\n{step}. Configure Reminder Settings in Admin")
    print("   Go to: http://localhost:8000/admin/appointments/remindersettings/1/change/")
    print("   Update:")
    print("   - Email addresses for receptionists, admins, nurses")
    print("   - Reminder timing if needed")
    print("   - Enable SMS if you have Twilio account")
    step += 1
    
    print(f"\n{step}. Test Sending Reminders")
    print("   python manage.py send_appointment_reminders --dry-run")
    print("   (Check what would be sent without actually sending)")
    step += 1
    
    print(f"\n{step}. Send Real Reminders")
    print("   python manage.py send_appointment_reminders")
    step += 1
    
    print(f"\n{step}. Set Up Automated Scheduling")
    print("   Windows Task Scheduler:")
    print("   - Run every 30 minutes")
    print("   - Command: python manage.py send_appointment_reminders")
    print("   - Working directory: " + os.path.dirname(os.path.abspath(__file__)))
    print("\n   OR use Cron (Linux/Mac):")
    print("   */30 * * * * cd " + os.path.dirname(os.path.abspath(__file__)) + " && python manage.py send_appointment_reminders")
    
    print("\n📚 DOCUMENTATION:")
    print("   - Full Guide: APPOINTMENT_REMINDERS_SETUP.md")
    print("   - Quick Start: REMINDERS_QUICK_START.md")
    
    print("\n💡 OPTIONAL: SMS Setup (Not Required)")
    print("   Email reminders work perfectly without SMS!")
    print("   If you want SMS later:")
    print("   1. Install: pip install twilio phonenumbers")
    print("      (Note: May require enabling Windows long paths)")
    print("   2. Sign up at: https://www.twilio.com/")
    print("   3. Add credentials in Admin → Reminder Settings")
    print("   4. Enable SMS checkbox in settings")
    
    print("\n" + "="*70)


def main():
    """Main setup function"""
    print_header("APPOINTMENT REMINDER SYSTEM - AUTOMATED SETUP")
    print("This script will set up everything automatically")
    print("Press Ctrl+C to cancel at any time")
    
    input("\nPress Enter to continue...")
    
    # Step 1: Run migrations
    if not run_migrations():
        print_error("Setup failed at migration step")
        return
    
    # Step 2: Create reminder settings
    success, settings_obj = create_reminder_settings()
    if not success:
        print_error("Setup failed at settings creation step")
        return
    
    # Step 3: Check email configuration
    email_configured = check_email_configuration()
    
    # Step 4: Test system
    test_reminder_system()
    
    # Print next steps
    print_next_steps(email_configured, settings_obj)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
