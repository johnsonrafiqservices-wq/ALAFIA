from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import date

import logging

logger = logging.getLogger(__name__)


@shared_task(name='patients.tasks.send_birthday_wishes')
def send_birthday_wishes(override_date=None):
    """
    Send birthday wish emails to all active patients whose birthday is today.
    Skips patients who already received a wish this calendar year.
    Safe to run multiple times per day.
    """
    from patients.models import Patient, BirthdayWish
    from clinic_settings.models import ClinicSettings

    today = date.fromisoformat(override_date) if override_date else date.today()

    try:
        clinic_settings = ClinicSettings.objects.first()
    except Exception:
        clinic_settings = None

    clinic_name = (
        getattr(clinic_settings, 'clinic_name', None)
        or getattr(settings, 'CLINIC_NAME', None)
        or 'Alafia Point Wellness Clinic'
    )

    birthday_patients = Patient.objects.filter(
        date_of_birth__month=today.month,
        date_of_birth__day=today.day,
        is_active=True,
        email__isnull=False,
    ).exclude(email='')

    sent = skipped = failed = 0

    for patient in birthday_patients:
        already_sent = BirthdayWish.objects.filter(
            patient=patient,
            year=today.year,
            success=True,
        ).exists()

        if already_sent:
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

        try:
            subject = f"Happy Birthday from {clinic_name}! 🎂"
            text_body = (
                f"Dear {patient.first_name},\n\n"
                f"Wishing you a very Happy Birthday from everyone at {clinic_name}!\n"
                f"We hope your special day is filled with joy and good health.\n\n"
                f"Best wishes,\n{clinic_name}"
            )
            html_body = render_to_string('patients/email/birthday_wishes.html', context)

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
            logger.info('Birthday wish sent to %s <%s>', patient.get_full_name(), patient.email)

        except Exception as exc:
            BirthdayWish.objects.update_or_create(
                patient=patient,
                year=today.year,
                defaults={'success': False, 'error_message': str(exc)},
            )
            failed += 1
            logger.error(
                'Failed to send birthday wish to %s <%s>: %s',
                patient.get_full_name(), patient.email, exc,
            )

    logger.info(
        'Birthday wishes complete for %s — sent: %d, skipped: %d, failed: %d',
        today, sent, skipped, failed,
    )
    return {'date': str(today), 'sent': sent, 'skipped': skipped, 'failed': failed}
