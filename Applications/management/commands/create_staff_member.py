from django.core.management.base import BaseCommand
from Applications.Authentication.auth_models import User


class Command(BaseCommand):
    help = 'Create a staff member with a specific role and department'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, required=True, help='Username of staff member')
        parser.add_argument('--email', type=str, required=True, help='Email address of staff member')
        parser.add_argument('--password', type=str, required=True, help='Password for staff member')
        parser.add_argument('--role', type=str, required=True, help='Role assigned to staff member')
        parser.add_argument('--department', type=str, required=True, help='Department of staff member')
        parser.add_argument('--fullname', type=str, default='', help='Full name of staff member')
        parser.add_argument('--superuser', action='store_true', help='Grant superuser privileges')

    def handle(self, *args, **options):
        username = options['username'].strip()
        email = options['email'].strip().lower()
        password = options['password']
        role = options['role'].strip()
        department = options['department'].strip()
        fullname = options.get('fullname', '').strip()
        is_superuser = options.get('superuser', False)

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'role': role,
                'department': department,
                'fullname': fullname,
                'is_staff': True,
                'is_superuser': is_superuser,
                'is_email_verified': True,
                'is_active': True,
            }
        )

        if not created:
            user.email = email
            user.role = role
            user.department = department
            if fullname:
                user.fullname = fullname
            user.is_staff = True
            if is_superuser:
                user.is_superuser = True
            user.is_email_verified = True
            user.is_active = True

        user.set_password(password)
        user.save()

        action = "Created new" if created else "Updated existing"
        self.stdout.write(
            self.style.SUCCESS(
                f"[OK] {action} staff member '{user.username}' ({user.role} | {user.department}) successfully."
            )
        )
