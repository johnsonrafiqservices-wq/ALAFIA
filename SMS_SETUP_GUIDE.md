# SMS Setup Guide - Free & Affordable Options for Uganda

This guide shows you how to add SMS reminders to your appointment system using **FREE or affordable** SMS services.

## 🎯 Quick Summary

| Provider | Best For | Cost | Setup Time |
|----------|----------|------|------------|
| **Africa's Talking** | East Africa | ~UGX 130/SMS | 10 min |
| People's SMS | Uganda only | Competitive | 10 min |
| SMS Box | Uganda only | Competitive | 10 min |
| Generic Gateway | Any provider | Varies | 15 min |

---

## ⭐ RECOMMENDED: Africa's Talking (FREE TESTING)

### Why Africa's Talking?
- ✅ **FREE sandbox for testing**
- ✅ Popular in East Africa (Kenya, Uganda, Tanzania)
- ✅ Affordable: ~UGX 130 per SMS
- ✅ Good delivery rates
- ✅ Easy integration
- ✅ Supports multiple countries

### Step-by-Step Setup

#### 1. Create Free Account
1. Go to https://africastalking.com/
2. Click "Get Started"
3. Sign up with your email
4. Verify email address

#### 2. Get API Credentials
1. Log in to your account
2. Go to "Sandbox" (for testing) or "Production" (for live)
3. Navigate to "Settings" → "API Key"
4. Generate API key
5. Copy:
   - **API Key** (looks like: `atsk_abc123...`)
   - **Username** (for sandbox: `sandbox`, for production: your app name)

#### 3. Configure in Your System

**Option A: Using .env file (Recommended)**

1. Open `.env` file in your project root
2. Add these lines:
```bash
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=your_api_key_here
AFRICAS_TALKING_USERNAME=sandbox
```

**Option B: Using Django Admin**

