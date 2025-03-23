import os
import django
from django.conf import settings
from django.core.management import call_command

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")# Initialize Django
django.setup()


with open("db.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", "entertainment", "goals", "learning_tracker", "missions", "sessions_manager", indent=2, stdout=f)

