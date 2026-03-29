# 📄 Prescription Print & Email - Quick Reference

## 🖨️ How to Print a Prescription

### Method 1: From Prescription List
1. Navigate to **Pharmacy** → **Prescriptions**
2. Find the prescription you want to print
3. Click the **printer icon** (🖨️) in the Actions column
4. A new window opens with the formatted prescription
5. Click the **"Print"** button (or press Ctrl+P)
6. Select your printer and print

### Method 2: Direct URL
- Visit: `/pharmacy/prescriptions/<PRESCRIPTION_ID>/print/`
- Replace `<PRESCRIPTION_ID>` with the actual prescription number

## 📧 How to Email a Prescription

### From Prescription List:
1. Navigate to **Pharmacy** → **Prescriptions**
2. Find the prescription (patient must have email)
3. Click the **envelope icon** (📧) in the Actions column
4. Confirm sending in the popup dialog
5. System sends email and displays success message

### What Patient Receives:
- Email subject: "Prescription from PhysioNutrition Clinic - RX-XXXXX"
- Complete prescription details
- Medication, dosage, frequency, duration
- Special instructions
- Professionally formatted HTML

## 📋 Prescription Template Features

### Document Contains:
- ✅ Clinic name, address, and contact information
- ✅ Prescription number with barcode
- ✅ Patient information (name, ID, age, gender)
- ✅ Medication details with icons
- ✅ Dosage, frequency, duration, quantity
- ✅ Special instructions (if any)
- ✅ Prescribed by doctor name and date
- ✅ Dispensed by pharmacist (if applicable)
- ✅ Important safety warnings
- ✅ Professional signatures section

### Visual Elements:
- 🎨 Medical-grade typography (Times New Roman)
- 💊 Prominent ℞ (Rx) symbol watermark
- 🏥 Clinic branding colors (Blue & Green)
- 📐 Professional layout with clear sections
- ⚠️ Highlighted warnings and instructions

## 🔧 Action Buttons

### On Print Page:
| Button | Icon | Function |
|--------|------|----------|
| **Print** | 🖨️ | Opens browser print dialog |
| **Send Email** | 📧 | Emails prescription to patient |
| **Close** | ✖️ | Closes the print window |

### On Prescription List:
| Button | Icon | Status | Function |
|--------|------|--------|----------|
| **Print** | 🖨️ | Always | Opens print view in new tab |
| **Email** | 📧 | If patient has email | Sends prescription via email |
| **Email Disabled** | 📧 | If no email | Shows email not available |

## ⚡ Quick Tips

### For Faster Printing:
- Use the auto-print URL: `/pharmacy/prescriptions/<ID>/print/?auto_print=true`
- Automatically triggers print dialog when page loads

### For Better Print Quality:
- Use "Save as PDF" in print dialog for digital copies
- Select "Print backgrounds" for colored sections
- Use A4 or Letter paper size

### For Email Issues:
- Verify patient email address is correct
- Check spam/junk folder if not received
- Contact IT if email fails to send

## 📱 Access Points

### Where to Find Prescriptions:
1. **Main Menu** → Pharmacy → Prescriptions
2. **Sales Dashboard** → Prescriptions section
3. **Patient Detail Page** → Medications tab

### Quick URLs:
- List: `/pharmacy/prescriptions/`
- Print: `/pharmacy/prescriptions/<ID>/print/`
- Email: `/pharmacy/prescriptions/<ID>/email/`

## ❓ Common Questions

### Q: Can I print old prescriptions?
**A:** Yes! All prescriptions (pending, dispensed, cancelled) can be printed.

### Q: What if patient has no email?
**A:** The email button will be disabled. You can only print or give printed copy.

### Q: Can I edit a prescription before printing?
**A:** No. The document shows prescription as recorded. Edit the prescription first if changes needed.

### Q: Who can print/email prescriptions?
**A:** Only logged-in staff members with pharmacy access can print or email prescriptions.

### Q: Is the email secure?
**A:** Yes! Emails are sent via secure SMTP connection with TLS encryption.

### Q: Can I add clinic logo?
**A:** Yes! Contact IT administrator to customize the template with clinic logo.

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Print button not working | Check browser pop-up blocker |
| Email not sending | Verify email server configuration |
| Missing clinic info | Update clinic settings in admin panel |
| Layout issues | Try different browser or update current one |
| Patient email not showing | Add email to patient profile |

## 📞 Need Help?

Contact your system administrator if:
- Emails are not being sent
- Print layout looks incorrect
- Clinic information is wrong
- Technical errors occur

---

**System Version**: 1.0  
**Last Updated**: November 2024  
**Support**: IT Department
