import os
import django
from django.contrib.auth import get_user_model
# Thiết lập biến môi trường DJANGO_SETTINGS_MODULE
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Khởi động Django
django.setup()

User = get_user_model()

superusers = [
    {'user_name': 'nguyenquangtuyen', 'password': 'thaco@1234', 'email': 'quangtuyennguyen0299@gmail.com'},
    {'user_name': 'phananhtu', 'password': 'thaco@1234', 'email': 'phananhtu@thaco.com.vn'},
    # Thêm nhiều superuser ở đây
]

for superuser in superusers:
    if not User.objects.filter(user_name=superuser['user_name']).exists():
        User.objects.create_superuser(user_name=superuser['user_name'], email=superuser['email'], password=superuser['password'])
        print(f'Superuser created.')
    else:
        print(f'Superuser already exists.')
