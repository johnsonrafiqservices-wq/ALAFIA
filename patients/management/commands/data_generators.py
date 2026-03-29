"""Data generators for sample data creation"""

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta, time
from decimal import Decimal
import random

User = get_user_model()

# Sample data constants
FIRST_NAMES = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Jennifer',
    'William', 'Mary', 'James', 'Patricia', 'Richard', 'Linda', 'Joseph', 'Barbara',
    'Thomas', 'Elizabeth', 'Charles', 'Susan', 'Christopher', 'Jessica', 'Daniel', 'Nancy']

LAST_NAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor']

UGANDAN_CITIES = ['Kampala', 'Entebbe', 'Mbarara', 'Gulu', 'Jinja', 'Fort Portal',
    'Masaka', 'Mbale', 'Kabale', 'Arua', 'Hoima', 'Soroti']

MEDICAL_CONDITIONS = ['Hypertension', 'Diabetes Type 2', 'Asthma', 'Arthritis',
    'Back Pain', 'Sports Injury', 'Obesity', 'Malnutrition']

CHIEF_COMPLAINTS = ['Lower back pain', 'Knee pain', 'Shoulder stiffness',
    'Weight management', 'Post-surgery rehab', 'Chronic neck pain', 'Dietary counseling']

class DataGenerator:
    def __init__(self, stdout, style):
        self.stdout = stdout
        self.style = style
        self.stats = {}
    
    def clear_existing_data(self):
        """Clear all sample data"""
        self.stdout.write(self.style.WARNING('\nClearing existing data...'))
        
        from patients.models import Patient, VitalSigns, Triage, Assessment
        from appointments.models import Appointment, Service, TreatmentSession, NutritionConsultation
        from billing.models import Invoice, InvoiceLineItem, Payment, InsuranceClaim
        from laboratory.models import LabTest, LabTestRequest, LabTestResult
        from pharmacy.models import Medication, Category, Supplier, Batch, Prescription, PrescriptionItem
        
        Payment.objects.all().delete()
        InsuranceClaim.objects.all().delete()
        InvoiceLineItem.objects.all().delete()
        Invoice.objects.all().delete()
        TreatmentSession.objects.all().delete()
        NutritionConsultation.objects.all().delete()
        Appointment.objects.all().delete()
        LabTestResult.objects.all().delete()
        LabTestRequest.objects.all().delete()
        LabTest.objects.all().delete()
        PrescriptionItem.objects.all().delete()
        Prescription.objects.all().delete()
        Batch.objects.all().delete()
        Medication.objects.all().delete()
        Category.objects.all().delete()
        Supplier.objects.all().delete()
        Assessment.objects.all().delete()
        Triage.objects.all().delete()
        VitalSigns.objects.all().delete()
        Patient.objects.all().delete()
        Service.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(self.style.SUCCESS('✓ Data cleared'))
    
    def generate_all_data(self, num_users, num_patients):
        """Generate all sample data"""
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('PhysioNutritionClinic Sample Data Generator'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        users = self.generate_users(num_users)
        services = self.generate_services()
        patients = self.generate_patients(num_patients, users)
        self.generate_vital_signs(patients, users)
        self.generate_triages(patients, users)
        self.generate_assessments(patients, users)
        appointments = self.generate_appointments(patients, users, services)
        self.generate_treatment_sessions(appointments)
        self.generate_nutrition_consultations(appointments)
        lab_tests = self.generate_lab_tests()
        self.generate_lab_requests(patients, lab_tests, users)
        suppliers, categories = self.generate_pharmacy_basics()
        medications = self.generate_medications(categories)
        self.generate_batches(medications, suppliers, users)
        self.generate_prescriptions(patients, medications, users)
        invoices = self.generate_invoices(patients, services, users)
        self.generate_payments(invoices, patients, users)
        self.generate_insurance_claims(patients, invoices, users)
    
    def generate_users(self, count):
        """Generate staff users"""
        self.stdout.write('\n1. Generating users...')
        users = []
        roles = ['admin', 'doctor', 'nutritionist', 'receptionist', 'nurse', 'billing']
        
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin', email='admin@clinic.com', password='admin123',
                first_name='System', last_name='Administrator', role='admin'
            )
            users.append(admin)
        
        for i in range(count):
            role = roles[i % len(roles)]
            username = f"{role}{i+1}"
            if User.objects.filter(username=username).exists():
                continue
            user = User.objects.create_user(
                username=username, email=f"{username}@clinic.com", password='password123',
                first_name=random.choice(FIRST_NAMES), last_name=random.choice(LAST_NAMES),
                role=role, phone=f"+256{random.randint(700000000, 799999999)}",
                employee_id=f"EMP{str(i+1).zfill(4)}", is_active_employee=True
            )
            users.append(user)
        
        self.stats['users'] = len(users)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(users)} users'))
        return users
    
    def generate_services(self):
        """Generate clinic services"""
        self.stdout.write('\n2. Generating services...')
        from appointments.models import Service
        
        services_data = [
            ('Initial Physiotherapy Assessment', 'physiotherapy', 60, 80000),
            ('Physiotherapy Treatment Session', 'physiotherapy', 45, 60000),
            ('Nutrition Consultation', 'nutrition', 45, 65000),
            ('Dietary Planning', 'nutrition', 30, 45000),
            ('General Consultation', 'consultation', 30, 50000),
            ('Follow-up Consultation', 'consultation', 20, 35000),
        ]
        
        services = []
        for name, category, duration, price in services_data:
            service, _ = Service.objects.get_or_create(
                name=name, defaults={
                    'category': category, 'duration_minutes': duration,
                    'base_price': Decimal(price), 'is_active': True
                }
            )
            services.append(service)
        
        self.stats['services'] = len(services)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(services)} services'))
        return services
    
    def generate_patients(self, count, users):
        """Generate patients"""
        self.stdout.write(f'\n3. Generating {count} patients...')
        from patients.models import Patient
        
        patients = []
        receptionist = next((u for u in users if u.role == 'receptionist'), users[0])
        
        for i in range(count):
            is_visiting = i % 10 == 0
            patient_id = f"PT-{str(i+1).zfill(6)}" if not is_visiting else f"VP-{str(i+1).zfill(6)}"
            
            patient = Patient.objects.create(
                patient_id=patient_id, is_visiting_patient=is_visiting,
                first_name=random.choice(FIRST_NAMES), last_name=random.choice(LAST_NAMES),
                date_of_birth=date.today() - timedelta(days=random.randint(6570, 25550)),
                gender=random.choice(['M', 'F']),
                phone=f"+256{random.randint(700000000, 799999999)}",
                email=f"patient{i+1}@email.com" if not is_visiting else '',
                city=random.choice(UGANDAN_CITIES), country='Uganda',
                emergency_contact_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                emergency_contact_phone=f"+256{random.randint(700000000, 799999999)}",
                blood_type=random.choice(['A+', 'B+', 'O+', 'AB+']),
                allergies=random.choice(['None', 'Penicillin', 'Sulfa drugs']),
                registered_by=receptionist, is_active=True
            )
            patients.append(patient)
        
        self.stats['patients'] = len(patients)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(patients)} patients'))
        return patients
    
    def generate_vital_signs(self, patients, users):
        """Generate vital signs"""
        self.stdout.write('\n4. Generating vital signs...')
        from patients.models import VitalSigns
        
        nurse = next((u for u in users if u.role == 'nurse'), users[0])
        vitals = []
        
        for patient in patients[:len(patients)//2]:
            vital = VitalSigns.objects.create(
                patient=patient, recorded_by=nurse,
                height=Decimal(random.randint(150, 190)),
                weight=Decimal(random.randint(50, 120)),
                blood_pressure_systolic=random.randint(110, 140),
                blood_pressure_diastolic=random.randint(70, 90),
                heart_rate=random.randint(60, 100),
                temperature=Decimal(random.randint(360, 385) / 10),
                respiratory_rate=random.randint(12, 20),
                oxygen_saturation=random.randint(95, 100)
            )
            vitals.append(vital)
        
        self.stats['vital_signs'] = len(vitals)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(vitals)} vital signs'))
        return vitals
    
    def generate_triages(self, patients, users):
        """Generate triages"""
        self.stdout.write('\n5. Generating triages...')
        from patients.models import Triage
        
        nurse = next((u for u in users if u.role == 'nurse'), users[0])
        triages = []
        
        for patient in patients[:len(patients)//3]:
            triage = Triage.objects.create(
                patient=patient, triaged_by=nurse,
                assigned_department=random.choice(['physiotherapy', 'nutrition', 'general']),
                chief_complaint=random.choice(CHIEF_COMPLAINTS),
                pain_scale=random.randint(0, 10),
                priority_level=random.choice(['2', '3', '4']),
                symptoms=f"Patient reports {random.choice(CHIEF_COMPLAINTS)}",
                onset='2 days ago', duration='2 days'
            )
            triages.append(triage)
        
        self.stats['triages'] = len(triages)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(triages)} triages'))
        return triages
    
    def generate_assessments(self, patients, users):
        """Generate assessments"""
        self.stdout.write('\n6. Generating assessments...')
        from patients.models import Assessment
        
        doctors = [u for u in users if u.role in ['doctor', 'nutritionist']] or users
        assessments = []
        
        for patient in patients[:len(patients)//2]:
            assessment = Assessment.objects.create(
                patient=patient, assessed_by=random.choice(doctors),
                assessment_type=random.choice(['first_visit', 'follow_up']),
                department=random.choice(['physiotherapy', 'nutrition', 'general']),
                chief_complaint=random.choice(CHIEF_COMPLAINTS),
                history_of_present_illness=f"Patient presents with {random.choice(CHIEF_COMPLAINTS)}",
                physical_examination="Physical exam findings documented",
                diagnosis=random.choice(MEDICAL_CONDITIONS),
                treatment_plan="Treatment plan established"
            )
            assessments.append(assessment)
        
        self.stats['assessments'] = len(assessments)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(assessments)} assessments'))
        return assessments
    
    def generate_appointments(self, patients, users, services):
        """Generate appointments"""
        self.stdout.write('\n7. Generating appointments...')
        from appointments.models import Appointment
        
        doctors = [u for u in users if u.role in ['doctor', 'nutritionist']] or users[:3]
        receptionist = next((u for u in users if u.role == 'receptionist'), users[0])
        appointments = []
        
        for patient in patients:
            for j in range(random.randint(1, 2)):
                days_offset = random.randint(-30, 14)
                appointment_date = date.today() + timedelta(days=days_offset)
                appointment_time = time(hour=random.randint(8, 16), minute=0)
                
                status = 'completed' if days_offset < 0 else random.choice(['scheduled', 'confirmed'])
                
                try:
                    appointment = Appointment.objects.create(
                        patient=patient, service=random.choice(services),
                        provider=random.choice(doctors),
                        appointment_date=appointment_date, appointment_time=appointment_time,
                        duration_minutes=45, status=status,
                        created_by=receptionist
                    )
                    appointments.append(appointment)
                except:
                    continue
        
        self.stats['appointments'] = len(appointments)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(appointments)} appointments'))
        return appointments
    
    def generate_treatment_sessions(self, appointments):
        """Generate treatment sessions"""
        self.stdout.write('\n8. Generating treatment sessions...')
        from appointments.models import TreatmentSession
        
        physio_appts = [a for a in appointments if 'physio' in a.service.name.lower() and a.status == 'completed']
        sessions = []
        
        for appt in physio_appts[:len(physio_appts)//2]:
            session = TreatmentSession.objects.create(
                appointment=appt, chief_complaint=random.choice(CHIEF_COMPLAINTS),
                assessment_findings="Good progress noted",
                treatment_provided="Manual therapy and exercises",
                patient_response="Positive response",
                pain_level_before=random.randint(5, 8),
                pain_level_after=random.randint(2, 4),
                session_completed=True, completed_at=timezone.now()
            )
            sessions.append(session)
        
        self.stats['treatment_sessions'] = len(sessions)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(sessions)} treatment sessions'))
        return sessions
    
    def generate_nutrition_consultations(self, appointments):
        """Generate nutrition consultations"""
        self.stdout.write('\n9. Generating nutrition consultations...')
        from appointments.models import NutritionConsultation
        
        nutrition_appts = [a for a in appointments if 'nutrition' in a.service.name.lower() and a.status == 'completed']
        consultations = []
        
        for appt in nutrition_appts[:len(nutrition_appts)//2]:
            consult = NutritionConsultation.objects.create(
                appointment=appt,
                current_diet="Typical balanced diet",
                dietary_restrictions=random.choice(['None', 'Vegetarian']),
                health_goals=random.choice(['Weight loss', 'Better energy']),
                current_weight=Decimal(random.randint(60, 100)),
                target_weight=Decimal(random.randint(60, 90)),
                meal_plan="Balanced meal plan provided",
                consultation_completed=True, completed_at=timezone.now()
            )
            consultations.append(consult)
        
        self.stats['nutrition_consultations'] = len(consultations)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(consultations)} consultations'))
        return consultations
    
    def generate_lab_tests(self):
        """Generate lab tests"""
        self.stdout.write('\n10. Generating lab tests...')
        from laboratory.models import LabTest
        
        tests_data = [
            ('CBC', 'Complete Blood Count', 50000),
            ('FBS', 'Fasting Blood Sugar', 25000),
            ('LIPID', 'Lipid Profile', 75000),
            ('LFT', 'Liver Function Test', 80000),
        ]
        
        tests = []
        for code, name, price in tests_data:
            test, _ = LabTest.objects.get_or_create(
                code=code, defaults={'name': name, 'price': Decimal(price), 'currency': 'UGX'}
            )
            tests.append(test)
        
        self.stats['lab_tests'] = len(tests)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(tests)} lab test types'))
        return tests
    
    def generate_lab_requests(self, patients, lab_tests, users):
        """Generate lab requests"""
        self.stdout.write('\n11. Generating lab requests...')
        from laboratory.models import LabTestRequest, LabTestResult
        
        doctors = [u for u in users if u.role == 'doctor'] or users
        requests = []
        
        for patient in patients[:len(patients)//3]:
            for test in random.sample(lab_tests, min(2, len(lab_tests))):
                request = LabTestRequest.objects.create(
                    patient=patient, test=test,
                    requested_by=random.choice(doctors).get_full_name(),
                    status='completed'
                )
                requests.append(request)
                LabTestResult.objects.create(
                    request=request,
                    result=f"{test.name}: Normal range",
                    reported_by='Lab Tech'
                )
        
        self.stats['lab_requests'] = len(requests)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(requests)} lab requests'))
        return requests
    
    def generate_pharmacy_basics(self):
        """Generate suppliers and categories"""
        self.stdout.write('\n12. Generating pharmacy basics...')
        from pharmacy.models import Supplier, Category
        
        suppliers = []
        for i in range(3):
            supplier, _ = Supplier.objects.get_or_create(
                name=f'Supplier {i+1}',
                defaults={'contact_person': 'Contact', 'email': f'supplier{i+1}@email.com',
                         'phone': '+256700000000', 'address': 'Kampala'}
            )
            suppliers.append(supplier)
        
        categories = []
        for cat in ['Analgesics', 'Antibiotics', 'Vitamins']:
            category, _ = Category.objects.get_or_create(name=cat)
            categories.append(category)
        
        self.stats['suppliers'] = len(suppliers)
        self.stats['categories'] = len(categories)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(suppliers)} suppliers, {len(categories)} categories'))
        return suppliers, categories
    
    def generate_medications(self, categories):
        """Generate medications"""
        self.stdout.write('\n13. Generating medications...')
        from pharmacy.models import Medication
        
        meds_data = [
            ('Paracetamol', 'Acetaminophen', '500mg', 'tablet', 1000),
            ('Ibuprofen', 'Ibuprofen', '400mg', 'tablet', 2000),
            ('Amoxicillin', 'Amoxicillin', '500mg', 'capsule', 3000),
            ('Metformin', 'Metformin', '500mg', 'tablet', 2500),
        ]
        
        medications = []
        for name, generic, strength, form, price in meds_data:
            med, _ = Medication.objects.get_or_create(
                name=name, strength=strength,
                defaults={'generic_name': generic, 'category': random.choice(categories),
                         'form': form, 'unit_price': Decimal(price),
                         'unit_of_measure': 'tablets', 'manufacturer': 'Pharma Co'}
            )
            medications.append(med)
        
        self.stats['medications'] = len(medications)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(medications)} medications'))
        return medications
    
    def generate_batches(self, medications, suppliers, users):
        """Generate medication batches"""
        self.stdout.write('\n14. Generating batches...')
        from pharmacy.models import Batch
        
        # Get the last batch number to avoid duplicates
        last_batch = Batch.objects.order_by('-id').first()
        start_num = 1
        if last_batch and last_batch.batch_number.startswith('BATCH'):
            try:
                last_num = int(last_batch.batch_number.replace('BATCH', ''))
                start_num = last_num + 1
            except (ValueError, IndexError):
                pass
        
        batches = []
        for i, med in enumerate(medications):
            batch_number = f'BATCH{str(start_num + i).zfill(6)}'
            
            # Skip if batch already exists
            if Batch.objects.filter(batch_number=batch_number).exists():
                continue
            
            batch = Batch.objects.create(
                medication=med, supplier=random.choice(suppliers),
                batch_number=batch_number,
                quantity_remaining=random.randint(100, 1000),
                cost_price=med.unit_price * Decimal('0.7'),
                selling_price=med.unit_price,
                expiry_date=date.today() + timedelta(days=random.randint(365, 730)),
                status='active', received_by=users[0] if users else None
            )
            batches.append(batch)
        
        self.stats['batches'] = len(batches)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(batches)} batches'))
        return batches
    
    def generate_prescriptions(self, patients, medications, users):
        """Generate prescriptions"""
        self.stdout.write('\n15. Generating prescriptions...')
        from pharmacy.models import Prescription, PrescriptionItem
        
        doctors = [u for u in users if u.role == 'doctor'] or users
        prescriptions = []
        
        for patient in patients[:len(patients)//3]:
            prescription = Prescription.objects.create(
                patient=patient, prescribed_by=random.choice(doctors),
                status=random.choice(['pending', 'dispensed'])
            )
            
            for med in random.sample(medications, min(2, len(medications))):
                PrescriptionItem.objects.create(
                    prescription=prescription, medication=med,
                    dosage='1 tablet', frequency='Twice daily',
                    duration='7 days', quantity=14
                )
            
            prescriptions.append(prescription)
        
        self.stats['prescriptions'] = len(prescriptions)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(prescriptions)} prescriptions'))
        return prescriptions
    
    def generate_invoices(self, patients, services, users):
        """Generate invoices"""
        self.stdout.write('\n16. Generating invoices...')
        from billing.models import Invoice, InvoiceLineItem
        
        billing_user = next((u for u in users if u.role == 'billing'), users[0])
        invoices = []
        
        # Get the last invoice number to avoid duplicates
        last_invoice = Invoice.objects.order_by('-id').first()
        start_num = 1
        if last_invoice and last_invoice.invoice_number.startswith('INV-'):
            try:
                last_num = int(last_invoice.invoice_number.split('-')[1])
                start_num = last_num + 1
            except (ValueError, IndexError):
                pass
        
        for i, patient in enumerate(patients[:len(patients)//2]):
            invoice_number = f'INV-{str(start_num + i).zfill(6)}'
            
            # Skip if invoice already exists for this patient
            if Invoice.objects.filter(invoice_number=invoice_number).exists():
                continue
            
            invoice = Invoice.objects.create(
                invoice_number=invoice_number,
                patient=patient,
                due_date=date.today() + timedelta(days=30),
                status=random.choice(['draft', 'sent', 'paid']),
                created_by=billing_user
            )
            
            for service in random.sample(services, min(2, len(services))):
                InvoiceLineItem.objects.create(
                    invoice=invoice, service=service,
                    description=service.name, quantity=1,
                    unit_price=service.base_price,
                    total_amount=service.base_price
                )
            
            invoice.calculate_totals()
            invoices.append(invoice)
        
        self.stats['invoices'] = len(invoices)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(invoices)} invoices'))
        return invoices
    
    def generate_payments(self, invoices, patients, users):
        """Generate payments"""
        self.stdout.write('\n17. Generating payments...')
        from billing.models import Payment
        
        billing_user = next((u for u in users if u.role == 'billing'), users[0])
        payments = []
        
        # Get the last payment number to avoid duplicates
        last_payment = Payment.objects.order_by('-id').first()
        start_num = 1
        if last_payment and last_payment.payment_id.startswith('PAY-'):
            try:
                last_num = int(last_payment.payment_id.split('-')[1])
                start_num = last_num + 1
            except (ValueError, IndexError):
                pass
        
        for i, invoice in enumerate([inv for inv in invoices if inv.status == 'paid']):
            payment_id = f'PAY-{str(start_num + i).zfill(6)}'
            
            # Skip if payment already exists
            if Payment.objects.filter(payment_id=payment_id).exists():
                continue
            
            payment = Payment.objects.create(
                payment_id=payment_id,
                invoice=invoice, patient=invoice.patient,
                amount=invoice.total_amount,
                payment_method=random.choice(['cash', 'credit_card', 'bank_transfer']),
                status='completed', processed_by=billing_user
            )
            payments.append(payment)
        
        self.stats['payments'] = len(payments)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(payments)} payments'))
        return payments
    
    def generate_insurance_claims(self, patients, invoices, users):
        """Generate insurance claims"""
        self.stdout.write('\n18. Generating insurance claims...')
        from billing.models import InsuranceClaim
        
        billing_user = next((u for u in users if u.role == 'billing'), users[0])
        claims = []
        
        # Get the last claim number to avoid duplicates
        last_claim = InsuranceClaim.objects.order_by('-id').first()
        start_num = 1
        if last_claim and last_claim.claim_number.startswith('CLM-'):
            try:
                last_num = int(last_claim.claim_number.split('-')[1])
                start_num = last_num + 1
            except (ValueError, IndexError):
                pass
        
        insured_invoices = [inv for inv in invoices if inv.patient.insurance_provider]
        
        for i, invoice in enumerate(insured_invoices[:5]):
            claim_number = f'CLM-{str(start_num + i).zfill(6)}'
            
            # Skip if claim already exists
            if InsuranceClaim.objects.filter(claim_number=claim_number).exists():
                continue
            
            claim = InsuranceClaim.objects.create(
                claim_number=claim_number,
                patient=invoice.patient, invoice=invoice,
                insurance_provider=invoice.patient.insurance_provider,
                policy_number=invoice.patient.insurance_policy_number or 'POL123456',
                claim_amount=invoice.total_amount,
                status=random.choice(['submitted', 'approved', 'paid']),
                submitted_by=billing_user
            )
            claims.append(claim)
        
        self.stats['insurance_claims'] = len(claims)
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(claims)} insurance claims'))
        return claims
    
    def print_summary(self):
        """Print generation summary"""
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 70))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        for key, value in self.stats.items():
            self.stdout.write(f"  {key.replace('_', ' ').title()}: {value}")
