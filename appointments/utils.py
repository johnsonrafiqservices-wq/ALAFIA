"""
Utility functions for appointments app
"""
import logging

logger = logging.getLogger(__name__)


def send_sms(to_number, message, api_key=None, api_secret=None, from_number=None):
    """
    Send SMS using configured SMS service
    
    Supports multiple providers:
    - Africa's Talking (recommended for Uganda/East Africa)
    - People's SMS Uganda
    - SMS Box Uganda
    - Generic HTTP SMS gateway
    - Twilio (if installed)
    
    Args:
        to_number: Recipient phone number (e.g., "+256700000000")
        message: SMS message body
        api_key: API key (legacy parameter, now configured in settings)
        api_secret: API secret (legacy parameter, now configured in settings)
        from_number: Sender phone number (legacy parameter, now configured in settings)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    
    try:
        # First try the new SMS services
        from .sms_services import send_sms as send_sms_new
        
        success, result_message = send_sms_new(to_number, message)
        if success:
            logger.info(f'SMS sent successfully to {to_number}')
            return True
        else:
            logger.error(f'Failed to send SMS: {result_message}')
            
            # Try Twilio as fallback if credentials provided
            if all([api_key, api_secret, from_number]):
                logger.info('Attempting Twilio fallback...')
                return send_sms_twilio(to_number, message, api_key, api_secret, from_number)
            
            return False
            
    except Exception as e:
        logger.error(f'SMS service error: {str(e)}')
        
        # Try Twilio as fallback if credentials provided
        if all([api_key, api_secret, from_number]):
            logger.info('Attempting Twilio fallback...')
            return send_sms_twilio(to_number, message, api_key, api_secret, from_number)
        
        return False


def send_sms_twilio(to_number, message, api_key, api_secret, from_number):
    """
    Send SMS using Twilio (fallback option)
    
    Args:
        to_number: Recipient phone number
        message: SMS message body
        api_key: Twilio Account SID
        api_secret: Twilio Auth Token
        from_number: Twilio phone number
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        from twilio.rest import Client
        
        client = Client(api_key, api_secret)
        
        message_obj = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        logger.info(f'SMS sent via Twilio successfully: {message_obj.sid}')
        return True
        
    except ImportError:
        logger.error('Twilio library not installed. Install with: pip install twilio')
        return False
        
    except Exception as e:
        logger.error(f'Failed to send SMS via Twilio: {str(e)}')
        return False


def format_phone_number(phone):
    """
    Format phone number to E.164 format
    
    Args:
        phone: Phone number string
    
    Returns:
        str: Formatted phone number or original if formatting fails
    """
    try:
        import phonenumbers
        
        # Try to parse the number
        parsed = phonenumbers.parse(phone, "UG")  # Default to Uganda
        
        # Format to E.164
        formatted = phonenumbers.format_number(
            parsed, 
            phonenumbers.PhoneNumberFormat.E164
        )
        
        return formatted
        
    except ImportError:
        logger.warning('phonenumbers library not installed. Install with: pip install phonenumbers')
        return phone
        
    except Exception as e:
        logger.warning(f'Failed to format phone number: {str(e)}')
        return phone
