"""
SMS Service Providers Integration
Supports multiple SMS gateways including free/affordable options for Uganda
"""
import logging
import requests
from typing import Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class SMSService:
    """Base SMS Service class"""
    
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """
        Send SMS message
        Returns: (success: bool, message: str)
        """
        raise NotImplementedError("Subclasses must implement send_sms method")


class AfricasTalkingSMS(SMSService):
    """
    Africa's Talking SMS Service
    - Popular in East Africa (Kenya, Uganda, Tanzania, etc.)
    - Affordable rates for Uganda (~UGX 130 per SMS)
    - Has sandbox/testing environment
    - Website: https://africastalking.com/
    """
    
    def __init__(self, api_key: str, username: str):
        self.api_key = api_key
        self.username = username
        self.base_url = "https://api.africastalking.com/version1/messaging"
        
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send SMS via Africa's Talking API"""
        try:
            headers = {
                'apiKey': self.api_key,
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json'
            }
            
            data = {
                'username': self.username,
                'to': phone_number,
                'message': message
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                data=data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                if result.get('SMSMessageData', {}).get('Recipients'):
                    recipient = result['SMSMessageData']['Recipients'][0]
                    if recipient.get('statusCode') == 101:  # Success code
                        logger.info(f"SMS sent successfully to {phone_number}")
                        return True, "SMS sent successfully"
                    else:
                        error_msg = f"Failed to send SMS: {recipient.get('status', 'Unknown error')}"
                        logger.error(error_msg)
                        return False, error_msg
                        
            error_msg = f"API request failed with status {response.status_code}"
            logger.error(error_msg)
            return False, error_msg
            
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class GenericHTTPSMS(SMSService):
    """
    Generic HTTP SMS Gateway
    Works with any SMS provider that accepts HTTP/HTTPS requests
    - SMS API Uganda
    - BulkSMS Uganda
    - SMS Box
    - Any custom SMS gateway
    """
    
    def __init__(self, api_url: str, api_key: str, sender_id: str = ""):
        self.api_url = api_url
        self.api_key = api_key
        self.sender_id = sender_id
        
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send SMS via generic HTTP gateway"""
        try:
            # Common parameter formats - customize based on your provider
            params = {
                'apikey': self.api_key,
                'api_key': self.api_key,  # Alternative naming
                'phone': phone_number,
                'to': phone_number,  # Alternative naming
                'message': message,
                'text': message,  # Alternative naming
                'sender': self.sender_id,
                'from': self.sender_id,  # Alternative naming
            }
            
            response = requests.get(
                self.api_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                # Check for common success indicators
                text = response.text.lower()
                if any(word in text for word in ['success', 'sent', 'ok', 'delivered']):
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True, "SMS sent successfully"
                else:
                    error_msg = f"SMS send failed: {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(error_msg)
                return False, error_msg
                
        except requests.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class PeoplesMS(SMSService):
    """
    People's SMS Uganda
    - Uganda-based SMS provider
    - Affordable rates
    - Simple API
    - Website: https://peoplessms.com/
    """
    
    def __init__(self, api_key: str, sender_id: str):
        self.api_key = api_key
        self.sender_id = sender_id
        self.base_url = "https://api.peoplessms.com/send"
        
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send SMS via People's SMS API"""
        try:
            params = {
                'apikey': self.api_key,
                'sender': self.sender_id,
                'phone': phone_number,
                'message': message
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                if 'success' in response.text.lower():
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True, "SMS sent successfully"
                else:
                    error_msg = f"SMS send failed: {response.text}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error sending SMS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


class SMSBoxUganda(SMSService):
    """
    SMS Box Uganda
    - Uganda-based provider
    - Competitive rates
    - Website: https://smsbox.co.ug/
    """
    
    def __init__(self, api_key: str, sender_id: str):
        self.api_key = api_key
        self.sender_id = sender_id
        self.base_url = "https://api.smsbox.co.ug/api/send"
        
    def send_sms(self, phone_number: str, message: str) -> Tuple[bool, str]:
        """Send SMS via SMS Box API"""
        try:
            data = {
                'apikey': self.api_key,
                'sender': self.sender_id,
                'phone': phone_number,
                'message': message
            }
            
            response = requests.post(
                self.base_url,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    logger.info(f"SMS sent successfully to {phone_number}")
                    return True, "SMS sent successfully"
                else:
                    error_msg = f"SMS send failed: {result.get('message', 'Unknown error')}"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"API request failed with status {response.status_code}"
                logger.error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error sending SMS: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


def get_sms_service() -> Optional[SMSService]:
    """
    Factory function to get configured SMS service
    Returns the appropriate SMS service based on settings
    """
    sms_provider = getattr(settings, 'SMS_PROVIDER', 'africas_talking').lower()
    
    if sms_provider == 'africas_talking':
        api_key = getattr(settings, 'AFRICAS_TALKING_API_KEY', '')
        username = getattr(settings, 'AFRICAS_TALKING_USERNAME', '')
        
        if api_key and username:
            return AfricasTalkingSMS(api_key, username)
    
    elif sms_provider == 'peoples_sms':
        api_key = getattr(settings, 'PEOPLES_SMS_API_KEY', '')
        sender_id = getattr(settings, 'PEOPLES_SMS_SENDER_ID', '')
        
        if api_key and sender_id:
            return PeoplesMS(api_key, sender_id)
    
    elif sms_provider == 'smsbox':
        api_key = getattr(settings, 'SMSBOX_API_KEY', '')
        sender_id = getattr(settings, 'SMSBOX_SENDER_ID', '')
        
        if api_key and sender_id:
            return SMSBoxUganda(api_key, sender_id)
    
    elif sms_provider == 'generic':
        api_url = getattr(settings, 'GENERIC_SMS_URL', '')
        api_key = getattr(settings, 'GENERIC_SMS_API_KEY', '')
        sender_id = getattr(settings, 'GENERIC_SMS_SENDER_ID', '')
        
        if api_url and api_key:
            return GenericHTTPSMS(api_url, api_key, sender_id)
    
    logger.warning(f"No valid SMS service configured for provider: {sms_provider}")
    return None


def send_sms(phone_number: str, message: str) -> Tuple[bool, str]:
    """
    Send SMS using configured service
    
    Args:
        phone_number: Recipient phone number (e.g., "+256700000000")
        message: SMS message content
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    sms_service = get_sms_service()
    
    if not sms_service:
        error_msg = "No SMS service configured"
        logger.error(error_msg)
        return False, error_msg
    
    return sms_service.send_sms(phone_number, message)
