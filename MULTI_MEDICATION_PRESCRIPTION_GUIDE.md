# 💊 Multi-Medication Prescription System

## Overview

The prescription system now supports **multiple medications on a single prescription form**. This allows doctors to prescribe several medications at once, and they will all appear on one printed prescription document.

---

## ✨ Features

### **Multiple Medications**
- ✅ Add 2, 3, 5, or any number of medications to one prescription
- ✅ Each medication has its own dosage, frequency, duration, and quantity
- ✅ All medications print together on one form
- ✅ Clean table format for easy reading

### **Backward Compatibility**
- ✅ Old single-medication prescriptions still work
- ✅ System automatically detects legacy prescriptions
- ✅ No data loss from existing prescriptions

---

## 📋 How to Create a Multi-Medication Prescription

### **Method 1: Django Admin (Recommended)**

1. **Navigate to Admin**
   - Go to Django Admin
   - Click **Pharmacy** → **Prescriptions**

2. **Add New Prescription**
   - Click **"Add Prescription"** button
   - Fill in prescription header:
     - Patient (search and select)
     - Status (Pending/Dispensed)
     - Prescribed By (auto-filled with your name)
     - Instructions (optional general instructions)

3. **Add Medications**
   - Scroll to **"Medications"** section (inline table)
   - You'll see 2 empty rows by default
   - For each medication:
     - **Medication**: Select from dropdown
     - **Dosage**: e.g., "500mg", "10ml", "2 tablets"
     - **Frequency**: e.g., "Twice daily", "3x per day", "Every 8 hours"
     - **Duration**: e.g., "7 days", "2 weeks", "1 month"
     - **Quantity**: Number of units (e.g., 14, 30, 60)
     - **Notes**: Optional notes for this specific medication

4. **Add More Medications**
   - Need more rows? Scroll to bottom
   - Click **"Add another Medication"**
   - Repeat as needed

5. **Save**
   - Click **"Save"** button
   - Prescription created with all medications!

### **Example Prescription**

```
Patient: John Doe
Prescribed By: Dr. Smith
Date: November 10, 2024

Medications:
1. Amoxicillin 500mg | 3x daily | 7 days | Qty: 21 tablets
2. Paracetamol 500mg | Every 6 hours | 5 days | Qty: 20 tablets
3. Omeprazole 20mg | Once daily (morning) | 14 days | Qty: 14 capsules

General Instructions: Take all medications with food. Complete full course.
```

---

## 🖨️ Printing Multi-Medication Prescriptions

### **Access Print View**

1. Go to **Pharmacy** → **Prescriptions**
2. Find the prescription in the list
3. Click the **printer icon** (🖨️)
4. New window opens with formatted prescription

### **Prescription Format**

```
┌───────────────────────────────────────────────────┐
│  CLINIC HEADER                                    │
│  PhysioNutrition Clinic    ℞ PRESCRIPTION         │
│  Contact Info              RX-00001               │
├───────────────────────────────────────────────────┤
│  Patient Info  | Prescriber Info                  │
├───────────────────────────────────────────────────┤
│  MEDICATIONS PRESCRIBED                           │
│  ┌──────────────────────────────────────────┐    │
│  │ Medication | Dosage | Freq | Dur | Qty   │    │
│  ├──────────────────────────────────────────┤    │
│  │ ℞ Med 1   | 500mg  | 2x   | 7d  | 14    │    │
│  │ ℞ Med 2   | 250mg  | 3x   | 5d  | 15    │    │
│  │ ℞ Med 3   | 100mg  | 1x   | 30d | 30    │    │
│  └──────────────────────────────────────────┘    │
│  Special Instructions: [if any]                   │
│  Terms & Conditions (at bottom)                   │
└───────────────────────────────────────────────────┘
```

### **All Medications in One Table**
- Each medication appears as a row
- Easy to scan and read
- Professional medical document format
- Fits on single A4 page (unless many medications)

---

## 📊 Medication Table Layout

| Column | Width | Content Example |
|--------|-------|-----------------|
| **Medication Name** | 35% | ℞ Amoxicillin 500mg Capsules |
| **Dosage** | 18% | 500mg |
| **Frequency** | 18% | 3 times daily |
| **Duration** | 15% | 7 days |
| **Quantity** | 14% | 21 tablets |

---

## 🔄 Updating Existing Prescriptions

### **Add Medications to Existing Prescription**

1. Go to Django Admin → Prescriptions
2. Click on existing prescription
3. Scroll to **"Medications"** section
4. Click **"Add another Medication"**
5. Fill in medication details
6. Save

### **Edit Medication Details**

1. Open prescription in admin
2. Find medication in inline table
3. Update any field (dosage, frequency, etc.)
4. Save

### **Remove Medication**

1. Open prescription in admin
2. Find medication in inline table
3. Check the **"Delete"** checkbox
4. Save

---

## 📧 Email Multi-Medication Prescriptions

- Works exactly the same as before
- Click **envelope icon** (📧) next to prescription
- Patient receives email with all medications listed
- HTML formatted for readability

---

## 🔍 Searching Prescriptions

### **Find by Medication**

- Admin search now includes medication items
- Search for any medication name
- Returns all prescriptions containing that medication

### **Example Searches**
- "Amoxicillin" - All prescriptions with Amoxicillin
- "John Doe" - All prescriptions for patient John Doe
- "Dr. Smith" - All prescriptions by Dr. Smith

