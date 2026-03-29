# Sample Data Generator Guide

## Overview
The PhysioNutritionClinic system includes a comprehensive sample data generator that creates realistic test data across all modules for development, testing, and demonstration purposes.

## Features
- **18 Data Types Generated**: Users, patients, appointments, assessments, lab tests, medications, invoices, and more
- **Realistic Data**: Uses Ugandan names, cities, phone numbers, and currency (UGX)
- **Configurable**: Customize number of users and patients
- **Safe**: Option to clear existing data before generation
- **Complete**: Generates interconnected data across all modules

## Usage

### Basic Generation
```bash
python manage.py generate_sample_data
```
This creates:
- 15 staff users (default)
- 30 patients (default)
- All related data (appointments, assessments, invoices, etc.)

### Custom Amounts
```bash
# Generate 20 users and 50 patients
python manage.py generate_sample_data --users 20 --patients 50
```

### Clear and Regenerate
```bash
# Clear existing data before generating new data
python manage.py generate_sample_data --clear
```

### Multiple Runs (Additive)
```bash
# Running without --clear will ADD new data with unique IDs
python manage.py generate_sample_data
python manage.py generate_sample_data  # Safe to run again
```
**Smart ID Generation:** The command checks for existing records and generates unique IDs:
- Invoices: INV-000001, INV-000002, etc. (continues from last)
- Payments: PAY-000001, PAY-000002, etc.
- Claims: CLM-000001, CLM-000002, etc.
- Batches: BATCH000001, BATCH000002, etc.

## Generated Data

### 1. Users (Staff) - Default: 15
**Roles Created:**
- Admin (superuser)
- Doctors/Physiotherapists
- Nutritionists
- Receptionists
- Nurses
- Billing staff

**Default Credentials:**
- Superuser: `admin` / `admin123`
- All others: `{role}{number}` / `password123`
- Example: `doctor1` / `password123`

### 2. Services - 6 Types
- Initial Physiotherapy Assessment (80,000 UGX)
- Physiotherapy Treatment Session (60,000 UGX)
- Nutrition Consultation (65,000 UGX)
- Dietary Planning (45,000 UGX)
- General Consultation (50,000 UGX)
- Follow-up Consultation (35,000 UGX)

### 3. Patients - Default: 30
**Patient Types:**
- 90% Regular patients (PT-000001 format)
- 10% Visiting patients (VP-000001 format)

**Data Includes:**
- Ugandan names and cities
- Phone numbers (+256 format)
- Emergency contacts
- Blood types
- Allergies
- Insurance information (some patients)

### 4. Vital Signs - ~15 Records
Generated for 50% of patients:
- Height, weight (BMI calculated automatically)
- Blood pressure (systolic/diastolic)
- Heart rate, temperature
- Respiratory rate, oxygen saturation

### 5. Triages - ~10 Records
Generated for 33% of patients:
- Assigned departments (physiotherapy/nutrition/general)
- Chief complaints
- Pain scale (0-10)
- Priority levels (1-5)
- Symptoms and onset information

### 6. Assessments - ~15 Records
Generated for 50% of patients:
- First visit and follow-up assessments
- Department-specific (physiotherapy/nutrition/general)
- Chief complaints and diagnoses
- Treatment plans
- Physical examination findings

### 7. Appointments - ~30-60 Records
**Date Range:** Past 30 days to future 14 days
**Status Distribution:**
- Past appointments: Completed or No-show
- Today appointments: In Progress
- Future appointments: Scheduled or Confirmed

### 8. Treatment Sessions - ~5-10 Records
For completed physiotherapy appointments:
- Assessment findings
- Treatment provided
- Pain levels (before/after)
- Patient response
- Home exercises and recommendations

### 9. Nutrition Consultations - ~5-10 Records
For completed nutrition appointments:
- Current diet and dietary restrictions
- Health goals (weight loss, better energy, etc.)
- Current and target weight
- Meal plans
- Supplement recommendations

### 10. Laboratory Tests - 4 Types
- CBC (Complete Blood Count) - 50,000 UGX
- FBS (Fasting Blood Sugar) - 25,000 UGX
- LIPID (Lipid Profile) - 75,000 UGX
- LFT (Liver Function Test) - 80,000 UGX

### 11. Lab Requests - ~20 Records
Generated for 33% of patients:
- 2 random tests per patient
- All marked as completed
- Results included

### 12. Pharmacy Data

**Suppliers - 3 Companies:**
- Supplier 1, 2, 3 (Kampala-based)

**Categories - 3 Types:**
- Analgesics
- Antibiotics
- Vitamins

**Medications - 4 Types:**
- Paracetamol 500mg tablets (1,000 UGX)
- Ibuprofen 400mg tablets (2,000 UGX)
- Amoxicillin 500mg capsules (3,000 UGX)
- Metformin 500mg tablets (2,500 UGX)

**Batches - 4 Batches:**
- Stock levels: 100-1,000 units
- Expiry dates: 1-2 years from now
- Status: Active

**Prescriptions - ~10 Records:**
- Generated for 33% of patients
- 2 medications per prescription
- Status: Pending or Dispensed

### 13. Billing Data

**Invoices - ~15 Records:**
- Generated for 50% of patients
- Invoice numbers: INV-000001 format
- Status: Draft, Sent, or Paid
- Due date: 30 days from creation
- 2 random services per invoice

**Payments - ~5-10 Records:**
- Only for invoices with "Paid" status
- Payment IDs: PAY-000001 format
- Methods: Cash, Credit Card, Bank Transfer
- Status: Completed

