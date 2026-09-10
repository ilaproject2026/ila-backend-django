import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class Command(BaseCommand):
    help = "Creates or updates a default Super Admin user non-interactively for deployments (e.g. Vercel)"

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default=None, help='Superuser username')
        parser.add_argument('--email', type=str, default=None, help='Superuser email')
        parser.add_argument('--password', type=str, default=None, help='Superuser password')
        parser.add_argument('--phone', type=str, default=None, help='Superuser phone')

    def handle(self, *args, **options):
        from decouple import config
        username = options['username'] or config('SUPERUSER_USERNAME', 'admin')
        email = options['email'] or config('SUPERUSER_EMAIL', 'admin@ilaglobal.com')
        phone = options['phone'] or config('SUPERUSER_PHONE', '+919999999999')
        password = options['password'] or config('SUPERUSER_PASSWORD', 'Admin@123')

        try:
            existing_user = User.objects.filter(
                Q(username=username) | Q(email=email)
            ).first()

            if existing_user:
                # Ensure staff & superuser permissions are enabled
                updated = False
                if not existing_user.is_superuser or not existing_user.is_staff:
                    existing_user.is_superuser = True
                    existing_user.is_staff = True
                    existing_user.is_admin = True
                    existing_user.role = 'Super Admin'
                    existing_user.save(update_fields=['is_superuser', 'is_staff', 'is_admin', 'role'])
                    updated = True
                self.stdout.write(self.style.SUCCESS(
                    f"Superuser '{existing_user.username}' already exists. (Permissions verified: updated={updated})"
                ))
                return

            user = User.objects.create_superuser(
                username=username,
                email=email,
                phone=phone,
                password=password,
                role='Super Admin',
                department='Super Admin',
                is_admin=True,
                is_staff=True,
                is_superuser=True,
                is_email_verified=True,
                is_phone_verified=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f"Successfully created Superuser '{user.username}' ({user.email})"
            ))

        except Exception as e:
            self.stdout.write(self.style.WARNING(
                f"Notice: Superuser creation skipped or deferred: {e}"
            ))
