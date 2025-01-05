import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

django.setup()

User = get_user_model()

superusers = [
    {'user_name': '', 'password': '', 'email': ''},
    {'user_name': '', 'password': '', 'email': ''},
    # Thêm nhiều superuser ở đây
]

for superuser in superusers:
    if not User.objects.filter(user_name=superuser['user_name']).exists():
        User.objects.create_superuser(user_name=superuser['user_name'], email=superuser['email'], password=superuser['password'])
        print(f'Superuser created.')
    else:
        print(f'Superuser already exists.')
