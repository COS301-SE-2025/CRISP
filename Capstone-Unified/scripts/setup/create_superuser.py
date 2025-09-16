from core.models.models import , Organization
from core.user_management.models import CustomUser
from django.contrib.auth.hashers import make_password

# Create default organization
org, created = Organization.objects.get_or_create(
    name="Blue Vision Technologies",
    defaults={
        'domain': 'bluevision.tech',
        'organization_type': 'private',
        'description': 'Default administrative organization',
        'contact_email': 'admin@bluevision.tech',
        'is_active': True
    }
)

# Create superuser
user, created = CustomUser.objects.get_or_create(
    username='bluevision_admin',
    defaults={
        'email': 'admin@bluevision.tech',
        'first_name': 'Blue Vision',
        'last_name': 'Admin',
        'role': 'BlueVisionAdmin',
        'organization': org,
        'is_active': True,
        'is_staff': True,
        'is_superuser': True,
        'password': make_password('admin123')
    }
)

if created:
    print(f"Created superuser: {user.username}")
else:
    print(f"Superuser already exists: {user.username}")