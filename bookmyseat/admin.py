import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

if not User.objects.filter(username='admin_fix').exists():
    User.objects.create_superuser('admin', 'admin@example.com', '1234')
    print("Superuser created!")