**Insurance Claims - ~5 Records:**
- Only for patients with insurance
- Claim numbers: CLM-000001 format
- Status: Submitted, Approved, or Paid
- Links to invoices

## Data Relationships

```
Users
├── Registered Patients
├── Recorded Vital Signs
├── Performed Triages
├── Conducted Assessments
├── Provider for Appointments
├── Created Invoices
└── Processed Payments

Patients
├── Vital Signs
├── Triages
├── Assessments
├── Appointments
│   ├── Treatment Sessions
│   └── Nutrition Consultations
├── Lab Requests
│   └── Lab Results
├── Prescriptions
├── Invoices
│   ├── Invoice Line Items
│   ├── Payments
│   └── Insurance Claims
└── Related to Services

Medications
├── Batches
├── Prescriptions
└── Categories
```

## Sample Data Characteristics

### Realistic Ugandan Context
- **Cities**: Kampala, Entebbe, Mbarara, Gulu, Jinja, etc.
- **Phone Numbers**: +256 7XX XXX XXX format
- **Currency**: UGX (Ugandan Shillings)
- **Insurance**: AAR Healthcare, Jubilee, UAP

### Medical Conditions
- Hypertension
- Diabetes Type 2
- Asthma
- Arthritis
- Back Pain
- Sports Injuries
- Obesity
- Malnutrition

### Chief Complaints
- Lower back pain
- Knee pain after exercise
- Shoulder stiffness
- Weight management consultation
- Post-surgery rehabilitation
- Chronic neck pain
- Dietary counseling

## Development Workflow

### 1. Initial Setup
```bash
# First time setup - create sample data
python manage.py generate_sample_data
```

### 2. Testing Changes
```bash
# Clear and regenerate data after model changes
python manage.py generate_sample_data --clear
```

### 3. Demo Preparation
```bash
# Generate lots of data for demonstration
python manage.py generate_sample_data --users 30 --patients 100 --clear
```

### 4. Specific Testing
```bash
# Generate minimal data for specific feature testing
python manage.py generate_sample_data --users 5 --patients 10
```

## Login Credentials

### Superuser
- **Username:** admin
- **Password:** admin123
- **Access:** Full system access

### Staff Users
All created with pattern: `{role}{number}`

**Examples:**
- `doctor1` / `password123`
- `doctor2` / `password123`
- `nutritionist1` / `password123`
- `receptionist1` / `password123`
- `nurse1` / `password123`
- `billing1` / `password123`

## Best Practices

### For Development
1. Generate sample data on local development database
2. Don't run on production databases
3. Use `--clear` flag when model structure changes
4. Customize user/patient count based on testing needs

### For Testing
1. Generate fresh data before major testing sessions
2. Use realistic amounts (30-50 patients) for UI testing
3. Test with both regular and visiting patients
4. Verify all relationships are created correctly

### For Demonstration
1. Generate larger datasets (50-100 patients)
2. Ensure all statuses are represented
3. Include past, current, and future appointments
4. Show variety in payment methods and statuses

## Troubleshooting

### Issue: Command Not Found
```bash
# Ensure you're in the project directory
cd /path/to/PhysioNutritionClinic

# Check management command exists
python manage.py help generate_sample_data
```

### Issue: Database Errors
```bash
# Run migrations first
python manage.py migrate

# Then generate data
python manage.py generate_sample_data
```

### Issue: Duplicate Data
```bash
# Use --clear flag to remove existing data first
python manage.py generate_sample_data --clear
```

### Issue: Foreign Key Errors
```bash
# Ensure all apps are migrated
python manage.py migrate

# Check for circular dependencies in models
```

## Customization

### Modify Data Amounts
Edit `data_generators.py` and adjust the generation logic:
- Change proportions (e.g., 50% of patients → 75%)
- Add more sample names, cities, conditions
- Adjust date ranges for appointments
- Modify price ranges for services

### Add New Data Types
1. Create new generator method in `DataGenerator` class
2. Add call to method in `generate_all_data()`
3. Import required models
4. Follow existing patterns for consistency

### Customize Sample Values
Edit constants in `data_generators.py`:
- `FIRST_NAMES` - Add more first names
- `LAST_NAMES` - Add more last names
- `UGANDAN_CITIES` - Add more cities
- `MEDICAL_CONDITIONS` - Add more conditions
- `CHIEF_COMPLAINTS` - Add more complaints

## Statistics

After generation, the command prints a summary:
```
======================================================================
SUMMARY
======================================================================
  Users: 15
  Services: 6
  Patients: 30
  Vital Signs: 15
  Triages: 10
  Assessments: 15
  Appointments: 45
  Treatment Sessions: 8
  Nutrition Consultations: 6
  Lab Tests: 4
  Lab Requests: 20
  Suppliers: 3
  Categories: 3
  Medications: 4
  Batches: 4
  Prescriptions: 10
  Invoices: 15
  Payments: 7
  Insurance Claims: 5
```

## Safety Notes

⚠️ **Important:**
- Never run on production databases
- Always backup before using `--clear` flag
- Generated data is for testing only
- Password is NOT secure (`password123`)
- Email addresses are fake

## Support

For issues or questions:
1. Check this documentation
2. Review error messages carefully
3. Verify migrations are up to date
4. Check model relationships in code

## Version Information

- **Created:** November 2024
- **Compatible with:** PhysioNutritionClinic v1.0
- **Django Version:** 4.x+
- **Python Version:** 3.8+