1. Go to `/admin/appointments/remindersettings/`
2. Click on your reminder settings
3. In SMS Settings section:
   - **SMS API Key**: Your Africa's Talking API key
   - **SMS API Secret**: Your username (sandbox or production)
   - **SMS From Number**: (not needed for Africa's Talking)
4. Check "SMS Enabled"
5. Click Save

#### 4. Test It

**Sandbox Testing (FREE):**
- Sandbox only sends to registered test numbers
- Add test numbers in Africa's Talking dashboard
- Perfect for development/testing

**Test Command:**
```bash
python manage.py send_appointment_reminders --dry-run
```

#### 5. Go Live (When Ready)

1. Add credit to your Africa's Talking account
2. Switch from "sandbox" to your production app name
3. Update `.env`:
   ```bash
   AFRICAS_TALKING_USERNAME=your_production_app_name
   ```
4. SMS will now send to real numbers

### Pricing (Uganda)
- **SMS Cost**: ~UGX 130 per message (~$0.035 USD)
- **Example**: 100 patients × 3 reminders = 300 SMS = ~UGX 39,000/day

---

## 🇺🇬 Option 2: People's SMS Uganda

### Why People's SMS?
- Uganda-based provider
- Competitive rates
- Local support

### Setup Steps

1. **Sign Up**: https://peoplessms.com/
2. **Get Credentials**:
   - API Key
   - Sender ID (your clinic name, e.g., "PhysioClinic")
3. **Configure**:
```bash
# Add to .env
SMS_PROVIDER=peoples_sms
PEOPLES_SMS_API_KEY=your_api_key_here
PEOPLES_SMS_SENDER_ID=YourClinic
```

---

## 🇺🇬 Option 3: SMS Box Uganda

### Setup Steps

1. **Sign Up**: https://smsbox.co.ug/
2. **Get API Key and Sender ID**
3. **Configure**:
```bash
# Add to .env
SMS_PROVIDER=smsbox
SMSBOX_API_KEY=your_api_key_here
SMSBOX_SENDER_ID=YourClinic
```

---

## 🌐 Option 4: Generic HTTP Gateway

### For Any SMS Provider

If you have another SMS provider, use the generic integration:

```bash
# Add to .env
SMS_PROVIDER=generic
GENERIC_SMS_URL=https://api.yourprovider.com/send
GENERIC_SMS_API_KEY=your_api_key_here
GENERIC_SMS_SENDER_ID=YourClinic
```

**Compatible with**:
- SMS API Uganda
- BulkSMS
- Any HTTP-based SMS gateway
- Custom SMS solutions

---

## 📝 Complete Configuration Example

Here's a complete `.env` file example:

```bash
# Email Configuration (Already setup)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=clinic@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=Physio Clinic <clinic@gmail.com>

# SMS Configuration (Add this)
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=atsk_1234567890abcdefghijklmnop
AFRICAS_TALKING_USERNAME=sandbox
```

---

## 🧪 Testing Your SMS Setup

### Test 1: Dry Run
```bash
python manage.py send_appointment_reminders --dry-run
```
This shows what would be sent without actually sending.

### Test 2: Real SMS
1. Create a test appointment for tomorrow
2. Add your phone number to the patient
3. Run:
```bash
python manage.py send_appointment_reminders
```
4. Check if you receive SMS

### Test 3: Check Logs
In Django admin:
- Go to `/admin/appointments/appointmentreminder/`
- Check status of sent SMS
- View any error messages

---

## 💰 Cost Comparison (Uganda)

| Provider | Per SMS | 1000 SMS | 10,000 SMS |
|----------|---------|----------|------------|
| Africa's Talking | ~UGX 130 | ~UGX 130,000 | ~UGX 1,300,000 |
| People's SMS | Contact | Contact | Contact |
| SMS Box | Contact | Contact | Contact |

**Clinic Example:**
- 50 patients/day
- 3 reminders each = 150 SMS/day
- Monthly: ~4,500 SMS = ~UGX 585,000

---

## 🔧 Troubleshooting

### SMS Not Sending?

**Check 1: Is SMS Enabled?**
```bash
# In Django shell
python manage.py shell
>>> from appointments.models import ReminderSettings
>>> settings = ReminderSettings.objects.first()
>>> print(settings.sms_enabled)  # Should be True
```

**Check 2: Are Credentials Correct?**
```bash
# Check .env file
notepad .env
# Verify SMS_PROVIDER and credentials
```

**Check 3: Test Manually**
```python
# In Django shell
python manage.py shell
>>> from appointments.sms_services import send_sms
>>> send_sms('+256700000000', 'Test message')
```

**Check 4: Phone Number Format**
- Must be in international format
- Include country code
- Example: `+256700000000` (Uganda)

### Common Errors

**Error**: "No SMS service configured"
- **Fix**: Add SMS configuration to `.env` file

**Error**: "API request failed"
- **Fix**: Check API key is correct
- **Fix**: Check you have credits (for production)

**Error**: "Invalid phone number"
- **Fix**: Use international format (+256...)

---

## 🚀 Going to Production

### Checklist

- [ ] Switch from sandbox to production credentials
- [ ] Add credits to SMS provider account
- [ ] Test with real phone numbers
- [ ] Monitor first batch of SMS
- [ ] Set up credit alerts (low balance warnings)
- [ ] Update .env with production credentials
- [ ] Restart Django server
- [ ] Test end-to-end

### Production .env

```bash
# Production SMS Configuration
SMS_PROVIDER=africas_talking
AFRICAS_TALKING_API_KEY=atsk_production_key_here
AFRICAS_TALKING_USERNAME=YourProductionAppName  # NOT 'sandbox'
```

---

## 📊 Monitoring SMS

### View Sent SMS
1. Django Admin: `/admin/appointments/appointmentreminder/`
2. Filter by:
   - Status (sent/failed)
   - Method (sms)
   - Date range

### SMS Statistics
Check these metrics:
- Total SMS sent
- Failed SMS
- Average delivery rate
- Cost per day/week/month

---

## 💡 Tips for Saving Money

1. **Optimize Messages**: Keep messages under 160 characters
2. **Reduce Frequency**: Maybe skip "final reminder" for confirmed appointments
3. **Smart Targeting**: Only send to patients who need reminders
4. **Bulk Credits**: Buy SMS credits in bulk for better rates
5. **Monitor Usage**: Check daily SMS count

---

## 📞 Support Contacts

### Africa's Talking
- Website: https://africastalking.com/
- Email: support@africastalking.com
- Docs: https://developers.africastalking.com/

### People's SMS
- Website: https://peoplessms.com/
- Contact: Check website for details

### SMS Box
- Website: https://smsbox.co.ug/
- Contact: Check website for details

---

## ✅ Quick Start Checklist

- [ ] Choose SMS provider (recommend: Africa's Talking)
- [ ] Sign up for free account
- [ ] Get API credentials
- [ ] Add to `.env` file
- [ ] Enable SMS in reminder settings
- [ ] Test with dry-run
- [ ] Test with real SMS
- [ ] Monitor results
- [ ] Go to production when ready

---

## 🎉 You're Done!

Your appointment reminder system now sends SMS messages!

**Remember:**
- Start with sandbox/testing (free)
- Test thoroughly before production
- Monitor costs and delivery rates
- Keep API keys secure

Need help? Check the main documentation: `APPOINTMENT_REMINDERS_SETUP.md`
