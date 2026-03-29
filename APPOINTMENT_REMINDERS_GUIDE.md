# Appointment Reminder System Guide

## Overview

The PhysioNutrition Clinic has a comprehensive appointment reminder system that can send reminders via **Email** and **SMS** both manually and automatically.

## Features

### ✅ Manual Reminders (Button)
- Send reminders immediately with a button click
- Available on appointment detail page
- Staff-only feature
- Works for scheduled and confirmed appointments

### ✅ Automatic Reminders (Scheduled)
- Automated reminders sent before appointments
- Three reminder types: First, Second, and Final
- Configurable timing (hours before appointment)
- Runs via management command (can be automated with cron/scheduler)

### ✅ Multi-Channel Support
- **Email**: Professional email reminders
- **SMS**: Text message reminders
- Supports multiple SMS providers (Africa's Talking, People's SMS, SMS Box, Generic HTTP)

### ✅ Reminder History
- Track all sent reminders
- View status (sent, failed, pending)
- See recipient details
- Error logging for troubleshooting

---

## Manual Reminder Sending

### How to Send Manual Reminders

1. Navigate to the appointment detail page
2. In the "Quick Actions" section (right sidebar)
3. Click **"Send Reminder Now"** button
4. System will send reminders to:
   - Patient (if email/phone available)
   - Provider (if enabled in settings)

### Requirements
- User must be staff member
- Appointment must be in 'scheduled' or 'confirmed' status
- Reminder settings must be active

### What Gets Sent

**Email to Patient:**
```
Dear [Patient Name],

This is a reminder about your upcoming appointment:

Date: [Day, Month DD, YYYY]
Time: [HH:MM AM/PM]
Service: [Service Name]
Provider: [Provider Name]
Duration: [XX] minutes

Please arrive 10 minutes early to complete any necessary paperwork.

If you need to reschedule or cancel, please contact us as soon as possible.

Thank you,
Physio & Nutrition Clinic
```

**SMS to Patient:**
```
Appointment Reminder:

Date: [Mon DD, YYYY]
Time: [HH:MM AM/PM]
Service: [Service Name]
Provider: [Provider Name]

Please arrive 10 minutes early.

Physio & Nutrition Clinic
```

---

## Automatic Reminder System

### Setup Reminder Settings

1. Go to Django Admin: `/admin/`
2. Navigate to **Appointments → Reminder Settings**
3. Configure the following:

#### Timing Settings
- **First Reminder Hours**: Default 48 (2 days before)
- **Second Reminder Hours**: Default 24 (1 day before)
- **Final Reminder Hours**: Default 2 (2 hours before)

#### Notification Methods
- ✅ **Email Enabled**: Send email reminders
- ✅ **SMS Enabled**: Send SMS reminders

#### Recipients
- ✅ **Notify Patient**: Send to patient
- ✅ **Notify Provider**: Send to provider
- ⬜ **Notify Admin**: Send to admin staff
- ⬜ **Notify Nurse**: Send to nurses
- ✅ **Notify Receptionist**: Send to receptionists

#### Email Configuration
- **Reminder From Email**: Sender email address
- **Admin Emails**: Comma-separated admin emails
- **Nurse Emails**: Comma-separated nurse emails
- **Receptionist Emails**: Comma-separated receptionist emails

#### System Status
- ✅ **Is Active**: Enable/disable entire reminder system

### Running Automatic Reminders

#### Manual Execution
```bash
# Send all reminder types
python manage.py send_appointment_reminders

# Dry run (test without sending)
python manage.py send_appointment_reminders --dry-run

# Send specific reminder type
python manage.py send_appointment_reminders --reminder-type first
python manage.py send_appointment_reminders --reminder-type second
python manage.py send_appointment_reminders --reminder-type final
```

#### Automated Execution (Windows Task Scheduler)

1. Open **Task Scheduler**
2. Create New Task
3. **Trigger**: Run every hour (or your preferred interval)
4. **Action**: Start a program
   - Program: `python.exe`
   - Arguments: `manage.py send_appointment_reminders`
   - Start in: `C:\Users\it.sm\Music\PhysioNutritionClinic`

#### Automated Execution (Linux Cron)

Add to crontab:
```bash
# Run every hour
0 * * * * cd /path/to/PhysioNutritionClinic && python manage.py send_appointment_reminders

# Or run every 30 minutes
*/30 * * * * cd /path/to/PhysioNutritionClinic && python manage.py send_appointment_reminders
```

---

## SMS Configuration

### Supported SMS Providers

1. **Africa's Talking** (Recommended for Uganda/East Africa)
2. **People's SMS** (Uganda-based)
3. **SMS Box Uganda**
4. **Generic HTTP Gateway** (Any SMS provider)
5. **Twilio** (Fallback option)

### Configuration (settings.py or .env)

#### Africa's Talking
```python
SMS_PROVIDER = 'africas_talking'
AFRICAS_TALKING_API_KEY = 'your_api_key_here'
AFRICAS_TALKING_USERNAME = 'your_username'
```

#### People's SMS
```python
SMS_PROVIDER = 'peoples_sms'
PEOPLES_SMS_API_KEY = 'your_api_key_here'
PEOPLES_SMS_SENDER_ID = 'PhysioClinic'
```

