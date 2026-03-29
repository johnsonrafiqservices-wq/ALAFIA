# Fix: 'EmailMessage' object has no attribute 'attach_alternative'

## Error
```
Error sending email: 'EmailMessage' object has no attribute 'attach_alternative'
```

## Cause
The code was using `EmailMessage` class from `django.core.mail`, which only supports plain text emails. The `attach_alternative()` method is only available in `EmailMultiAlternatives` class.

## Solution Applied

### Changed in `pharmacy/views.py`:

**Before (Line 2016):**
```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject=subject,
    body=email_body,
    from_email='noreply@physionutrition.com',
    to=[prescription.patient.email],
    reply_to=[...]
)
email.attach_alternative(html_content, "text/html")  # ❌ ERROR!
```

**After (Line 2016):**
```python
from django.core.mail import EmailMultiAlternatives

email = EmailMultiAlternatives(  # ✅ FIXED!
    subject=subject,
    body=email_body,
    from_email=clinic_settings.email if clinic_settings and clinic_settings.email else 'noreply@physionutrition.com',
    to=[prescription.patient.email],
    reply_to=[clinic_settings.email if clinic_settings and clinic_settings.email else 'info@physionutrition.com']
)
email.attach_alternative(html_content, "text/html")  # ✅ Now works!
```

### Also Fixed in `pharmacy/management/commands/test_email.py`:

**Before:**
```python
from django.core.mail import EmailMessage

email = EmailMessage(...)
email.attach_alternative(html_content, "text/html")  # ❌ ERROR!
```

**After:**
```python
from django.core.mail import EmailMultiAlternatives

email = EmailMultiAlternatives(...)
email.attach_alternative(html_content, "text/html")  # ✅ Works!
```

## Understanding the Difference

### EmailMessage (Plain Text Only)
```python
from django.core.mail import EmailMessage

email = EmailMessage(
    subject='Test',
    body='Plain text only',
    from_email='from@example.com',
    to=['to@example.com']
)
email.send()  # ✅ Sends plain text email
```

### EmailMultiAlternatives (Text + HTML)
```python
from django.core.mail import EmailMultiAlternatives

email = EmailMultiAlternatives(
    subject='Test',
    body='Plain text version',  # Fallback for email clients that don't support HTML
    from_email='from@example.com',
    to=['to@example.com']
)
email.attach_alternative('<h1>HTML version</h1>', 'text/html')  # ✅ Works!
email.send()  # ✅ Sends both text and HTML versions
```

## Why Use EmailMultiAlternatives?

1. **Better User Experience**: HTML emails look more professional
2. **Fallback Support**: Plain text version for old email clients
3. **Formatting**: Can include images, styling, and layout
4. **Accessibility**: Text version for screen readers

## Files Modified
1. ✅ `pharmacy/views.py` - Line 2016, 2049
2. ✅ `pharmacy/management/commands/test_email.py` - Line 71, 85
3. ✅ `EMAIL_TROUBLESHOOTING.md` - Added common error section

## Testing the Fix

### Option 1: Console Backend (No Real Email)
```bash
set EMAIL_BACKEND=console
python manage.py runserver
# Try sending prescription - email will print to console
```

### Option 2: Test Command
```bash
python manage.py test_email youremail@gmail.com
```

Expected output:
```
✓ Simple test email sent successfully!
✓ HTML test email sent successfully!
✓ All email tests passed!
```

### Option 3: Real Prescription
1. Go to prescription detail page
2. Click "Email Prescription"
3. Should now work without the 'attach_alternative' error

## Status
✅ **FIXED** - Prescription emails now work correctly with both text and HTML versions.

## Additional Benefits of This Fix

1. **Professional Emails**: HTML prescription emails with clinic branding
2. **Better Readability**: Formatted medication lists and instructions
3. **Email Client Support**: Works with all email clients (HTML or text-only)
4. **Consistent with Django Best Practices**: Using the correct email class
