import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from library.models import BOOK, Author, Category, Publisher

class Command(BaseCommand):
    help = 'Import dataset from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file_path}'))
            return
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                with transaction.atomic():
                    for row_num, row in enumerate(reader, 1):
                        try:
                            # Map CSV columns to model fields
                            title = row.get('title', '').strip()
                            author_name = row.get('author', '').strip()
                            category_name = row.get('category', '').strip()
                            publisher_name = row.get('publisher', '').strip()
                            isbn = row.get('isbn', '').strip()
                            quantity = int(row.get('quantity', 1))
                            published_date = row.get('published_date', '').strip()
                            description = row.get('description', '').strip()
                            summary = row.get('summary', '').strip()
                            cover_url = row.get('cover_url', '').strip()
                            
                            if not title:
                                self.stdout.write(self.style.WARNING(f'Row {row_num}: Missing title, skipping'))
                                continue
                            
                            # Create or get author
                            if author_name:
                                author, created = Author.objects.get_or_create(name=author_name.strip())
                            else:
                                author = None
                            
                            # Create or get category
                            if category_name:
                                category, created = Category.objects.get_or_create(name=category_name.strip())
                            else:
                                category = None
                            
                            # Create or get publisher
                            if publisher_name:
                                publisher, created = Publisher.objects.get_or_create(name=publisher_name.strip())
                            else:
                                publisher = None
                            
                            # Create book
                            book = BOOK.objects.create(
                                title=title,
                                author=author,
                                category=category,
                                publisher=publisher,
                                isbn=isbn,
                                quantity=quantity,
                                published_date=published_date if published_date else None,
                                description=description,
                                summary=summary,
                                cover_url=cover_url
                            )
                            
                            self.stdout.write(f'Created book: {book.title}')
                            
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Row {row_num}: {str(e)}'))
                            continue
                
                self.stdout.write(self.style.SUCCESS(f'Successfully imported books from {csv_file_path}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading file: {str(e)}'))
