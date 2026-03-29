"""
Management command to send appointment reminders via email and SMS
Run with: python manage.py send_appointment_reminders
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
from appointments.models import Appointment, ReminderSettings, AppointmentReminder
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send appointment reminders via email and SMS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )
        parser.add_argument(
            '--reminder-type',
            type=str,
            choices=['first', 'second', 'final', 'all'],
            default='all',
            help='Type of reminder to send (default: all)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reminder_type = options['reminder_type']
        
        self.stdout.write(self.style.SUCCESS('Starting appointment reminder job...'))
        
        # Get reminder settings
        settings_obj = ReminderSettings.get_settings()
        
        if not settings_obj.is_active:
            self.stdout.write(self.style.WARNING('Reminder system is disabled in settings'))
            return
        
        # Get current time
        now = timezone.now()
        
        # Process each reminder type
        reminder_types = ['first', 'second', 'final'] if reminder_type == 'all' else [reminder_type]
        
        for rtype in reminder_types:
            self.process_reminder_type(rtype, settings_obj, now, dry_run)
        
        self.stdout.write(self.style.SUCCESS('Reminder job completed!'))

    def process_reminder_type(self, reminder_type, settings_obj, now, dry_run):
        """Process reminders for a specific type"""
        
        # Get hours before appointment
        if reminder_type == 'first':
            hours_before = settings_obj.first_reminder_hours
        elif reminder_type == 'second':
            hours_before = settings_obj.second_reminder_hours
        else:  # final
            hours_before = settings_obj.final_reminder_hours
        
        # Calculate time window
        reminder_time = now + timedelta(hours=hours_before)
        window_start = reminder_time - timedelta(minutes=30)
        window_end = reminder_time + timedelta(minutes=30)
        
        self.stdout.write(f'\nProcessing {reminder_type} reminders (for appointments around {reminder_time.strftime("%Y-%m-%d %H:%M")})')
        
        # Find appointments that need reminders
        appointments = Appointment.objects.filter(
            appointment_date=reminder_time.date(),
            appointment_time__gte=window_start.time(),
            appointment_time__lte=window_end.time(),
            status__in=['scheduled', 'confirmed']
        ).select_related('patient', 'provider', 'service')
        
        self.stdout.write(f'Found {appointments.count()} appointments needing {reminder_type} reminders')
        
        for appointment in appointments:
            # Check if reminder already sent
            if AppointmentReminder.objects.filter(
                appointment=appointment,
                reminder_type=reminder_type,
                status='sent'
            ).exists():
                self.stdout.write(f'  - Skipping {appointment.patient.get_full_name()} - already sent')
                continue
            
            self.send_reminders_for_appointment(appointment, reminder_type, settings_obj, now, dry_run)

    def send_reminders_for_appointment(self, appointment, reminder_type, settings_obj, now, dry_run):
        """Send reminders to all configured recipients"""
        
        self.stdout.write(f'  Processing: {appointment.patient.get_full_name()} on {appointment.appointment_date} at {appointment.appointment_time}')
        
        recipients = []
        
        # Patient
        if settings_obj.notify_patient:
            recipients.append({
                'type': 'patient',
                'name': appointment.patient.get_full_name(),
                'email': appointment.patient.email,
                'phone': appointment.patient.phone,
            })
        
        # Provider
        if settings_obj.notify_provider:
            recipients.append({
                'type': 'provider',
                'name': appointment.provider.get_full_name(),
                'email': appointment.provider.email,
                'phone': getattr(appointment.provider, 'phone', ''),
            })
        
        # Admin
        if settings_obj.notify_admin and settings_obj.admin_emails:
            for email in settings_obj.admin_emails.split(','):
                email = email.strip()
                if email:
                    recipients.append({
                        'type': 'admin',
                        'name': 'Admin',
                        'email': email,
                        'phone': '',
                    })
        
        # Nurse
        if settings_obj.notify_nurse and settings_obj.nurse_emails:
            for email in settings_obj.nurse_emails.split(','):
                email = email.strip()
                if email:
                    recipients.append({
                        'type': 'nurse',
                        'name': 'Nurse',
                        'email': email,
                        'phone': '',
                    })
        
        # Receptionist
        if settings_obj.notify_receptionist and settings_obj.receptionist_emails:
            for email in settings_obj.receptionist_emails.split(','):
                email = email.strip()
                if email:
                    recipients.append({
                        'type': 'receptionist',
                        'name': 'Receptionist',
                        'email': email,
                        'phone': '',
                    })
        
        # Send to each recipient
        for recipient in recipients:
            # Email reminder
            if settings_obj.email_enabled and recipient['email']:
                self.send_email_reminder(
                    appointment, reminder_type, recipient, settings_obj, now, dry_run
                )
            
            # SMS reminder
            if settings_obj.sms_enabled and recipient['phone']:
                self.send_sms_reminder(
                    appointment, reminder_type, recipient, settings_obj, now, dry_run
                )

    def send_email_reminder(self, appointment, reminder_type, recipient, settings_obj, now, dry_run):
        """Send email reminder"""
        
        # Prepare email context
        context = {
            'recipient_name': recipient['name'],
            'patient_name': appointment.patient.get_full_name(),
            'appointment_date': appointment.appointment_date,
            'appointment_time': appointment.appointment_time,
            'service': appointment.service.name,
            'provider': appointment.provider.get_full_name(),
            'duration': appointment.duration_minutes,
            'reminder_type': reminder_type,
        }
        
        # Subject
        subject = f"Appointment Reminder: {appointment.appointment_date.strftime('%B %d, %Y')} at {appointment.appointment_time.strftime('%I:%M %p')}"
        
        # Message body (plain text)
        if recipient['type'] == 'patient':
            message = f"""
