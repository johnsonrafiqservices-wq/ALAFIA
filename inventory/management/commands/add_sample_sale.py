from django.core.management.base import BaseCommand
from django.utils import timezone
from inventory.models import Drug, DrugUsage, CashFlow, Supplier

class Command(BaseCommand):
    help = 'Add sample sale data to the inventory system'

    def handle(self, *args, **kwargs):
        # Create or get a supplier
        supplier, created = Supplier.objects.get_or_create(
            name='MediSupply Uganda Ltd',
            defaults={
                'country': 'Uganda',
                'contact': '+256 700 123456'
            }
        )
        
        # Create or get a drug
        drug, created = Drug.objects.get_or_create(
            name='Paracetamol',
            defaults={
                'description': 'Pain reliever and fever reducer',
                'atc_code': 'N02BE01',
                'manufacturer': 'PharmaCare Ltd',
                'batch_number': 'PARA2024001',
                'expiry_date': '2025-12-31',
                'quantity': 500,
                'unit_price': 500,
                'currency': 'UGX',
                'country': 'Uganda',
                'supplier': supplier
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created drug: {drug.name}'))
        
        # Create a sample sale
        sale = DrugUsage.objects.create(
            drug=drug,
            used_quantity=20,
            usage_type='sale',
            sold_to='John Doe',
            sale_price=15000,  # 20 units at 750 UGX each
            currency='UGX',
            country='Uganda',
            date_used=timezone.now()
        )
        
        # Update drug quantity
        drug.quantity -= sale.used_quantity
        drug.save()
        
        # Record cash flow for sale
        CashFlow.objects.create(
            drug=drug,
            amount=sale.sale_price,
            currency='UGX',
            flow_type='in',
            description=f'Sale to {sale.sold_to}',
            country='Uganda',
            date=timezone.now()
        )
        
        # Create a sample expense
        expense = CashFlow.objects.create(
            drug=None,
            amount=50000,
            currency='UGX',
            flow_type='out',
            description='Rent payment for clinic space',
            country='Uganda',
            date=timezone.now()
        )
        
        # Create another expense
        expense2 = CashFlow.objects.create(
            drug=None,
            amount=25000,
            currency='UGX',
            flow_type='out',
            description='Electricity bill',
            country='Uganda',
            date=timezone.now()
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'Successfully created:\n'
            f'- Sale: {sale.used_quantity} units of {drug.name} for UGX {sale.sale_price}\n'
            f'- Expense 1: UGX {expense.amount} - {expense.description}\n'
            f'- Expense 2: UGX {expense2.amount} - {expense2.description}'
        ))
