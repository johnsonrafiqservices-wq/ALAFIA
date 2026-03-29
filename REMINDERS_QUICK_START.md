# Appointment Reminders - Quick Start Guide

## 🚀 5-Minute Setup

### Step 1: Run Migrations (Required)
```bash
python manage.py makemigrations appointments
python manage.py migrate
```

### Step 2: Configure Email in settings.py (Required)
```python
# For Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-gmail-app-password'  # Generate at myaccount.google.com/apppasswords
DEFAULT_FROM_EMAIL = 'Physio Clinic <your-email@gmail.com>'
```

### Step 3: Configure Reminder Settings in Admin
1. Go to `/admin/appointments/remindersettings/`
2. Click "Add Reminder Settings"
3. Set basic configuration:
   - **First Reminder Hours**: 48
   - **Second Reminder Hours**: 24  
   - **Final Reminder Hours**: 2
   - ✅ Email Enabled
   - ✅ Notify Patient
   - ✅ Notify Provider
   - ✅ Notify Receptionist
   - **Receptionist Emails**: `reception@clinic.com`
4. Click Save

### Step 4: Test It (Required)
```bash
# See what would be sent (doesn't actually send)
python manage.py send_appointment_reminders --dry-run

# Send actual reminders
python manage.py send_appointment_reminders
```

### Step 5: Automate (Production)

**Windows Task Scheduler:**
1. Task Scheduler → Create Basic Task
2. Name: "Appointment Reminders"
3. Trigger: Daily at 6:00 AM, Repeat every 30 minutes
4. Action: Start Program
   - Program: `C:\...\python.exe`
   - Arguments: `manage.py send_appointment_reminders`
   - Start in: `C:\Users\it.sm\Music\PhysioNutritionClinic`

**Linux/Mac Cron:**
```bash
# Edit crontab
crontab -e

# Add this line (runs every 30 minutes)
*/30 * * * * cd /path/to/PhysioNutritionClinic && python manage.py send_appointment_reminders
```

## 📱 Optional: SMS Setup

### Install Twilio
```bash
pip install twilio phonenumbers
```

### Get Twilio Account
1. Sign up at https://www.twilio.com/
2. Get a phone number
3. Note: Account SID, Auth Token, Phone Number

### Configure in Admin
1. Admin → Reminder Settings
2. SMS Settings section:
   - **SMS API Key**: Your Account SID
   - **SMS API Secret**: Your Auth Token
   - **SMS From Number**: +1234567890
   - ✅ SMS Enabled
3. Save

## 📊 Monitoring

**View Sent Reminders:**
`/admin/appointments/appointmentreminder/`

**Filter by Status:**
- Sent ✅
- Failed ❌
- Pending ⏳

## ⚡ Quick Commands

```bash
# Test without sending
python manage.py send_appointment_reminders --dry-run

# Send all reminders
python manage.py send_appointment_reminders

# Send only first reminders (48h before)
python manage.py send_appointment_reminders --reminder-type first

# Send only second reminders (24h before)
python manage.py send_appointment_reminders --reminder-type second

# Send only final reminders (2h before)
python manage.py send_appointment_reminders --reminder-type final
```

## 🎯 What Gets Sent

### Patients Receive:
```
Dear John Doe,

This is a reminder about your upcoming appointment:

Date: Wednesday, November 06, 2025
Time: 02:00 PM
Service: Physiotherapy Session
Provider: Dr. Jane Smith
Duration: 60 minutes

Please arrive 10 minutes early.
```

### Staff Receive:
```
Appointment Reminder:

Patient: John Doe
Date: Wednesday, November 06, 2025
Time: 02:00 PM
Service: Physiotherapy Session
Provider: Dr. Jane Smith
Status: Confirmed
```

## ✅ Recipients Configuration

| Recipient | Email | SMS | Default |
|-----------|-------|-----|---------|
| Patient | ✅ | ✅ | ON |
| Provider | ✅ | ✅ | ON |
| Receptionist | ✅ | ✅ | ON |
| Admin | ✅ | ✅ | OFF |
| Nurse | ✅ | ✅ | OFF |

Configure in Admin → Reminder Settings → Recipients section

## 🔧 Troubleshooting

### Email Not Working?
```bash
# Test Django email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@email.com', ['to@email.com'])
```

### SMS Not Working?
```bash
# Test Twilio
python manage.py shell
>>> from appointments.utils import send_sms
>>> send_sms('+256700000000', 'Test', 'SID', 'TOKEN', 'FROM_NUMBER')
```

### No Reminders Sent?
1. Check appointments are "scheduled" or "confirmed"
2. Check appointments are in the future
3. Run with `--dry-run` to see what would be sent
4. Check Admin → Reminder Settings → Is Active = ✅

## 💰 Cost Estimate

**Email**: FREE (Gmail: 500/day)
**SMS**: ~$0.04 per message (Uganda via Twilio)

Example: 50 patients/day × 3 reminders = 150 SMS × $0.04 = $6/day

## 📝 Default Schedule

| Reminder | Hours Before | When Sent |
|----------|--------------|-----------|
| First | 48 | 2 days before |
| Second | 24 | 1 day before |
| Final | 2 | 2 hours before |

Customize in Admin → Reminder Settings

## 🎉 Done!

Your appointment reminder system is now active. Reminders will be sent automatically based on your schedule.

**Next Steps:**
1. Monitor first day of reminders
2. Check AppointmentReminder table for sent status
3. Ask patients/staff for feedback
4. Adjust timing if needed

For detailed documentation, see `APPOINTMENT_REMINDERS_SETUP.md`
