"""
Management command to generate comprehensive sample data for PhysioNutritionClinic system.
Usage: python manage.py generate_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Generate comprehensive sample data for the PhysioNutritionClinic system'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=15, help='Number of staff users')
        parser.add_argument('--patients', type=int, default=30, help='Number of patients')
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        from .data_generators import DataGenerator
        
        generator = DataGenerator(self.stdout, self.style)
        
        if options['clear']:
            generator.clear_existing_data()
        
        with transaction.atomic():
            generator.generate_all_data(options['users'], options['patients'])
        
        generator.print_summary()
        self.stdout.write(self.style.SUCCESS('\nSample data generation completed!'))
