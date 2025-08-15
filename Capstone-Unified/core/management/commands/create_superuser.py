from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser with predefined credentials'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='bluevision_admin',
            help='Username for the superuser (default: bluevision_admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='AdminPass123',
            help='Password for the superuser (default: AdminPass123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@bluevision.com',
            help='Email for the superuser (default: admin@bluevision.com)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        try:
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'User "{username}" already exists. Updating password...')
                )
                user = User.objects.get(username=username)
                user.set_password(password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.email = email
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully updated user "{username}" with superuser privileges')
                )
            else:
                # Create new superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                user.is_active = True
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser "{username}"')
                )

            # Display credentials for confirmation
            self.stdout.write(f'\n--- Superuser Credentials ---')
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Is Staff: {user.is_staff}')
            self.stdout.write(f'Is Superuser: {user.is_superuser}')
            self.stdout.write(f'Is Active: {user.is_active}')
            self.stdout.write(f'-----------------------------\n')

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )