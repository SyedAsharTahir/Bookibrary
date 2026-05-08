from django.core.management.base import BaseCommand
from library.models import BOOK, Category
import random

class Command(BaseCommand):
    help = 'Assign categories to uncategorized books'

    def handle(self, *args, **options):
        # Get all uncategorized books
        uncategorized_books = BOOK.objects.filter(category__isnull=True)
        
        if not uncategorized_books.exists():
            self.stdout.write(self.style.WARNING('No uncategorized books found'))
            return
        
        # Get all available categories
        categories = list(Category.objects.all())
        
        if not categories:
            self.stdout.write(self.style.WARNING('No categories available to assign'))
            return
        
        # Assign categories to books
        updated_count = 0
        for book in uncategorized_books:
            # Assign a random category
            category = random.choice(categories)
            book.category = category
            book.save()
            updated_count += 1
            self.stdout.write(f'Assigned "{category.name}" to: {book.title}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully assigned categories to {updated_count} books'))
        self.stdout.write(f'Remaining uncategorized books: {BOOK.objects.filter(category__isnull=True).count()}')
