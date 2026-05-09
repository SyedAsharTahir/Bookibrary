from django.core.management.base import BaseCommand
from django.utils import timezone
from library.models import Borrowing, Fine, Notification, FinePolicy
from datetime import timedelta

class Command(BaseCommand):
    help = 'Check for overdue books and create fines/notifications'

    def handle(self, *args, **options):
        today = timezone.now().date()
        overdue_borrowings = Borrowing.objects.filter(
            dueDate__lt=today,
            returned=False
        )
        
        for borrowing in overdue_borrowings:
            # Calculate overdue days and fine
            overdue_days = (today - borrowing.dueDate).days
            policy = FinePolicy.objects.filter(category=borrowing.book.category).first()
            rate = policy.finePerDay if policy else 5
            fine_amount = overdue_days * rate
            
            # Check if fine already exists
            existing_fine = Fine.objects.filter(borrowing=borrowing).first()
            if not existing_fine:
                # Create fine record
                Fine.objects.create(
                    borrowing=borrowing,
                    amount=fine_amount,
                    issuedDate=today
                )
                
                # Create overdue notification
                Notification.objects.create(
                    member=borrowing.member,
                    message=f"Your book '{borrowing.book.title}' is {overdue_days} days overdue. Fine: ${fine_amount}",
                    type='overdue',
                    isRead=False
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created fine ${fine_amount} for {borrowing.member.name} - {borrowing.book.title}"
                    )
                )
        
        if not overdue_borrowings.exists():
            self.stdout.write(self.style.SUCCESS('No overdue books found.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Processed {overdue_borrowings.count()} overdue books.")
            )