#### SMS Box Uganda
```python
SMS_PROVIDER = 'smsbox'
SMSBOX_API_KEY = 'your_api_key_here'
SMSBOX_SENDER_ID = 'PhysioClinic'
```

#### Generic HTTP Gateway
```python
SMS_PROVIDER = 'generic'
GENERIC_SMS_URL = 'https://your-sms-gateway.com/send'
GENERIC_SMS_API_KEY = 'your_api_key_here'
GENERIC_SMS_SENDER_ID = 'PhysioClinic'
```

### Getting SMS Credentials

#### Africa's Talking
1. Sign up at https://africastalking.com/
2. Create an app
3. Get your API key from dashboard
4. Username is usually your app name

#### People's SMS Uganda
1. Sign up at https://peoplessms.com/
2. Purchase SMS credits
3. Get API key from account settings

#### SMS Box Uganda
1. Contact SMS Box: https://smsbox.co.ug/
2. Setup account and get API credentials

---

## Email Configuration

### Django Email Settings (settings.py)

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Physio & Nutrition Clinic <your-email@gmail.com>'
```

### Gmail Setup
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
3. Use the generated password in `EMAIL_HOST_PASSWORD`

---

## Reminder History & Tracking

### Viewing Reminder History

#### In Appointment Detail Page
- Reminder history shows in the sidebar
- Displays last 10 reminders for the appointment
- Shows:
  - Send date/time
  - Method (Email/SMS)
  - Recipient name
  - Status (Sent/Failed/Pending)
  - Error messages (if failed)

#### In Django Admin
1. Go to `/admin/`
2. Navigate to **Appointments → Appointment Reminders**
3. Filter by:
   - Status
   - Method
   - Reminder type
   - Date range

### Reminder Statuses

- **Pending**: Scheduled but not sent yet
- **Sent**: Successfully delivered
- **Failed**: Delivery failed (see error message)
- **Cancelled**: Reminder cancelled (e.g., appointment cancelled)

---

## Troubleshooting

### Reminders Not Sending

1. **Check Reminder Settings**
   - Admin → Reminder Settings
   - Ensure "Is Active" is checked
   - Verify notification methods are enabled

2. **Check Recipient Contact Info**
   - Patient must have valid email/phone
   - Provider must have email if "Notify Provider" enabled

3. **Check Email Configuration**
   - Test email settings: `python manage.py sendtestemail your@email.com`
   - Verify SMTP credentials

4. **Check SMS Configuration**
   - Verify SMS_PROVIDER is set correctly
   - Check API credentials
   - Test SMS manually in Python shell

5. **Check Logs**
   - View Django logs for error messages
   - Check reminder history in admin for error details

### Email Delivery Issues

- **Gmail Blocking**: Use App Password instead of regular password
- **Spam Filters**: Check recipient spam folders
- **SMTP Errors**: Verify server, port, and TLS settings

### SMS Delivery Issues

- **Invalid Phone Numbers**: Must be in E.164 format (+256...)
- **Insufficient Credits**: Check SMS provider account balance
- **API Errors**: Verify API credentials and URL
- **Network Issues**: Check internet connectivity

---

## Best Practices

### Reminder Timing
- **First Reminder**: 48 hours before (gives patient time to reschedule)
- **Second Reminder**: 24 hours before (final warning)
- **Final Reminder**: 2 hours before (last-minute reminder)

### Recipient Selection
- Always enable patient notifications
- Enable provider notifications for staff coordination
- Use admin/receptionist emails for internal tracking

### Message Content
- Keep SMS messages under 160 characters to avoid splitting
- Include essential info: date, time, location
- Provide contact info for rescheduling

### Testing
- Always run with `--dry-run` first
- Test with a few appointments before full deployment
- Monitor logs and reminder history

### Cost Management
- SMS costs money per message
- Consider email-first for cost savings
- Use SMS for high-priority reminders only
- Monitor SMS usage and costs

---

## API Reference

### Manual Reminder Function

```python
from appointments.views import send_appointment_reminders
from appointments.models import Appointment, ReminderSettings
from django.utils import timezone

# Get appointment
appointment = Appointment.objects.get(pk=1)

# Get settings
settings = ReminderSettings.get_settings()

# Send reminders
sent_count = send_appointment_reminders(
    appointment=appointment,
    reminder_type='manual',  # or 'first', 'second', 'final'
    settings_obj=settings,
    now=timezone.now()
)

print(f"Sent {sent_count} reminders")
```

### SMS Sending Function

```python
from appointments.utils import send_sms

# Send SMS
success = send_sms(
    to_number='+256700000000',
    message='Your appointment is tomorrow at 10 AM'
)

if success:
    print("SMS sent successfully")
else:
    print("Failed to send SMS")
```

---

## Summary

✅ **Manual Reminders**: Click button on appointment detail page
✅ **Automatic Reminders**: Run management command (manually or scheduled)
✅ **Email & SMS**: Multi-channel notification support
✅ **Full Tracking**: Complete history of all sent reminders
✅ **Flexible Configuration**: Customize timing, recipients, and methods
✅ **Error Handling**: Robust error logging and retry support

For additional support or questions, consult the Django admin documentation or system logs.
