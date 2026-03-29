# Email Troubleshooting Guide

## Issue: Prescription Email Not Sending

### Problem
When trying to send a prescription via email, you see a 302 redirect but the email is not sent.

### Possible Causes

#### 1. Email Configuration Not Set Up
The Gmail account credentials may not be configured or may be incorrect.

#### 2. Gmail App Password Required
Gmail requires an App Password (not your regular password) for third-party applications.

#### 3. Network/Firewall Issues
The server may not be able to connect to Gmail's SMTP server.

#### 4. Patient Email Missing
The patient record may not have an email address.

---

## Solutions

### Solution 1: Set Up Gmail App Password

1. **Enable 2-Step Verification**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" as the app
   - Select "Other" for device and name it "PhysioNutrition Clinic"
   - Click "Generate"
   - **Copy the 16-character password** (no spaces)

3. **Update Django Settings**
   Edit `clinic_system/settings.py` or set environment variable:
   ```python
   EMAIL_HOST_USER = 'youremail@gmail.com'
   EMAIL_HOST_PASSWORD = 'your16charapppassword'  # NO SPACES!
   DEFAULT_FROM_EMAIL = 'youremail@gmail.com'
   ```

4. **Restart Django Server**
   ```bash
   # Stop the current server (Ctrl+C)
   # Start again
   python manage.py runserver
   ```

### Solution 2: Use Console Backend for Testing

If you want to test email functionality without sending real emails:

1. **Set Environment Variable**
   ```bash
   # Windows Command Prompt
   set EMAIL_BACKEND=console
   
   # Windows PowerShell
   $env:EMAIL_BACKEND="console"
   
   # Linux/Mac
   export EMAIL_BACKEND=console
   ```

2. **Or Edit settings.py**
   ```python
   EMAIL_BACKEND_TYPE = 'console'  # Change from 'smtp' to 'console'
   ```

3. **Restart Server**
   - Emails will now print to the console instead of sending

### Solution 3: Check Patient Email

1. **Verify Patient Has Email**
   - Go to patient detail page
   - Check if email address is filled in
   - Add email if missing

2. **Check Email Format**
   - Must be valid email format: `name@domain.com`

### Solution 4: Test Email Configuration

Create a test management command:

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

# Try sending a test email
try:
    send_mail(
        'Test Email',
        'This is a test email from PhysioNutrition Clinic.',
        'mwondhamail@gmail.com',  # From
        ['youremail@gmail.com'],  # To
        fail_silently=False,
    )
    print("✓ Email sent successfully!")
except Exception as e:
    print(f"✗ Email failed: {e}")
```

---

## Error Messages Explained

### "Authentication error"
- **Cause**: Incorrect email or password
- **Fix**: Update EMAIL_HOST_USER and EMAIL_HOST_PASSWORD

### "Cannot connect to email server"
- **Cause**: Network issue or firewall blocking port 587
- **Fix**: Check internet connection, try port 465 with SSL

### "Connection timeout"
- **Cause**: Server taking too long to respond
- **Fix**: Check firewall settings, increase EMAIL_TIMEOUT

### "Patient email not available"
- **Cause**: Patient record has no email address
- **Fix**: Add email to patient profile

---

## Common Error: 'EmailMessage' object has no attribute 'attach_alternative'

**Error:**
```
Error sending email: 'EmailMessage' object has no attribute 'attach_alternative'
```

**Cause:**
- Using `EmailMessage` instead of `EmailMultiAlternatives` for HTML emails

**Solution:**
- ✅ Already fixed in the codebase
- Use `from django.core.mail import EmailMultiAlternatives`
- `EmailMessage` is for plain text only
- `EmailMultiAlternatives` supports both text and HTML

---

## Quick Testing Steps

1. **Check current email backend:**
   ```bash
   python manage.py shell
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   print(settings.EMAIL_HOST_USER)
   ```

2. **Switch to console for testing:**
   - Set `EMAIL_BACKEND=console` environment variable
   - Restart server
   - Try sending prescription
   - Check terminal/console for email output

3. **Check error logs:**
   - Look at terminal where Django server is running
   - Error messages will show specific failure reason

---

## Alternative Solutions

### Option 1: Print Instead of Email
- Use the "Print Prescription" button
- Save as PDF
- Send PDF manually via email or WhatsApp

### Option 2: Download PDF
- Print prescription
- Use browser's "Save as PDF" option
- Share the PDF file

### Option 3: Use Different Email Provider
If Gmail doesn't work, try:
- **Outlook/Office365**
  ```python
  EMAIL_HOST = 'smtp.office365.com'
  EMAIL_PORT = 587
  ```
- **SendGrid** (Recommended for production)
- **Mailgun**
- **Amazon SES**

---

## Production Recommendations

For production deployment:

1. **Use Professional Email Service**
   - SendGrid (99% deliverability)
   - Mailgun
   - Amazon SES
   - Postmark

2. **Don't Use Personal Gmail**
   - Personal accounts have sending limits
   - May get flagged as spam
   - Not reliable for business use

3. **Set Up SPF/DKIM Records**
   - Improves email deliverability
   - Prevents emails going to spam

4. **Monitor Email Logs**
   - Track successful/failed sends
   - Set up alerts for failures

---

## Current Configuration

Your current settings:
```
EMAIL_HOST: smtp.gmail.com
EMAIL_PORT: 587
EMAIL_USE_TLS: True
EMAIL_HOST_USER: mwondhamail@gmail.com
```

**Next Steps:**
1. Generate Gmail App Password (see Solution 1)
2. Update EMAIL_HOST_PASSWORD with the 16-character code
3. Restart Django server
4. Try sending prescription again

---

## Need Help?

If you still have issues:
1. Check terminal logs for specific error messages
2. Try console backend to verify email content
3. Test with simple send_mail() command
4. Check Gmail account security settings
5. Verify patient has valid email address

The improved error messages will now show specific failure reasons in the Django messages framework.
