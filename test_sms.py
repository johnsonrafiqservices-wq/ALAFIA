"""
Quick SMS Test Script
Run this to test your SMS configuration
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from appointments.sms_services import send_sms
from appointments.utils import format_phone_number


def test_sms():
    """Test SMS sending"""
    print("="*70)
    print("SMS CONFIGURATION TEST")
    print("="*70)
    
    # Get phone number
    print("\nEnter recipient phone number (e.g., +256700000000 or 0700000000):")
    phone = input("Phone: ").strip()
    
    if not phone:
        print("❌ No phone number provided")
        return
    
    # Format phone number
    formatted_phone = format_phone_number(phone)
    print(f"\nFormatted phone: {formatted_phone}")
    
    # Test message
    message = "Test SMS from PhysioNutrition Clinic appointment reminder system."
    
    print(f"\nMessage: {message}")
    print(f"Length: {len(message)} characters")
    
    print("\n" + "="*70)
    print("SENDING SMS...")
    print("="*70)
    
    # Send SMS
    success, result_message = send_sms(formatted_phone, message)
    
    print("\n" + "="*70)
    if success:
        print("✅ SUCCESS!")
        print(f"Message: {result_message}")
        print("\nCheck your phone for the SMS.")
    else:
        print("❌ FAILED!")
        print(f"Error: {result_message}")
        print("\nTroubleshooting:")
        print("1. Check your .env file has correct SMS credentials")
        print("2. Verify SMS_PROVIDER is set correctly")
        print("3. For Africa's Talking sandbox, register test numbers first")
        print("4. Check you have SMS credits (for production)")
    print("="*70)


def show_config():
    """Show current SMS configuration"""
    from django.conf import settings
    
    print("\n" + "="*70)
    print("CURRENT SMS CONFIGURATION")
    print("="*70)
    
    provider = getattr(settings, 'SMS_PROVIDER', 'Not configured')
    print(f"\nProvider: {provider}")
    
    if provider == 'africas_talking':
        api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', '')
        username = getattr(settings, 'AFRICAS_TALKING_USERNAME', '')
        print(f"Username: {username}")
        print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
        
    elif provider == 'peoples_sms':
        api_key = getattr(settings, 'PEOPLES_SMS_API_KEY', '')
        sender = getattr(settings, 'PEOPLES_SMS_SENDER_ID', '')
        print(f"Sender ID: {sender or 'NOT SET'}")
        print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
        
    elif provider == 'smsbox':
        api_key = getattr(settings, 'SMSBOX_API_KEY', '')
        sender = getattr(settings, 'SMSBOX_SENDER_ID', '')
        print(f"Sender ID: {sender or 'NOT SET'}")
        print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
        
    elif provider == 'generic':
        url = getattr(settings, 'GENERIC_SMS_URL', '')
        api_key = getattr(settings, 'GENERIC_SMS_API_KEY', '')
        sender = getattr(settings, 'GENERIC_SMS_SENDER_ID', '')
        print(f"API URL: {url or 'NOT SET'}")
        print(f"Sender ID: {sender or 'NOT SET'}")
        print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
    
    print("="*70)


if __name__ == '__main__':
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║              SMS TEST UTILITY                                     ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    
    show_config()
    
    print("\n\nOptions:")
    print("1. Test SMS sending")
    print("2. Show configuration only")
    print("3. Exit")
    
    choice = input("\nChoice (1-3): ").strip()
    
    if choice == '1':
        test_sms()
    elif choice == '2':
        print("\nConfiguration shown above.")
    else:
        print("\nExiting...")
    
    print("\n")
