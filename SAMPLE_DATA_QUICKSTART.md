# Sample Data Quick Start

## Generate Sample Data - 3 Simple Steps

### Step 1: Navigate to Project Directory
```bash
cd /path/to/PhysioNutritionClinic
```

### Step 2: Run the Command
```bash
python manage.py generate_sample_data
```

### Step 3: Login and Explore
- **URL:** http://localhost:8000/admin
- **Username:** admin
- **Password:** admin123

That's it! Your system now has:
- ✅ 15 staff users
- ✅ 30 patients  
- ✅ 45+ appointments
- ✅ Lab tests and results
- ✅ Medications and prescriptions
- ✅ Invoices and payments
- ✅ And much more!

---

## Quick Commands

### Default Generation (Recommended)
```bash
python manage.py generate_sample_data
```
Creates 15 users and 30 patients with all related data.

### Custom Amounts
```bash
# More users and patients
python manage.py generate_sample_data --users 20 --patients 50

# Minimal data for testing
python manage.py generate_sample_data --users 5 --patients 10
```

### Clear and Regenerate
```bash
# ⚠️ Warning: Deletes existing sample data!
python manage.py generate_sample_data --clear
```

### Run Multiple Times (Safe)
```bash
# You can run this multiple times without --clear
# New data will be added with unique IDs
python manage.py generate_sample_data
```
**Note:** The command intelligently avoids duplicate IDs by checking existing records.

---

## Login Credentials

### Admin Access
| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Superuser |

### Staff Access (Pattern: `{role}{number}`)
| Username | Password | Role |
|----------|----------|------|
| doctor1 | password123 | Doctor |
| nutritionist1 | password123 | Nutritionist |
| receptionist1 | password123 | Receptionist |
| nurse1 | password123 | Nurse |
| billing1 | password123 | Billing Staff |

**Note:** Numbers increment (doctor2, doctor3, etc.)

---

## What Gets Created

### Core Data
- 📋 **Users:** Admin + staff with different roles
- 🏥 **Patients:** Regular (PT-000001) and visiting (VP-000001)
- 📅 **Appointments:** Past, current, and future (30 days range)
- 💉 **Services:** Physiotherapy, nutrition, consultations

### Clinical Data
- 🩺 **Vital Signs:** Blood pressure, heart rate, temperature, etc.
- 🚨 **Triages:** Priority assessments with departments
- 📝 **Assessments:** Clinical evaluations with diagnoses
- 🏋️ **Treatment Sessions:** Physiotherapy session notes
- 🥗 **Nutrition Consultations:** Dietary planning records

### Laboratory
- 🔬 **Lab Tests:** CBC, FBS, Lipid Profile, LFT
- 📊 **Lab Requests:** Test orders with results

### Pharmacy
- 💊 **Medications:** Paracetamol, Ibuprofen, Amoxicillin, Metformin
- 📦 **Batches:** Stock with expiry dates
- 📋 **Prescriptions:** Patient prescriptions with medications
- 🏪 **Suppliers:** Pharmaceutical suppliers

### Billing
- 🧾 **Invoices:** Draft, sent, and paid invoices
- 💰 **Payments:** Cash, card, and bank transfers
- 🏥 **Insurance Claims:** Claims for insured patients

---

## Data Summary (Default Generation)

| Category | Count | Details |
|----------|-------|---------|
| Users | 15 | Admin + staff (various roles) |
| Patients | 30 | 27 regular + 3 visiting |
| Services | 6 | Therapy, nutrition, consultations |
| Appointments | 45+ | Past 30 days + future 14 days |
| Vital Signs | 15 | For 50% of patients |
| Assessments | 15 | Various departments |
| Lab Requests | 20 | With results |
| Medications | 4 | Common medications |
| Prescriptions | 10 | Multi-medication prescriptions |
| Invoices | 15 | Various statuses |
| Payments | 7+ | For paid invoices |

---

## Common Use Cases

### 1. Development Testing
```bash
# Generate once at start of development
python manage.py generate_sample_data
```

### 2. Demo Preparation
```bash
# Generate lots of data for impressive demo
python manage.py generate_sample_data --users 30 --patients 100 --clear
```

### 3. Feature Testing
```bash
# Minimal data for focused testing
python manage.py generate_sample_data --users 5 --patients 10
```

### 4. After Model Changes
```bash
# Clear old data and regenerate
python manage.py generate_sample_data --clear
```

---

## Quick Tips

### ✅ Do This
- Run on local development database
- Use for testing and demos
- Customize user/patient counts as needed
- Clear data when model structure changes

### ❌ Don't Do This
- Run on production database
- Use generated passwords in production
- Rely on sample data for real operations
- Forget to backup before using `--clear`

---

## Troubleshooting

### Command Not Found?
```bash
# Make sure you're in the project directory
python manage.py help generate_sample_data
```

### Database Errors?
```bash
# Run migrations first
python manage.py migrate
```

### Already Have Data?
```bash
# Use --clear to remove existing sample data
python manage.py generate_sample_data --clear
```

---

## Next Steps

1. **Explore the System:**
   - Login as admin
   - Browse patients, appointments, invoices
   - Try different user roles

2. **Test Features:**
   - Create new appointments
   - Record vital signs
   - Generate invoices
   - Process payments

3. **Review Data:**
   - Check patient records
   - View lab results
   - Review prescriptions
   - Examine billing reports

4. **Customize:**
   - Adjust user/patient counts
   - Modify sample data in code
   - Add your own test scenarios

---

## Need More Help?

📖 **Read Full Documentation:**
See `SAMPLE_DATA_GUIDE.md` for complete details

🔧 **Customize Generation:**
Edit `patients/management/commands/data_generators.py`

🐛 **Report Issues:**
Check error messages and verify migrations are up to date

---

## Quick Reference Card

```bash
# Basic Commands
python manage.py generate_sample_data          # Default generation
python manage.py generate_sample_data --clear  # Clear and regenerate
python manage.py generate_sample_data --users 20 --patients 50  # Custom amounts

# Login
URL: http://localhost:8000/admin
Username: admin
Password: admin123

# Staff Pattern
Username: {role}{number}  (e.g., doctor1, nurse2)
Password: password123
```

---

**Ready to start? Run the command and explore your clinic management system! 🏥**
