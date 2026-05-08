from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from library.models import Member, BOOK, Borrowing, Fine, FinePolicy
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Create sample data for dashboard testing'

    def handle(self, *args, **options):
        # Create sample members
        members_data = [
            {'name': 'John Doe', 'email': 'john@example.com', 'role': 'member'},
            {'name': 'Jane Smith', 'email': 'jane@example.com', 'role': 'member'},
            {'name': 'Bob Johnson', 'email': 'bob@example.com', 'role': 'member'},
            {'name': 'Alice Brown', 'email': 'alice@example.com', 'role': 'librarian'},
            {'name': 'Charlie Wilson', 'email': 'charlie@example.com', 'role': 'admin'},
        ]
        
        created_members = []
        for member_data in members_data:
            user, created = User.objects.get_or_create(
                username=member_data['email'],
                defaults={
                    'email': member_data['email'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            
            member, member_created = Member.objects.get_or_create(
                user=user,
                defaults={
                    'name': member_data['name'],
                    'email': member_data['email'],
                    'role': member_data['role'],
                    'phone': '1234567890'
                }
            )
            if member_created:
                created_members.append(member)
                self.stdout.write(f'Created member: {member.name}')
            else:
                created_members.append(member)
                self.stdout.write(f'Using existing member: {member.name}')
        
        # Get some books for borrowing
        books = list(BOOK.objects.all()[:10])
        
        # Create sample borrowings
        for i, member in enumerate(created_members[:3]):  # Only for regular members
            if books:
                book = random.choice(books)
                # Create borrowing
                borrowing = Borrowing.objects.create(
                    member=member,
                    book=book,
                    borrowDate=timezone.now() - timedelta(days=random.randint(1, 30)),
                    dueDate=timezone.now() + timedelta(days=random.randint(-5, 14))
                )
                books.remove(book)  # Don't reuse the same book
                
                # Create overdue fine if needed
                if borrowing.dueDate < timezone.now():
                    Fine.objects.create(
                        borrowing=borrowing,
                        amount=random.uniform(5.0, 25.0)
                    )
        
        # Create fine policy (need a category first)
        from library.models import Category
        category, _ = Category.objects.get_or_create(name='General')
        FinePolicy.objects.create(
            category=category,
            finePerDay=2.50,
            maxFineDays=30
        )
        
        # Display statistics
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write(f'Total Members: {Member.objects.count()}')
        self.stdout.write(f'Active Borrowings: {Borrowing.objects.count()}')
        self.stdout.write(f'Overdue Books: {Borrowing.objects.filter(dueDate__lt=timezone.now().date()).count()}')
        self.stdout.write(f'Total Fines: {Fine.objects.count()}')
