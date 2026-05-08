from django.core.management.base import BaseCommand
from library.models import Category

class Command(BaseCommand):
    help = 'Add sample categories to the library'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Fiction', 'description': 'Novels and stories'},
            {'name': 'Non-Fiction', 'description': 'Factual books and biographies'},
            {'name': 'Science Fiction', 'description': 'Science fiction novels'},
            {'name': 'Fantasy', 'description': 'Fantasy novels and stories'},
            {'name': 'Mystery', 'description': 'Mystery and thriller books'},
            {'name': 'Romance', 'description': 'Romance novels'},
            {'name': 'Biography', 'description': 'Life stories and biographies'},
            {'name': 'History', 'description': 'Historical books'},
            {'name': 'Science', 'description': 'Science and technology books'},
            {'name': 'Self-Help', 'description': 'Self-improvement books'},
            {'name': 'Business', 'description': 'Business and finance books'},
            {'name': 'Children', 'description': 'Children books'},
            {'name': 'Young Adult', 'description': 'Young adult fiction'},
            {'name': 'Poetry', 'description': 'Poetry collections'},
            {'name': 'Drama', 'description': 'Plays and drama'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')
            else:
                self.stdout.write(f'Category already exists: {category.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Total categories: {Category.objects.count()}'))
