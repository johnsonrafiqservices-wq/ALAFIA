from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from inventory.models import CashFlow
import random

class Command(BaseCommand):
    help = 'Add more sample expense data to the inventory system'

    def handle(self, *args, **kwargs):
        # Define various expense categories and amounts
        expenses_data = [
            # Rent and Utilities
            {'description': 'Monthly Clinic Rent', 'amount': 500000, 'days_ago': 30},
            {'description': 'Monthly Clinic Rent', 'amount': 500000, 'days_ago': 60},
            {'description': 'Electricity Bill - November', 'amount': 85000, 'days_ago': 5},
            {'description': 'Electricity Bill - October', 'amount': 92000, 'days_ago': 35},
            {'description': 'Water Bill', 'amount': 35000, 'days_ago': 8},
            {'description': 'Internet & Phone Services', 'amount': 120000, 'days_ago': 10},
            
            # Salaries
            {'description': 'Staff Salaries - November', 'amount': 3500000, 'days_ago': 2},
            {'description': 'Staff Salaries - October', 'amount': 3500000, 'days_ago': 32},
            
            # Medical Supplies
            {'description': 'Medical Supplies Purchase', 'amount': 450000, 'days_ago': 15},
            {'description': 'Surgical Gloves Stock', 'amount': 120000, 'days_ago': 20},
            {'description': 'Syringes and Needles', 'amount': 85000, 'days_ago': 12},
            {'description': 'First Aid Supplies', 'amount': 95000, 'days_ago': 25},
            {'description': 'Bandages and Dressings', 'amount': 75000, 'days_ago': 18},
            {'description': 'Disinfectants and Sanitizers', 'amount': 55000, 'days_ago': 22},
            
            # Equipment Maintenance
            {'description': 'Medical Equipment Maintenance', 'amount': 250000, 'days_ago': 14},
            {'description': 'X-Ray Machine Service', 'amount': 180000, 'days_ago': 28},
            {'description': 'Computer System Maintenance', 'amount': 95000, 'days_ago': 19},
            {'description': 'Autoclave Repair', 'amount': 135000, 'days_ago': 24},
            
            # Office Supplies
            {'description': 'Printing and Stationery', 'amount': 45000, 'days_ago': 7},
            {'description': 'Office Supplies', 'amount': 38000, 'days_ago': 16},
            {'description': 'Patient Forms and Records', 'amount': 52000, 'days_ago': 21},
            
            # Transportation
            {'description': 'Fuel for Clinic Vehicle', 'amount': 180000, 'days_ago': 3},
            {'description': 'Fuel for Clinic Vehicle', 'amount': 165000, 'days_ago': 11},
            {'description': 'Vehicle Maintenance', 'amount': 220000, 'days_ago': 27},
            {'description': 'Staff Transport Allowance', 'amount': 95000, 'days_ago': 4},
            
            # Marketing and Admin
            {'description': 'Advertising and Marketing', 'amount': 150000, 'days_ago': 13},
            {'description': 'Website Hosting and Domain', 'amount': 85000, 'days_ago': 29},
            {'description': 'Professional Licenses Renewal', 'amount': 450000, 'days_ago': 45},
            
            # Cleaning and Maintenance
            {'description': 'Cleaning Services', 'amount': 120000, 'days_ago': 6},
            {'description': 'Janitorial Supplies', 'amount': 42000, 'days_ago': 9},
            {'description': 'Waste Disposal Services', 'amount': 75000, 'days_ago': 17},
            {'description': 'Pest Control Services', 'amount': 55000, 'days_ago': 26},
            
            # Insurance and Legal
            {'description': 'Clinic Insurance Premium', 'amount': 380000, 'days_ago': 40},
            {'description': 'Professional Liability Insurance', 'amount': 290000, 'days_ago': 42},
            
            # Training and Development
            {'description': 'Staff Training Workshop', 'amount': 320000, 'days_ago': 23},
            {'description': 'Medical Conference Registration', 'amount': 250000, 'days_ago': 31},
            
            # Miscellaneous
            {'description': 'Bank Service Charges', 'amount': 25000, 'days_ago': 1},
            {'description': 'Security Services', 'amount': 150000, 'days_ago': 5},
            {'description': 'Coffee & Tea Supplies', 'amount': 35000, 'days_ago': 8},
            {'description': 'Pharmacy License Renewal', 'amount': 180000, 'days_ago': 38},
        ]
        
        expenses_created = 0
        total_amount = 0
        
        for expense_data in expenses_data:
            # Create expense (CashFlow out)
            expense_date = timezone.now() - timedelta(days=expense_data['days_ago'])
            
            expense = CashFlow.objects.create(
                drug=None,  # General expense, not related to specific drug
                amount=expense_data['amount'],
                currency='UGX',
                flow_type='out',
                description=expense_data['description'],
                country='Uganda',
                date=expense_date
            )
            
            expenses_created += 1
            total_amount += expense_data['amount']
            
            if expenses_created % 10 == 0:
                self.stdout.write(self.style.SUCCESS(f'Created {expenses_created} expenses...'))
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Expense data created successfully!\n'
            f'- Total Expense Transactions: {expenses_created}\n'
            f'- Total Expenses Amount: UGX {total_amount:,.0f}\n'
            f'- Expense Categories: Rent, Utilities, Salaries, Medical Supplies,\n'
            f'  Equipment, Office, Transport, Marketing, Insurance, Training, etc.\n'
            f'\n📊 View expenses dashboard at: /inventory/expenses/'
        ))
