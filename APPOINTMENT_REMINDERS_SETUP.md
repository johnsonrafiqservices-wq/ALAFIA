# Appointment Reminders System

Comprehensive appointment reminder system with email and SMS notifications for patients, providers, admins, nurses, and receptionists.

## Features

### ✅ Multi-Channel Notifications
- **Email Reminders**: Professional email notifications
- **SMS Reminders**: Text message notifications via Twilio

### ✅ Multiple Reminder Types
- **First Reminder**: Default 48 hours before appointment
- **Second Reminder**: Default 24 hours before appointment
- **Final Reminder**: Default 2 hours before appointment

### ✅ Multiple Recipients
- **Patients**: Get reminders about their appointments
- **Providers**: Get notified about upcoming appointments with patients
- **Admins**: Receive all appointment reminders
- **Nurses**: Stay informed about scheduled appointments
- **Receptionists**: Track upcoming appointments

### ✅ Complete Tracking
- Track all sent reminders
- Monitor delivery status (sent/failed/cancelled)
- View error messages for failed reminders
- Audit trail of all notifications

## Installation Steps

### 1. Run Database Migrations

```bash
python manage.py makemigrations appointments
python manage.py migrate appointments
```

This creates the following database tables:
- `appointments_remindersettings` - System-wide reminder configuration
- `appointments_appointmentreminder` - Log of all sent reminders

### 2. Install Required Packages

#### For Email (Built-in, no extra packages needed)
Django's email system is used.

#### For SMS (Optional - Only if using SMS)

```bash
pip install twilio
pip install phonenumbers
```

### 3. Configure Django Email Settings

Add to `settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'Physio & Nutrition Clinic <your-email@gmail.com>'
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the app password in `EMAIL_HOST_PASSWORD`

### 4. Configure Reminder Settings (Admin Panel)

1. Go to Django Admin: `http://your-site.com/admin/`
2. Navigate to **Appointments > Reminder Settings**
3. Click **Add Reminder Settings** (first time only)
4. Configure:

#### Reminder Timing
- First Reminder Hours: `48` (2 days before)
- Second Reminder Hours: `24` (1 day before)
- Final Reminder Hours: `2` (2 hours before)

#### Notification Methods
- ✅ Email Enabled
- ✅ SMS Enabled (if configured)

#### Recipients
- ✅ Notify Patient
- ✅ Notify Provider
- ✅ Notify Receptionist
- ☐ Notify Admin (optional)
- ☐ Notify Nurse (optional)

#### Email Settings
- **Reminder From Email**: `appointments@clinic.com`
- **Admin Emails**: `admin1@clinic.com, admin2@clinic.com`
- **Nurse Emails**: `nurse1@clinic.com, nurse2@clinic.com`
- **Receptionist Emails**: `reception@clinic.com`

#### SMS Settings (Optional)
- **SMS API Key**: Your Twilio Account SID
- **SMS API Secret**: Your Twilio Auth Token
- **SMS From Number**: Your Twilio phone number (e.g., +1234567890)

5. Save settings

### 5. Get Twilio Credentials (For SMS)

1. Sign up at https://www.twilio.com/
2. Get a Twilio phone number
3. Get your credentials:
   - **Account SID** = SMS API Key
   - **Auth Token** = SMS API Secret
   - **Twilio Phone Number** = SMS From Number
4. Add credits to your Twilio account

## Usage

### Manual Testing (Dry Run)

Test what reminders would be sent without actually sending:

```bash
python manage.py send_appointment_reminders --dry-run
```

This shows:
- Which appointments need reminders
- Which recipients would receive notifications
- Email and SMS messages that would be sent

### Send Reminders Manually

```bash
# Send all reminder types
python manage.py send_appointment_reminders

# Send only first reminders
python manage.py send_appointment_reminders --reminder-type first

# Send only second reminders
python manage.py send_appointment_reminders --reminder-type second

# Send only final reminders
python manage.py send_appointment_reminders --reminder-type final
```

### Automated Scheduling (Production)

#### Option 1: Cron Job (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Run every 30 minutes
*/30 * * * * cd /path/to/PhysioNutritionClinic && /path/to/python manage.py send_appointment_reminders >> /var/log/reminders.log 2>&1
```

#### Option 2: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 6:00 AM (or hourly)
4. Action: Start a program
   - Program: `C:\path\to\python.exe`
   - Arguments: `manage.py send_appointment_reminders`
   - Start in: `C:\Users\it.sm\Music\PhysioNutritionClinic`
5. Advanced settings: Repeat every 30 minutes

#### Option 3: Celery (Recommended for Production)

1. Install Celery and Redis:
```bash
pip install celery redis
```

2. Create `celery.py` in your project:
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('clinic_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-appointment-reminders': {
        'task': 'appointments.tasks.send_reminders',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
```

3. Create `appointments/tasks.py`:
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def send_reminders():
    call_command('send_appointment_reminders')
