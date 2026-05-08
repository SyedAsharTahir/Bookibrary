from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import getpass

class Command(BaseCommand):
    help = 'Reset password for a user account'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the account to reset password for')
        parser.add_argument('--password', type=str, help='New password (will prompt if not provided)')

    def handle(self, *args, **options):
        username = options['username']
        password = options.get('password')
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Active: {user.is_active}')
            self.stdout.write(f'Staff: {user.is_staff}')
            self.stdout.write(f'Superuser: {user.is_superuser}')
            
            if not password:
                password = getpass.getpass('Enter new password: ')
                confirm_password = getpass.getpass('Confirm new password: ')
                
                if password != confirm_password:
                    self.stdout.write(self.style.ERROR('Passwords do not match!'))
                    return
                
                if len(password) < 8:
                    self.stdout.write(self.style.ERROR('Password must be at least 8 characters long!'))
                    return
            
            user.set_password(password)
            user.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Password successfully reset for user: {username}'))
            self.stdout.write(self.style.SUCCESS('You can now login with the new password.'))
            
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User "{username}" not found!'))
            
            # Show available users
            self.stdout.write('\nAvailable users:')
            for user in User.objects.all():
                self.stdout.write(f'  - {user.username} ({"admin" if user.is_superuser else "staff" if user.is_staff else "regular"})')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error resetting password: {str(e)}'))
