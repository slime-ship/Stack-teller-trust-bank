# wealthbridge/management/commands/init_crypto_settings.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bank_app.models import SystemCryptoSetting  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Initialize system crypto settings'
    
    def handle(self, *args, **options):
        settings = SystemCryptoSetting.get_settings()
        self.stdout.write(self.style.SUCCESS('[SUCCESS] System crypto settings initialized.'))
        self.stdout.write(f"   Auto Approve Deposits: {settings.auto_approve_deposits}")
        self.stdout.write(f"   Deposit Fee %: {settings.deposit_fee_percentage}")
        self.stdout.write(f"   Min Deposit: {settings.min_deposit_amount}")
        self.stdout.write(f"   Max Deposit: {settings.max_deposit_amount}")
        self.stdout.write(f"   Updated At: {settings.updated_at}")