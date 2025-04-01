from django.core.management.base import BaseCommand
from authentication.models import Account, AccountSettings

class Command(BaseCommand):
    help = "Create AccountSettings for existing Accounts missing settings."

    def handle(self, *args, **options):
        accounts = Account.objects.all()
        created_count = 0
        for account in accounts:
            if not hasattr(account, 'settings'):
                AccountSettings.objects.create(account=account)
                created_count += 1
                self.stdout.write(f"Created settings for {account.email}")
        self.stdout.write(self.style.SUCCESS(f"Created settings for {created_count} accounts."))