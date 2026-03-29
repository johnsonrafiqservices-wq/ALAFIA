from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from datetime import date

from patients.models import Patient, BirthdayWish
from clinic_settings.models import ClinicSettings


class Command(BaseCommand):
    help = 'Send birthday wish emails to patients whose birthday is today'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview which patients would receive wishes without actually sending',
        )
        parser.add_argument(
            '--date',
            type=str,
            default=None,
            help='Override today\'s date (YYYY-MM-DD) for testing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if options['date']:
            try:
                today = date.fromisoformat(options['date'])
            except ValueError:
                self.stderr.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD'))
                return
        else:
            today = date.today()

        self.stdout.write(f"Checking birthdays for: {today.strftime('%B %d, %Y')}")

        # Get clinic settings for branding
        try:
            clinic_settings = ClinicSettings.objects.first()
        except Exception:
            clinic_settings = None

        clinic_name = getattr(clinic_settings, 'clinic_name', None) or \
                      getattr(settings, 'CLINIC_NAME', 'Alafia Point Wellness Clinic')

        # Find patients with today's birthday who have an email
        birthday_patients = Patient.objects.filter(
            date_of_birth__month=today.month,
            date_of_birth__day=today.day,
            is_active=True,
            email__isnull=False,
        ).exclude(email='')

        if not birthday_patients.exists():
            self.stdout.write(self.style.WARNING('No patients with birthdays today.'))
            return

        self.stdout.write(f"Found {birthday_patients.count()} patient(s) with birthdays today.")

        sent = 0
        skipped = 0
        failed = 0

        for patient in birthday_patients:
            # Skip if already sent this year
            already_sent = BirthdayWish.objects.filter(
                patient=patient,
                year=today.year,
                success=True,
            ).exists()

            if already_sent:
                self.stdout.write(
                    self.style.WARNING(f'  SKIP  {patient.get_full_name()} — already sent in {today.year}')
                )
                skipped += 1
                continue

            age = today.year - patient.date_of_birth.year
            context = {
                'patient': patient,
                'clinic_name': clinic_name,
                'clinic_settings': clinic_settings,
                'age': age,
                'today': today,
            }

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f'  DRY-RUN  Would send to {patient.get_full_name()} <{patient.email}> (turns {age})')
                )
                sent += 1
                continue

            try:
                subject = f"Happy Birthday from {clinic_name}! 🎂"
                text_body = (
                    f"Dear {patient.first_name},\n\n"
                    f"Wishing you a very Happy {age}{'st' if age == 1 else 'nd' if age == 2 else 'rd' if age == 3 else 'th'} Birthday!\n\n"
                    f"From all of us at {clinic_name}, we hope your special day is filled with joy and good health.\n\n"
                    f"Best wishes,\n{clinic_name}"
                )
                html_body = render_to_string(
                    'patients/email/birthday_wishes.html',
                    context,
                )

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[patient.email],
                )
                email.attach_alternative(html_body, 'text/html')
                email.send()

                BirthdayWish.objects.update_or_create(
                    patient=patient,
                    year=today.year,
                    defaults={'success': True, 'error_message': ''},
                )
                sent += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  SENT   {patient.get_full_name()} <{patient.email}>')
                )

            except Exception as exc:
                BirthdayWish.objects.update_or_create(
                    patient=patient,
                    year=today.year,
                    defaults={'success': False, 'error_message': str(exc)},
                )
                failed += 1
                self.stderr.write(
                    self.style.ERROR(f'  FAILED {patient.get_full_name()} <{patient.email}>: {exc}')
                )

        self.stdout.write('')
        self.stdout.write(f'Done — Sent: {sent}  Skipped: {skipped}  Failed: {failed}')
