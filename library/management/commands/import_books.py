from django.core.management.base import BaseCommand
from library.models import BOOK, Author, Category, Publisher
import csv
import os

class Command(BaseCommand):
    help = 'Import books from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--dry-run', action='store_true', help='Preview import without saving')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        dry_run = options['dry_run']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file_path}'))
            return
        
        self.stdout.write(f'Importing books from: {csv_file_path}')
        if dry_run:
            self.stdout.write('DRY RUN - No data will be saved')
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                
                imported_count = 0
                error_count = 0
                skipped_count = 0
                
                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        # Get values with flexible column mapping
                        title = self._get_value(row, ['title', 'book_title', 'name', 'book_name'])
                        author_name = self._get_value(row, ['author', 'author_name', 'writer', 'by'])
                        category_name = self._get_value(row, ['category', 'category_name', 'genre', 'type'])
                        
                        # If no category found, use a default based on title or author
                        if not category_name:
                            if 'Harry Potter' in title:
                                category_name = 'Fantasy'
                            elif 'Potter' in title:
                                category_name = 'Fantasy'
                            else:
                                category_name = 'Fiction'  # Default category
                        
                        if not title or not author_name or not category_name:
                            self.stdout.write(f'Row {row_num}: Missing required fields (title, author, category)')
                            error_count += 1
                            continue
                        
                        # Check for existing book
                        existing_author = Author.objects.filter(name=author_name).first()
                        if existing_author:
                            existing_book = BOOK.objects.filter(title=title, author=existing_author).first()
                            if existing_book:
                                self.stdout.write(f'Row {row_num}: Book already exists - {title} by {author_name}')
                                skipped_count += 1
                                continue
                        
                        if not dry_run:
                            # Create or get author
                            author, author_created = Author.objects.get_or_create(name=author_name.strip())
                            
                            # Create or get category
                            category, category_created = Category.objects.get_or_create(name=category_name.strip())
                            
                            # Create or get publisher (optional)
                            publisher = None
                            publisher_name = self._get_value(row, ['publisher', 'publisher_name', 'company', 'published_by'])
                            if publisher_name:
                                publisher, publisher_created = Publisher.objects.get_or_create(name=publisher_name.strip())
                            
                            # Get optional fields
                            isbn = self._get_value(row, ['isbn', 'isbn13', 'isbn10', 'isbn_number'])
                            quantity = self._get_value(row, ['quantity', 'qty', 'stock', 'amount', 'count']) or '1'
                            published_date = self._get_value(row, ['published_date', 'date', 'year', 'publication_date', 'published_year'])
                            description = self._get_value(row, ['description', 'desc', 'about', 'summary', 'book_description'])
                            summary = self._get_value(row, ['summary', 'brief', 'overview', 'plot'])
                            cover_url = self._get_value(row, ['cover_url', 'cover', 'image', 'cover_image', 'img_url'])
                            
                            # Handle published_date - convert year to full date if needed
                            final_published_date = None
                            if published_date:
                                pub_date = published_date.strip()
                                if pub_date.isdigit() and len(pub_date) == 4:
                                    # Convert year like "2006" to date "2006-01-01"
                                    final_published_date = f"{pub_date}-01-01"
                                else:
                                    final_published_date = pub_date
                            
                            # Create book
                            book = BOOK.objects.create(
                                title=title.strip(),
                                author=author,
                                category=category,
                                publisher=publisher,
                                isbn=isbn.strip() if isbn else None,
                                quantity=int(quantity) if quantity.isdigit() else 1,
                                published_date=final_published_date,
                                description=description.strip() if description else '',
                                summary=summary.strip() if summary else '',
                                cover_url=cover_url.strip() if cover_url else '',
                            )
                        
                        imported_count += 1
                        self.stdout.write(f'Row {row_num}: Imported - {title} by {author_name}')
                        
                    except Exception as e:
                        self.stdout.write(f'Row {row_num}: Error - {str(e)}')
                        error_count += 1
                
                self.stdout.write('\n' + '='*50)
                self.stdout.write(f'Import Summary:')
                self.stdout.write(f'  Imported: {imported_count} books')
                self.stdout.write(f'  Skipped: {skipped_count} books (duplicates)')
                self.stdout.write(f'  Errors: {error_count} rows')
                self.stdout.write(f'  Total processed: {imported_count + skipped_count + error_count} rows')
                
                if dry_run:
                    self.stdout.write('\nThis was a DRY RUN. Run without --dry-run to actually import.')
                else:
                    self.stdout.write('\nImport completed successfully!')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Import failed: {str(e)}'))
    
    def _get_value(self, row, possible_keys):
        for key in possible_keys:
            if key in row and row[key].strip():
                return row[key].strip()
        return None