Dear {recipient['name']},

This is a reminder about your upcoming appointment:

Date: {appointment.appointment_date.strftime('%A, %B %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Service: {appointment.service.name}
Provider: {appointment.provider.get_full_name()}
Duration: {appointment.duration_minutes} minutes

Please arrive 10 minutes early to complete any necessary paperwork.

If you need to reschedule or cancel, please contact us as soon as possible.

Thank you,
Physio & Nutrition Clinic
"""
        else:
            message = f"""
Appointment Reminder for {recipient['type'].title()}:

Patient: {appointment.patient.get_full_name()}
Date: {appointment.appointment_date.strftime('%A, %B %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Service: {appointment.service.name}
Provider: {appointment.provider.get_full_name()}

Status: {appointment.get_status_display()}

Physio & Nutrition Clinic Management System
"""
        
        if dry_run:
            self.stdout.write(f'    [DRY RUN] Would send email to {recipient["email"]}')
            self.stdout.write(f'              Subject: {subject}')
        else:
            try:
                # Create reminder record
                reminder = AppointmentReminder.objects.create(
                    appointment=appointment,
                    reminder_type=reminder_type,
                    recipient_type=recipient['type'],
                    method='email',
                    recipient_name=recipient['name'],
                    recipient_email=recipient['email'],
                    scheduled_for=now,
                    message_subject=subject,
                    message_body=message,
                    status='pending'
                )
                
                # Send email
                from_email = settings_obj.reminder_from_email or settings.DEFAULT_FROM_EMAIL
                send_mail(
                    subject,
                    message,
                    from_email,
                    [recipient['email']],
                    fail_silently=False,
                )
                
                # Update reminder status
                reminder.status = 'sent'
                reminder.sent_at = timezone.now()
                reminder.save()
                
                self.stdout.write(self.style.SUCCESS(f'    ✓ Email sent to {recipient["email"]}'))
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f'Failed to send email reminder: {error_msg}')
                self.stdout.write(self.style.ERROR(f'    ✗ Failed to send email to {recipient["email"]}: {error_msg}'))
                
                if 'reminder' in locals():
                    reminder.status = 'failed'
                    reminder.error_message = error_msg
                    reminder.save()

    def send_sms_reminder(self, appointment, reminder_type, recipient, settings_obj, now, dry_run):
        """Send SMS reminder"""
        
        # Prepare SMS message
        if recipient['type'] == 'patient':
            message = f"""
Appointment Reminder:

Date: {appointment.appointment_date.strftime('%b %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Service: {appointment.service.name}
Provider: {appointment.provider.get_full_name()}

Please arrive 10 minutes early.

Physio & Nutrition Clinic
"""
        else:
            message = f"""
Appointment: {appointment.patient.get_full_name()}
Date: {appointment.appointment_date.strftime('%b %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Service: {appointment.service.name}
"""
        
        if dry_run:
            self.stdout.write(f'    [DRY RUN] Would send SMS to {recipient["phone"]}')
        else:
            try:
                # Create reminder record
                reminder = AppointmentReminder.objects.create(
                    appointment=appointment,
                    reminder_type=reminder_type,
                    recipient_type=recipient['type'],
                    method='sms',
                    recipient_name=recipient['name'],
                    recipient_phone=recipient['phone'],
                    scheduled_for=now,
                    message_body=message,
                    status='pending'
                )
                
                # Send SMS using helper function
                from appointments.utils import send_sms
                success = send_sms(
                    recipient['phone'],
                    message,
                    settings_obj.sms_api_key,
                    settings_obj.sms_api_secret,
                    settings_obj.sms_from_number
                )
                
                if success:
                    reminder.status = 'sent'
                    reminder.sent_at = timezone.now()
                    reminder.save()
                    self.stdout.write(self.style.SUCCESS(f'    ✓ SMS sent to {recipient["phone"]}'))
                else:
                    raise Exception('SMS sending failed')
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f'Failed to send SMS reminder: {error_msg}')
                self.stdout.write(self.style.WARNING(f'    ✗ Failed to send SMS to {recipient["phone"]}: {error_msg}'))
                
                if 'reminder' in locals():
                    reminder.status = 'failed'
                    reminder.error_message = error_msg
                    reminder.save()