```

4. Start Celery worker and beat:
```bash
celery -A clinic_system worker -l info
celery -A clinic_system beat -l info
```

## Monitoring

### View Sent Reminders

1. Go to Django Admin
2. Navigate to **Appointments > Appointment Reminders**
3. Filter by:
   - Reminder Type (first/second/final)
   - Recipient Type (patient/provider/admin/nurse/receptionist)
   - Method (email/sms)
   - Status (pending/sent/failed/cancelled)
   - Date

### Check Failed Reminders

Filter by Status = "Failed" to see:
- Which reminders failed
- Error messages
- Recipient details

### Bulk Actions

Select multiple reminders and:
- Mark as sent
- Mark as cancelled

## Message Customization

### Email Messages

Edit the message templates in:
- `appointments/management/commands/send_appointment_reminders.py`
- Look for the `send_email_reminder()` method

### SMS Messages

Edit SMS templates in:
- `appointments/management/commands/send_appointment_reminders.py`
- Look for the `send_sms_reminder()` method

## Troubleshooting

### Email Not Sending

1. **Check Django Email Settings**
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Message', 'from@email.com', ['to@email.com'])
   ```

2. **Check Reminder Settings**
   - Admin > Reminder Settings
   - Ensure "Email Enabled" is checked
   - Ensure "Is Active" is checked

3. **Check Logs**
   - Look for error messages in console output
   - Check Django logs

### SMS Not Sending

1. **Check Twilio Installation**
   ```bash
   python manage.py shell
   >>> import twilio
   ```

2. **Check Twilio Credentials**
   - Admin > Reminder Settings > SMS Settings
   - Verify Account SID, Auth Token, Phone Number

3. **Check Twilio Balance**
   - Log into Twilio dashboard
   - Ensure you have credits

4. **Test Manually**
   ```bash
   python manage.py shell
   >>> from appointments.utils import send_sms
   >>> send_sms('+256700000000', 'Test', 'YOUR_SID', 'YOUR_TOKEN', 'YOUR_NUMBER')
   ```

### No Reminders Sent

1. **Check if appointments exist**
   - Appointments must be "scheduled" or "confirmed"
   - Appointments must be in the future

2. **Check reminder timing**
   - Reminders are sent within 30-minute window
   - Example: For 2pm appointment with 2-hour reminder, runs between 11:45am-12:15pm

3. **Run with --dry-run**
   ```bash
   python manage.py send_appointment_reminders --dry-run
   ```
   This shows what would be sent without sending

### Duplicate Reminders

Each reminder is tracked in the database. Once sent successfully, it won't be sent again.

If duplicates occur:
1. Check for multiple cron jobs running
2. Check Celery beat isn't running multiple times
3. Review AppointmentReminder table for duplicate entries

## Advanced Configuration

### Custom Reminder Intervals

Edit in Admin > Reminder Settings:
- First Reminder: 72 hours (3 days)
- Second Reminder: 24 hours (1 day)
- Final Reminder: 1 hour

### Disable Specific Recipients

Uncheck in Admin > Reminder Settings:
- ☐ Notify Admin (if admins don't need reminders)
- ☐ Notify Nurse (if nurses don't need reminders)

### Multiple Email Addresses

Use comma-separated format:
```
admin1@clinic.com, admin2@clinic.com, admin3@clinic.com
```

### Different From Email

Set custom sender:
```
Clinic Reminders <reminders@clinic.com>
```

## Security Notes

### Sensitive Data
- SMS API credentials are stored in the database
- Consider encrypting sensitive fields
- Restrict admin access

### Email Security
- Use app passwords, not account passwords
- Enable 2FA on email account
- Use dedicated email for reminders

### SMS Security
- Keep Twilio credentials private
- Rotate credentials periodically
- Monitor usage to detect abuse

## Cost Considerations

### Email
- Gmail: 500 emails/day (free)
- Use SendGrid/Mailgun for higher volume

### SMS
- Twilio: ~$0.0075 per SMS (varies by country)
- Uganda: ~$0.04 per SMS
- Monitor monthly costs

### Example Costs (100 patients/day, 3 reminders each)
- Email: FREE (within limits)
- SMS: 300 messages × $0.04 = $12/day = $360/month

## Testing Checklist

- [ ] Migrations applied successfully
- [ ] Reminder Settings configured in admin
- [ ] Email settings tested
- [ ] SMS settings tested (if applicable)
- [ ] Dry run shows correct appointments
- [ ] Test reminder sent to patient
- [ ] Test reminder sent to provider
- [ ] Test reminder sent to receptionist
- [ ] Reminders tracked in AppointmentReminder table
- [ ] Scheduled task running automatically

## Support

For issues or questions:
1. Check Django logs
2. Check Twilio dashboard (for SMS)
3. Review error messages in AppointmentReminder table
4. Test with --dry-run flag

## Summary

The appointment reminder system provides:
- ✅ Automated email and SMS reminders
- ✅ Multi-recipient support (patients, providers, staff)
- ✅ Three reminder types (48h, 24h, 2h before)
- ✅ Complete audit trail
- ✅ Easy configuration via admin panel
- ✅ Flexible scheduling options
- ✅ Professional message templates

Run `python manage.py send_appointment_reminders --dry-run` to test your configuration!
