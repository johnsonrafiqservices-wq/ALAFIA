#!/usr/bin/env python
"""
Sample data population script for Physio & Nutrition Clinic
Creates realistic test data for financial reports and analytics
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
from decimal import Decimal
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic_system.settings')
django.setup()

from patients.models import Patient, VitalSigns, Triage, Assessment
from appointments.models import Appointment, Service
from billing.models import Invoice, InvoiceLineItem, Payment, InsuranceClaim
from accounts.models import User
from django.contrib.auth.hashers import make_password

def create_services():
    """Create service offerings"""
    services = [
        {'name': 'Initial Physiotherapy Assessment', 'category': 'assessment', 'base_price': 120.00, 'duration_minutes': 60, 'description': 'Comprehensive initial assessment'},
        {'name': 'Physiotherapy Session', 'category': 'physiotherapy', 'base_price': 85.00, 'duration_minutes': 45, 'description': 'Individual physiotherapy treatment'},
        {'name': 'Group Physiotherapy', 'category': 'physiotherapy', 'base_price': 45.00, 'duration_minutes': 60, 'description': 'Group exercise therapy'},
        {'name': 'Initial Nutrition Consultation', 'category': 'consultation', 'base_price': 150.00, 'duration_minutes': 90, 'description': 'Comprehensive nutrition assessment'},
        {'name': 'Nutrition Follow-up', 'category': 'nutrition', 'base_price': 90.00, 'duration_minutes': 45, 'description': 'Follow-up nutrition consultation'},
        {'name': 'Meal Planning Session', 'category': 'nutrition', 'base_price': 75.00, 'duration_minutes': 30, 'description': 'Personalized meal planning'},
        {'name': 'Body Composition Analysis', 'category': 'assessment', 'base_price': 65.00, 'duration_minutes': 30, 'description': 'InBody analysis and consultation'},
        {'name': 'Sports Injury Assessment', 'category': 'assessment', 'base_price': 140.00, 'duration_minutes': 60, 'description': 'Specialized sports injury evaluation'},
        {'name': 'Ergonomic Assessment', 'category': 'assessment', 'base_price': 110.00, 'duration_minutes': 45, 'description': 'Workplace ergonomic evaluation'},
        {'name': 'Rehabilitation Program', 'category': 'treatment', 'base_price': 95.00, 'duration_minutes': 60, 'description': 'Structured rehabilitation session'},
    ]
    
    created_services = []
    for service_data in services:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults={
                'category': service_data['category'],
                'base_price': service_data['base_price'],
                'duration_minutes': service_data['duration_minutes'],
                'description': service_data['description'],
                'is_active': True
            }
        )
        created_services.append(service)
        if created:
            print(f"Created service: {service.name}")
    
    return created_services

def create_patients():
    """Create 50 sample patients"""
    first_names = [
        'John', 'Sarah', 'Michael', 'Emily', 'David', 'Lisa', 'Robert', 'Jennifer', 'William', 'Amanda',
        'James', 'Michelle', 'Christopher', 'Jessica', 'Matthew', 'Ashley', 'Daniel', 'Stephanie', 'Kevin', 'Nicole',
        'Ryan', 'Lauren', 'Brandon', 'Megan', 'Tyler', 'Rachel', 'Andrew', 'Samantha', 'Joshua', 'Elizabeth',
        'Nathan', 'Kimberly', 'Alexander', 'Amy', 'Benjamin', 'Angela', 'Jacob', 'Melissa', 'Nicholas', 'Rebecca',
        'Anthony', 'Laura', 'Jonathan', 'Sharon', 'Mark', 'Cynthia', 'Steven', 'Kathleen', 'Paul', 'Helen'
    ]
    
    last_names = [
        'Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Anderson', 'Taylor', 'Martinez', 'Garcia', 'Rodriguez',
        'Lee', 'White', 'Harris', 'Clark', 'Lewis', 'Walker', 'Hall', 'Allen', 'Young', 'King',
        'Wright', 'Lopez', 'Hill', 'Scott', 'Green', 'Adams', 'Baker', 'Gonzalez', 'Nelson', 'Carter',
        'Mitchell', 'Perez', 'Roberts', 'Turner', 'Phillips', 'Campbell', 'Parker', 'Evans', 'Edwards', 'Collins',
        'Stewart', 'Sanchez', 'Morris', 'Rogers', 'Reed', 'Cook', 'Morgan', 'Bell', 'Murphy', 'Bailey'
    ]
    
    insurance_providers = ['Blue Cross', 'Aetna', 'Cigna', 'United Healthcare', 'Kaiser', 'Humana', 'Anthem', 'Medicare', 'Medicaid']
    
    occupations = [
        'Teacher', 'Engineer', 'Nurse', 'Manager', 'Sales Representative', 'Accountant', 'Lawyer', 'Doctor',
        'Consultant', 'Designer', 'Developer', 'Analyst', 'Technician', 'Administrator', 'Coordinator',
        'Specialist', 'Director', 'Supervisor', 'Assistant', 'Executive', 'Clerk', 'Officer', 'Operator',
        'Mechanic', 'Electrician', 'Plumber', 'Chef', 'Driver', 'Security Guard', 'Cashier'
    ]
    
    marital_statuses = ['single', 'married', 'divorced', 'widowed']
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    
    medical_conditions = [
        'Lower back pain', 'Knee osteoarthritis', 'Shoulder impingement', 'Neck strain', 'Tennis elbow',
        'Plantar fasciitis', 'Rotator cuff injury', 'Sciatica', 'Carpal tunnel syndrome', 'Hip bursitis',
        'Ankle sprain', 'Muscle strain', 'Joint stiffness', 'Chronic pain', 'Sports injury',
        'Post-surgical rehabilitation', 'Balance issues', 'Mobility limitations'
    ]
    
    allergies_list = [
        'Penicillin', 'Latex', 'Shellfish', 'Nuts', 'Dairy', 'Eggs', 'Soy', 'Wheat',
        'Aspirin', 'Ibuprofen', 'Codeine', 'Sulfa drugs', 'Contrast dye', 'Adhesive tape'
    ]
    
    medications_list = [
        'Ibuprofen 400mg', 'Acetaminophen 500mg', 'Naproxen 220mg', 'Aspirin 81mg',
        'Lisinopril 10mg', 'Metformin 500mg', 'Atorvastatin 20mg', 'Omeprazole 20mg',
        'Levothyroxine 50mcg', 'Amlodipine 5mg', 'Metoprolol 25mg', 'Losartan 50mg'
    ]
    
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
    
    created_patients = []
    for i in range(80):  # Create 80 patients
        # Generate patient ID
        patient_id = f"P{str(i+1).zfill(6)}"
        
        # Generate random patient data
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        gender = random.choice(['male', 'female'])
        
        # Generate age between 18-80
        age = random.randint(18, 80)
        birth_date = date.today() - timedelta(days=age*365 + random.randint(0, 365))
        
        # Generate contact info
        phone = f"555-{random.randint(1000, 9999)}"
        email = f"{first_name.lower()}.{last_name.lower()}@email.com"
        
        # Generate address
        city_index = random.randint(0, len(cities)-1)
        city = cities[city_index]
        state = states[city_index]
        address = f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Cedar', 'Maple'])} {random.choice(['St', 'Ave', 'Dr', 'Ln', 'Blvd'])}"
        zip_code = f"{random.randint(10000, 99999)}"
        
        # Generate other details
        occupation = random.choice(occupations)
        marital_status = random.choice(marital_statuses)
        blood_type = random.choice(blood_types)
        insurance_provider = random.choice(insurance_providers)
        insurance_policy = f"{insurance_provider[:3].upper()}{random.randint(100000, 999999)}"
        
        # Generate medical info
        medical_history = random.sample(medical_conditions, random.randint(1, 3))
        allergies = random.sample(allergies_list, random.randint(0, 2)) if random.random() > 0.3 else []
        current_medications = random.sample(medications_list, random.randint(0, 3)) if random.random() > 0.4 else []
        
        # Generate emergency contact
        emergency_contact_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        emergency_contact_phone = f"555-{random.randint(1000, 9999)}"
        emergency_contact_relationship = random.choice(['Spouse', 'Parent', 'Child', 'Sibling', 'Friend'])
        
        patient, created = Patient.objects.get_or_create(
            patient_id=patient_id,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'date_of_birth': birth_date,
                'gender': 'M' if gender == 'male' else 'F',
                'phone': phone,
                'email': email,
                'address_line1': address,
                'city': city,
                'state': state,
                'postal_code': zip_code,
                'insurance_provider': insurance_provider,
                'insurance_policy_number': insurance_policy,
                'insurance_group_number': f"GRP{random.randint(1000, 9999)}",
                'emergency_contact_name': emergency_contact_name,
                'emergency_contact_phone': emergency_contact_phone,
                'emergency_contact_relationship': emergency_contact_relationship,
                'blood_type': blood_type,
                'medical_history': ', '.join(medical_history),
                'allergies': ', '.join(allergies) if allergies else '',
                'current_medications': ', '.join(current_medications) if current_medications else '',
                'is_active': True
            }
        )
        created_patients.append(patient)
        if created:
            print(f"Created patient: {patient.get_full_name()}")
    
    return created_patients

def create_appointments_and_invoices(patients, services):
    """Create appointments and corresponding invoices"""
    # Get or create providers
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.create_superuser('admin', 'admin@clinic.com', 'admin123')
    
    # Create additional provider users to avoid scheduling conflicts
    providers = [admin_user]
    provider_names = [
        ('Dr. Sarah Wilson', 'doctor'),
        ('Dr. Michael Chen', 'doctor'), 
        ('Lisa Rodriguez', 'nutritionist'),
        ('James Thompson', 'doctor')
    ]
    
    for name, role in provider_names:
        first_name, last_name = name.split(' ', 1)
        username = f"{first_name.lower()}.{last_name.lower().replace(' ', '')}"
        provider, created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'email': f"{username}@clinic.com",
                'role': role,
                'is_staff': True,
                'password': make_password('password123')
            }
        )
        providers.append(provider)
    
    # Create appointments from 2020 to 2024 for historical data
    start_date = date(2020, 1, 1)
    end_date = date(2024, 12, 31)
    
    appointments = []
    invoices = []
    
    for patient in patients:
        # Each patient gets 3-8 appointments for more realistic data
        num_appointments = random.randint(3, 8)
        
        for _ in range(num_appointments):
            # Random appointment date from 2020-2024
            days_range = (end_date - start_date).days
            appointment_date = start_date + timedelta(days=random.randint(0, days_range))
            appointment_time = datetime.min.time().replace(
                hour=random.randint(8, 17), 
                minute=random.choice([0, 15, 30, 45])
            )
            
            service = random.choice(services)
            provider = random.choice(providers)
            status = random.choices(
                ['scheduled', 'completed', 'cancelled', 'no_show'],
                weights=[10, 70, 15, 5]
            )[0]
            
            try:
                appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    provider=provider,
                    appointment_date=appointment_date,
                    appointment_time=appointment_time,
                    duration_minutes=service.duration_minutes,
                    status=status,
                    notes=f"Appointment for {service.name}",
                    created_by=admin_user
                )
                appointments.append(appointment)
            except Exception as e:
                # Skip this appointment if there's a conflict
                continue
            
            # Create invoice for completed appointments
            if status == 'completed':
                # Generate invoice number
                invoice_count = Invoice.objects.count()
                invoice_number = f"INV-{str(invoice_count + 1).zfill(6)}"
                
                # Random due date (7-30 days from appointment)
                due_date = appointment_date + timedelta(days=random.randint(7, 30))
                
                invoice = Invoice.objects.create(
                    invoice_number=invoice_number,
                    patient=patient,
                    due_date=due_date,
                    status=random.choices(
                        ['draft', 'sent', 'paid', 'overdue'],
                        weights=[5, 25, 50, 20]
                    )[0],
                    tax_rate=Decimal('8.25'),  # 8.25% tax
                    discount_amount=Decimal('0.00'),
                    created_by=admin_user
                )
                
                # Create line item
                InvoiceLineItem.objects.create(
                    invoice=invoice,
                    service=service,
                    appointment=appointment,
                    description=service.name,
                    quantity=1,
                    unit_price=Decimal(str(service.base_price))
                )
                
                # Calculate totals
                invoice.calculate_totals()
                invoices.append(invoice)
    
    print(f"Created {len(appointments)} appointments and {len(invoices)} invoices")
    return appointments, invoices

def create_payments(invoices):
    """Create payment records for invoices"""
    admin_user = User.objects.filter(is_superuser=True).first()
    payments = []
    
    for invoice in invoices:
        # 80% of sent/paid invoices get payments
        if invoice.status in ['sent', 'paid'] and random.random() < 0.8:
            # Generate payment ID
            payment_count = Payment.objects.count()
            payment_id = f"PAY-{str(payment_count + 1).zfill(6)}"
            
            # Payment amount (usually full amount, sometimes partial)
            if random.random() < 0.9:  # 90% full payments
                amount = invoice.total_amount
            else:  # 10% partial payments
                amount = invoice.total_amount * Decimal(str(random.uniform(0.3, 0.8)))
            
            # Payment date (can vary across all years from 2020-2024)
            days_after_invoice = random.randint(1, 180)
            payment_date = invoice.issue_date + timedelta(days=days_after_invoice)
            # Ensure payment date doesn't exceed 2024
            if payment_date > date(2024, 12, 31):
                payment_date = date(2024, 12, 31)
            
            payment = Payment.objects.create(
                payment_id=payment_id,
                invoice=invoice,
                patient=invoice.patient,
                amount=amount,
                payment_method=random.choice(['cash', 'credit_card', 'debit_card', 'check', 'bank_transfer', 'insurance']),
                payment_date=payment_date,
                status=random.choices(['pending', 'completed', 'failed'], weights=[10, 85, 5])[0],
                reference_number=f"REF{random.randint(100000, 999999)}",
                notes=f"Payment for invoice {invoice.invoice_number}",
                processed_by=admin_user
            )
            payments.append(payment)
            
            # Update invoice status if fully paid
            if payment.status == 'completed' and amount >= invoice.total_amount:
                invoice.status = 'paid'
                invoice.save()
    
    print(f"Created {len(payments)} payments")
    return payments

def create_insurance_claims(invoices):
    """Create insurance claims for some invoices"""
    admin_user = User.objects.filter(is_superuser=True).first()
    claims = []
    
    # Create claims for 40% of invoices
    claim_invoices = random.sample(invoices, int(len(invoices) * 0.4))
    
    for invoice in claim_invoices:
        claim_count = InsuranceClaim.objects.count()
        claim_number = f"CLM-{str(claim_count + 1).zfill(6)}"
        
        # Submission date (after invoice date, but within 2024)
        days_after_invoice = random.randint(1, 30)
        submission_date = invoice.issue_date + timedelta(days=days_after_invoice)
        # Ensure submission date doesn't exceed 2024
        if submission_date > date(2024, 12, 31):
            submission_date = date(2024, 12, 31)
        
        claim = InsuranceClaim.objects.create(
            claim_number=claim_number,
            patient=invoice.patient,
            invoice=invoice,
            insurance_provider=invoice.patient.insurance_provider,
            policy_number=invoice.patient.insurance_policy_number,
            group_number=invoice.patient.insurance_group_number,
            claim_amount=invoice.total_amount,
            approved_amount=invoice.total_amount * Decimal(str(random.uniform(0.7, 1.0))),
            status=random.choice(['submitted', 'pending', 'approved', 'denied', 'paid']),
            submission_date=submission_date,
            notes=f"Insurance claim for invoice {invoice.invoice_number}",
            submitted_by=admin_user
        )
        claims.append(claim)
    
    print(f"Created {len(claims)} insurance claims")
    return claims

def create_vital_signs(patients):
    """Create vital signs records for patients"""
    admin_user = User.objects.filter(is_superuser=True).first()
    vital_signs = []
    
    for patient in patients:
        # Each patient gets 2-5 vital signs records over time
        num_vitals = random.randint(2, 5)
        
        for _ in range(num_vitals):
            # Random date from 2020-2024
            vital_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 1825))
            
            # Generate realistic vital signs based on age and gender
            age = patient.get_age()
            
            # Height (relatively stable, slight variations)
            if patient.gender == 'M':
                height = random.uniform(165, 185)
            else:
                height = random.uniform(155, 175)
            
            # Weight (can vary more)
            if patient.gender == 'M':
                weight = random.uniform(60, 100)
            else:
                weight = random.uniform(50, 85)
            
            # Blood pressure (varies with age)
            if age < 40:
                systolic = random.randint(110, 130)
                diastolic = random.randint(70, 85)
            elif age < 60:
                systolic = random.randint(120, 140)
                diastolic = random.randint(75, 90)
            else:
                systolic = random.randint(130, 150)
                diastolic = random.randint(80, 95)
            
            vital = VitalSigns.objects.create(
                patient=patient,
                recorded_by=admin_user,
                height=round(height, 1),
                weight=round(weight, 1),
                blood_pressure_systolic=systolic,
                blood_pressure_diastolic=diastolic,
                heart_rate=random.randint(60, 100),
                temperature=round(random.uniform(36.0, 37.5), 1),
                respiratory_rate=random.randint(12, 20),
                oxygen_saturation=random.randint(95, 100),
                notes=random.choice(['Normal vitals', 'Patient feeling well', 'Routine check', ''])
            )
            vital.recorded_date = datetime.combine(vital_date, datetime.min.time())
            vital.save()
            vital_signs.append(vital)
    
    print(f"Created {len(vital_signs)} vital signs records")
    return vital_signs

def create_triage_records(patients):
    """Create triage records for patients"""
    admin_user = User.objects.filter(is_superuser=True).first()
    triages = []
    
    complaints = [
        'Lower back pain', 'Knee pain', 'Shoulder pain', 'Neck stiffness',
        'Hip discomfort', 'Ankle sprain', 'Muscle strain', 'Joint stiffness',
        'Chronic pain', 'Post-injury rehabilitation', 'Balance issues',
        'Mobility problems', 'Sports injury', 'Arthritis pain'
    ]
    
    symptoms = [
        'Pain and stiffness', 'Limited range of motion', 'Swelling and inflammation',
        'Muscle weakness', 'Numbness and tingling', 'Sharp shooting pain',
        'Dull aching pain', 'Morning stiffness', 'Pain with movement'
    ]
    
    for patient in patients:
        # 60% of patients have triage records
        if random.random() < 0.6:
            num_triages = random.randint(1, 3)
            
            for _ in range(num_triages):
                triage_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 1825))
                
                triage = Triage.objects.create(
                    patient=patient,
                    triaged_by=admin_user,
                    assigned_department=random.choice(['physiotherapy', 'nutrition', 'general']),
                    chief_complaint=random.choice(complaints),
                    pain_scale=random.randint(3, 8),
                    priority_level=random.choices(['1', '2', '3', '4', '5'], weights=[5, 15, 40, 30, 10])[0],
                    symptoms=random.choice(symptoms),
                    onset=random.choice(['Gradual onset over weeks', 'Sudden onset yesterday', 'Started 3 days ago', 'Chronic condition']),
                    duration=random.choice(['2-3 weeks', '1 month', '6 months', '1 year', 'Several years']),
                    notes=f"Patient presents with {random.choice(complaints).lower()}"
                )
                triage.triage_date = datetime.combine(triage_date, datetime.min.time())
                triage.save()
                triages.append(triage)
    
    print(f"Created {len(triages)} triage records")
    return triages

def create_assessments(patients, triages):
    """Create assessment records for patients"""
    admin_user = User.objects.filter(is_superuser=True).first()
    assessments = []
    
    diagnoses = [
        'Mechanical lower back pain', 'Osteoarthritis of knee', 'Rotator cuff impingement',
        'Cervical strain', 'Lumbar disc herniation', 'Patellofemoral pain syndrome',
        'Lateral epicondylitis', 'Plantar fasciitis', 'Chronic pain syndrome',
        'Post-traumatic stiffness', 'Muscle imbalance', 'Joint dysfunction'
    ]
    
    treatments = [
        'Manual therapy and exercise program', 'Strengthening and mobility exercises',
        'Pain management and rehabilitation', 'Postural correction program',
        'Sports-specific rehabilitation', 'Ergonomic assessment and training',
        'Balance and coordination training', 'Functional movement training'
    ]
    
    for patient in patients:
        # 70% of patients have assessments
        if random.random() < 0.7:
            num_assessments = random.randint(1, 4)
            
            for i in range(num_assessments):
                assessment_date = date(2020, 1, 1) + timedelta(days=random.randint(0, 1825))
                
                # Link to triage if available
                related_triage = None
                if triages and random.random() < 0.4:
                    patient_triages = [t for t in triages if t.patient == patient]
                    if patient_triages:
                        related_triage = random.choice(patient_triages)
                
                assessment = Assessment.objects.create(
                    patient=patient,
                    assessed_by=admin_user,
                    assessment_type='first_visit' if i == 0 else 'follow_up',
                    department=random.choice(['physiotherapy', 'nutrition', 'general']),
                    related_triage=related_triage,
                    chief_complaint=related_triage.chief_complaint if related_triage else random.choice(['Lower back pain', 'Knee pain', 'Shoulder pain']),
                    history_of_present_illness=f"Patient reports {random.choice(['gradual onset', 'sudden onset'])} of symptoms over {random.choice(['days', 'weeks', 'months'])}",
                    physical_examination=f"Examination reveals {random.choice(['limited ROM', 'muscle weakness', 'joint stiffness', 'inflammation'])}",
                    mobility_status=random.choice(['Independent', 'Assisted', 'Limited mobility']),
                    mental_status=random.choice(['Alert and oriented', 'Cooperative', 'Anxious about condition']),
                    diagnosis=random.choice(diagnoses),
                    treatment_plan=random.choice(treatments),
                    follow_up_required=random.choice([True, False]),
                    follow_up_date=assessment_date + timedelta(days=random.randint(7, 30)) if random.choice([True, False]) else None,
                    follow_up_instructions=random.choice(['Continue exercises', 'Return in 2 weeks', 'Home exercise program', '']),
                    notes=f"Assessment completed for {patient.get_full_name()}"
                )
                assessment.assessment_date = datetime.combine(assessment_date, datetime.min.time())
                assessment.save()
                assessments.append(assessment)
    
    print(f"Created {len(assessments)} assessment records")
    return assessments

def main():
    """Main function to populate all sample data"""
    print("Starting sample data population...")
    
    # Create services
    print("\n1. Creating services...")
    services = create_services()
    
    # Create patients
    print("\n2. Creating patients...")
    patients = create_patients()
    
    # Create appointments and invoices
    print("\n3. Creating appointments and invoices...")
    appointments, invoices = create_appointments_and_invoices(patients, services)
    
    # Create payments
    print("\n4. Creating payments...")
    payments = create_payments(invoices)
    
    # Create insurance claims
    print("\n5. Creating insurance claims...")
    claims = create_insurance_claims(invoices)
    
    # Create vital signs
    print("\n6. Creating vital signs records...")
    vital_signs = create_vital_signs(patients)
    
    # Create triage records
    print("\n7. Creating triage records...")
    triages = create_triage_records(patients)
    
    # Create assessments
    print("\n8. Creating assessment records...")
    assessments = create_assessments(patients, triages)
    
    print(f"\nSample data population completed!")
    print(f"Summary:")
    print(f"- Services: {len(services)}")
    print(f"- Patients: {len(patients)}")
    print(f"- Appointments: {len(appointments)}")
    print(f"- Invoices: {len(invoices)}")
    print(f"- Payments: {len(payments)}")
    print(f"- Insurance Claims: {len(claims)}")
    print(f"- Vital Signs: {len(vital_signs)}")
    print(f"- Triage Records: {len(triages)}")
    print(f"- Assessments: {len(assessments)}")

if __name__ == "__main__":
    main()