---

## 📈 Benefits

### **For Doctors**
- ✅ **Faster prescribing** - One form for multiple meds
- ✅ **Better organization** - All related medications together
- ✅ **Reduced paperwork** - Single document instead of multiple
- ✅ **Professional appearance** - Clean table format

### **For Pharmacists**
- ✅ **Clear overview** - All medications visible at once
- ✅ **Easy dispensing** - Check off each medication
- ✅ **Reduced errors** - Everything on one form
- ✅ **Faster processing** - No need to handle multiple forms

### **For Patients**
- ✅ **Single document** - Easy to keep track
- ✅ **Clear instructions** - All medications in one place
- ✅ **Professional** - Clean, organized format
- ✅ **Easy reference** - One form to bring to pharmacy

---

## 💡 Best Practices

### **When to Use Multi-Medication**
✅ Treating multiple conditions simultaneously
✅ Combination therapy (antibiotics + pain relief + supplements)
✅ Chronic condition management with multiple drugs
✅ Follow-up visits with medication adjustments

### **Prescribing Guidelines**
1. **Group related medications** - Put them on same prescription
2. **Clear dosages** - Use standard medical abbreviations
3. **Specific frequencies** - "3 times daily" better than "TDS"
4. **Exact durations** - "7 days" instead of "1 week"
5. **General instructions** - Use instructions field for overall guidance

### **Medication Order**
- List most important medication first
- Group by purpose (e.g., all pain meds together)
- Consider administration times
- Antibiotics typically first

---

## 🔧 Technical Details

### **Database Structure**

```
Prescription (Header)
├── patient
├── prescribed_by
├── prescribed_date
├── status
├── instructions (general)
└── PrescriptionItems (Multiple)
    ├── medication
    ├── dosage
    ├── frequency
    ├── duration
    ├── quantity
    └── notes (specific to this medication)
```

### **Model Files**
- `pharmacy/models.py` - Prescription and PrescriptionItem models
- `pharmacy/admin.py` - Admin interface with inline items
- `pharmacy/templates/prescription_print.html` - Print template

### **Key Methods**
- `prescription.get_medications()` - Returns all medications (new or legacy)
- `prescription.items.all()` - Direct access to PrescriptionItem queryset
- `prescription.items.count()` - Number of medications

---

## 📝 Common Scenarios

### **Scenario 1: Cold & Flu Treatment**
```
Medications:
1. Paracetamol 500mg | Every 6 hours | 5 days | 20 tablets
2. Dextromethorphan syrup | 10ml 3x daily | 5 days | 150ml
3. Vitamin C 1000mg | Once daily | 7 days | 7 tablets
```

### **Scenario 2: Post-Surgery Care**
```
Medications:
1. Amoxicillin 500mg | 3x daily | 7 days | 21 capsules
2. Ibuprofen 400mg | Every 8 hours as needed | 5 days | 15 tablets
3. Omeprazole 20mg | Once daily (morning) | 14 days | 14 capsules
4. Wound care cream | Apply 2x daily | 10 days | 1 tube
```

### **Scenario 3: Chronic Disease Management**
```
Medications:
1. Metformin 500mg | Twice daily with meals | 30 days | 60 tablets
2. Enalapril 10mg | Once daily (morning) | 30 days | 30 tablets
3. Aspirin 75mg | Once daily | 30 days | 30 tablets
4. Atorvastatin 20mg | Once daily (evening) | 30 days | 30 tablets
```

---

## ⚠️ Important Notes

### **Legacy Prescriptions**
- Old single-medication prescriptions still work
- They display in same format as new ones
- No need to migrate old data
- System handles both automatically

### **Migration**
- Migration already applied: `0013_alter_prescription_dosage_and_more`
- Adds `PrescriptionItem` table
- Makes medication fields optional for backward compatibility
- No data loss

### **Limitations**
- Maximum medications: No limit (but keep reasonable for one page)
- Recommended: 1-10 medications per prescription
- Very long lists may need multiple pages

---

## 🚀 Quick Start Checklist

For a new multi-medication prescription:

- [ ] Open Django Admin → Pharmacy → Prescriptions
- [ ] Click "Add Prescription"
- [ ] Select patient
- [ ] Add first medication (details in inline table)
- [ ] Add second medication (click "Add another")
- [ ] Add third medication (and so on...)
- [ ] Add general instructions if needed
- [ ] Save prescription
- [ ] Print from prescription list (printer icon)
- [ ] Verify all medications appear on form

---

## 📞 Support

### **Issues or Questions?**
- Check this guide first
- Review `PRESCRIPTION_PRINT_EMAIL_GUIDE.md` for printing details
- Contact system administrator

### **Feature Requests?**
- Additional medication fields needed?
- Different table layout?
- Custom medication grouping?
→ Discuss with development team

---

## ✅ Summary

The multi-medication prescription system allows you to:

1. ✅ **Add multiple medications** to one prescription
2. ✅ **Print all medications** on one form
3. ✅ **Easy management** through Django admin
4. ✅ **Professional output** with table format
5. ✅ **Backward compatible** with old prescriptions

**Start using it today for more efficient prescribing!** 💊📋

---

**Version**: 4.0 (Multi-Medication)  
**Feature**: Multiple medications per prescription  
**Status**: ✅ Production Ready  
**Updated**: November 10, 2024
