import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kalue.settings')
django.setup()

from django.contrib.auth.models import User

username = os.environ.get('DJANGO_SUPERUSER_USERNAME', '')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', '')
email    = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, password=password, email=email)
    print(f"✅ Superusuario '{username}' creado")
else:
    print(f"ℹ️ Superusuario '{username}' ya existe")