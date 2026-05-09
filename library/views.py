from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied
from django.db import connection, transaction
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
import logging

from django.utils import timezone
import re
from django.db.models import Count, Sum, Case, When, Value, IntegerField, Q
from django.db.models.functions import Coalesce
from django.conf import settings
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import requests
import os

logger = logging.getLogger(__name__)

def generate_book_cover(title, author, category):
    return f"https://via.placeholder.com/300x400?text={title.replace(' ', '+')}"

def get_gemini_api_key():
    return os.environ.get('GEMINI_API_KEY') or getattr(settings, 'GEMINI_API_KEY', None)

def get_openai_api_key():
    return os.environ.get('OPENAI_API_KEY') or getattr(settings, 'OPENAI_API_KEY', None)

def call_local_ollama(prompt):
    try:
        response = requests.post(
            'http://127.0.0.1:11434/api/generate',
            json={
                'model': 'llama3.2:1b',
                'prompt': prompt,
                'stream': False,
            },
            timeout=45,
        )
        if response.status_code == 200:
            result = response.json().get('response', '').strip()
            if result:
                logger.info("Ollama response received successfully")
                return result
            else:
                logger.warning("Ollama returned empty response")
                return None
        logger.warning("Ollama local model returned %s: %s", response.status_code, response.text)
        return None
    except requests.exceptions.Timeout:
        logger.warning("Ollama request timed out after 45 seconds")
        return None
    except requests.RequestException as e:
        logger.warning("Ollama local request failed: %s", str(e))
        return None

def call_openai_chat(api_key, prompt):
    url = 'https://api.openai.com/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful library assistant. Answer questions about books, borrowing rules, and provide assistance with library-related queries.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 250,
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content'].strip()
            logger.info("OpenAI response received successfully")
            return result
        logger.warning("OpenAI chat returned %s: %s", response.status_code, response.text)
        return None
    except requests.exceptions.Timeout:
        logger.warning("OpenAI request timed out after 30 seconds")
        return None
    except requests.RequestException as e:
        logger.warning("OpenAI request failed: %s", str(e))
        return None

def get_relevant_books_context(query, limit=5):
    from django.db.models import Q

    query_terms = query.strip()
    books = BOOK.objects.filter(
        Q(title__icontains=query_terms)
        | Q(author__name__icontains=query_terms)
        | Q(category__name__icontains=query_terms)
        | Q(description__icontains=query_terms)
    ).select_related('author', 'category')[:limit]

    if not books:
        books = BOOK.objects.select_related('author', 'category').all()[:limit]

    rows = []
    for book in books:
        rows.append(
            f"- Title: {book.title}\n  Author: {getattr(book.author, 'name', 'Unknown')}\n  "
            f"Category: {getattr(book.category, 'name', 'Unknown')}\n  Quantity: {book.quantity}\n  "
            f"Description: {book.description or 'No description available.'}"
        )

    return "\n".join(rows)


def call_ai_text(prompt):
    result = call_local_ollama(prompt)
    if result:
        return result

    openai_key = get_openai_api_key()
    if openai_key:
        return call_openai_chat(openai_key, prompt)

    return None

def generate_book_description(title, author, category):
    prompt = (
        f'Generate a compelling book description for "{title}" by {author} '
        f'in the {category} category. The description should be 2-3 sentences long, '
        f'engaging, and suitable for library readers. Focus on the main themes, '
        f'genre appeal, and what makes this book interesting. Avoid spoilers.'
    )
    result = call_ai_text(prompt)
    return result or "Description not available."

def generate_book_summary(title, author, category):
    # Try AI first with a very simple prompt
    prompt = f'Summary of {title} by {author}, {category} genre:'
    result = call_ai_text(prompt)
    
    # Check if AI failed or returned unhelpful content
    if (not result or 
        "couldn't find" in result.lower() or 
        "information" in result.lower() or 
        "possible that" in result.lower() or
        "if you have" in result.lower() or
        "not well" in result.lower() or
        len(result) < 20):
        
        # Use a reliable template-based summary
        result = f'"{title}" by {author} is an engaging {category} work that explores the genre\'s characteristic themes. The book offers readers a compelling narrative experience with well-developed characters and thoughtful storytelling. This {category} title provides an enjoyable reading experience that will appeal to fans of the genre.'
    
    return result

def generate_author_biography(author_name, books_written):
    prompt = (
        f'Generate a professional author biography for {author_name}. '
        f'Known works include: {books_written}. '
        f'The biography should be 3-4 sentences long, highlighting their writing style, '
        f'major achievements, and significance in literature. Make it sound authoritative '
        f'and suitable for a library system.'
    )
    result = call_ai_text(prompt)
    return result or "Biography not available."

def generate_book_cover(title, author, category):
    """
    Generate book cover using image generation API.
    For now, returns a placeholder URL. In production, integrate with actual image generation API.
    """
    import hashlib
    import urllib.parse
    
    # Create a unique identifier for this book
    book_id = hashlib.md5(f"{title}_{author}_{category}".encode()).hexdigest()[:8]
    
    # Generate a prompt for image generation
    prompt = f"Book cover for '{title}' by {author}, {category} genre, professional book design, minimalist, elegant"
    
    # For now, return a placeholder image URL with book-specific parameters
    # In production, replace with actual API call to image generation service
    placeholder_url = f"https://picsum.photos/seed/{book_id}/400/600.jpg"
    
    return {
        'cover_url': placeholder_url,
        'prompt_used': prompt,
        'note': 'This is a placeholder. Integrate with image generation API for production.'
    }


def resolve_relation(model, value):
    if not value:
        return None
    value = str(value).strip()
    try:
        return model.objects.get(pk=int(value))
    except (ValueError, model.DoesNotExist):
        return model.objects.filter(name__iexact=value).first()


def format_book_summary(book):
    return (
        f"ID: {book.id} | Title: {book.title} | Author: {getattr(book.author, 'name', 'Unknown')} | "
        f"Category: {getattr(book.category, 'name', 'Uncategorized')} | "
        f"Publisher: {getattr(book.publisher, 'name', 'Unknown')} | ISBN: {book.isbn} | "
        f"Qty: {book.quantity}"
    )


def list_books(query=None, limit=1000):
    books = BOOK.objects.select_related('author', 'category', 'publisher').all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['list all books', 'list books', 'show books', 'find books', 'search books']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(author__name__icontains=search)
            | Q(category__name__icontains=search)
            | Q(description__icontains=search)
        )
    books = books.order_by('title')[:limit]

    if not books:
        return "No matching books were found in the catalog."

    return "\n".join(format_book_summary(book) for book in books)


def count_books(query=None):
    books = BOOK.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['number of books in catalog', 'how many books', 'count books', 'total books', 'books count', 'number of books', 'books in catalog']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        books = books.filter(
            Q(title__icontains=search)
            | Q(author__name__icontains=search)
            | Q(category__name__icontains=search)
            | Q(description__icontains=search)
        )
    
    count = books.count()
    if search:
        return f"There are {count} books matching your search criteria."
    else:
        return f"There are {count} books in the library catalog."


def count_categories(query=None):
    categories = Category.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['number of categories', 'how many categories', 'count categories', 'total categories', 'categories count']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        categories = categories.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    
    count = categories.count()
    if search:
        return f"There are {count} categories matching your search criteria."
    else:
        return f"There are {count} categories in the library."


def count_authors(query=None):
    authors = Author.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['number of authors', 'how many authors', 'count authors', 'total authors', 'authors count']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        authors = authors.filter(
            Q(name__icontains=search) | Q(biography__icontains=search)
        )
    
    count = authors.count()
    if search:
        return f"There are {count} authors matching your search criteria."
    else:
        return f"There are {count} authors in the library."


def count_publishers(query=None):
    publishers = Publisher.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['number of publishers', 'how many publishers', 'count publishers', 'total publishers', 'publishers count']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        publishers = publishers.filter(
            Q(name__icontains=search) | Q(address__icontains=search)
        )
    
    count = publishers.count()
    if search:
        return f"There are {count} publishers matching your search criteria."
    else:
        return f"There are {count} publishers in the library."


def parse_field(query, field_name):
    regexes = [
        rf'{field_name}\s*[:=]\s*"([^"]+)"',
        rf'{field_name}\s*[:=]\s*([^,;\n]+)',
    ]
    for expr in regexes:
        match = re.search(expr, query, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def create_book_from_command(query):
    title = parse_field(query, 'title')
    if not title:
        return 'Please provide a book title using title:"..." or title:<name>.'

    author_value = parse_field(query, 'author')
    if not author_value:
        return 'Please provide an author using author:"..." or author:<name>.'

    category_value = parse_field(query, 'category')
    if not category_value:
        return 'Please provide a category using category:"..." or category:<name>.'

    publisher_value = parse_field(query, 'publisher')
    isbn = parse_field(query, 'isbn') or ''
    quantity = parse_field(query, 'quantity') or '1'
    published_date = parse_field(query, 'published_date') or parse_field(query, 'published')

    # Resolve or create author
    author = resolve_relation(Author, author_value)
    if not author:
        author = Author.objects.create(name=author_value)

    # Resolve or create category
    category = resolve_relation(Category, category_value)
    if not category:
        category = Category.objects.create(name=category_value)

    # Resolve or create publisher if provided
    publisher = None
    if publisher_value:
        publisher = resolve_relation(Publisher, publisher_value)
        if not publisher:
            publisher = Publisher.objects.create(name=publisher_value)

    try:
        quantity = int(quantity)
    except ValueError:
        quantity = 1

    book = BOOK.objects.create(
        title=title,
        author=author,
        category=category,
        publisher=publisher,
        isbn=isbn,
        quantity=quantity,
        published_date=published_date or None,
    )

    if not book.description:
        book.description = generate_book_description(
            book.title,
            author.name if author else '',
            category.name if category else '',
        )
    if not book.cover_url:
        book.cover_url = generate_book_cover(
            book.title,
            author.name if author else '',
            category.name if category else '',
        )
    book.save()
    return f'Created book {book.title} (ID: {book.id}).'


def update_book_from_command(query):
    book_id = parse_field(query, 'id') or parse_field(query, 'book')
    if not book_id:
        return 'Please specify the book ID to update using id:<book_id> or book:<book_id>.'

    try:
        book = BOOK.objects.get(pk=int(book_id))
    except (ValueError, BOOK.DoesNotExist):
        return f'Book not found for ID {book_id}.'

    title = parse_field(query, 'title')
    author_value = parse_field(query, 'author')
    category_value = parse_field(query, 'category')
    publisher_value = parse_field(query, 'publisher')
    isbn = parse_field(query, 'isbn')
    quantity = parse_field(query, 'quantity')
    published_date = parse_field(query, 'published_date') or parse_field(query, 'published')

    if title:
        book.title = title
    if author_value is not None:
        book.author = resolve_relation(Author, author_value)
    if category_value is not None:
        book.category = resolve_relation(Category, category_value)
    if publisher_value is not None:
        book.publisher = resolve_relation(Publisher, publisher_value)
    if isbn is not None:
        book.isbn = isbn
    if quantity is not None:
        try:
            book.quantity = int(quantity)
        except ValueError:
            pass
    if published_date is not None:
        book.published_date = published_date

    book.save()
    return f'Updated book {book.title} (ID: {book.id}).'


def delete_book_from_command(query):
    book_id = parse_field(query, 'id') or parse_field(query, 'book')
    if not book_id:
        return 'Please specify the book ID to delete using id:<book_id> or book:<book_id>.'

    try:
        book = BOOK.objects.get(pk=int(book_id))
    except (ValueError, BOOK.DoesNotExist):
        return f'Book not found for ID {book_id}.'

    title = book.title
    book.delete()
    return f'Deleted book {title} (ID: {book_id}).'


def format_author_summary(author):
    return f"ID: {author.id} | Name: {author.name}"


def format_category_summary(category):
    return f"ID: {category.id} | Name: {category.name}"


def format_publisher_summary(publisher):
    return f"ID: {publisher.id} | Name: {publisher.name}"


def list_authors(query=None, limit=1000):
    authors = Author.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['list all authors', 'list authors', 'show authors', 'find authors', 'search authors']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        authors = authors.filter(
            Q(name__icontains=search) | Q(biography__icontains=search)
        )
    authors = authors.order_by('name')[:limit]
    if not authors:
        return 'No matching authors were found.'
    return '\n'.join(format_author_summary(author) for author in authors)


def list_categories(query=None, limit=1000):
    categories = Category.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['list all categories', 'list categories', 'show categories', 'find categories', 'search categories']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        categories = categories.filter(
            Q(name__icontains=search) | Q(description__icontains=search)
        )
    categories = categories.order_by('name')[:limit]
    if not categories:
        return 'No matching categories were found.'
    return '\n'.join(format_category_summary(category) for category in categories)


def list_publishers(query=None, limit=1000):
    publishers = Publisher.objects.all()
    search = ''
    if query:
        search = query.strip()
        for prefix in ['list all publishers', 'list publishers', 'show publishers', 'find publishers', 'search publishers']:
            if search.lower().startswith(prefix):
                search = search[len(prefix):].strip(' :,-')
                break
    if search:
        publishers = publishers.filter(
            Q(name__icontains=search) | Q(address__icontains=search)
        )
    publishers = publishers.order_by('name')[:limit]
    if not publishers:
        return 'No matching publishers were found.'
    return '\n'.join(format_publisher_summary(publisher) for publisher in publishers)


def create_author_from_command(query):
    name = parse_field(query, 'name')
    if not name:
        return 'Please provide an author name using name:"..." or name:<name>.'
    biography = parse_field(query, 'biography') or ''
    author = Author.objects.create(name=name, biography=biography)
    return f'Created author {author.name} (ID: {author.id}).'


def update_author_from_command(query):
    author_id = parse_field(query, 'id') or parse_field(query, 'author')
    if not author_id:
        return 'Please specify the author ID to update using id:<author_id> or author:<author_id>.'
    try:
        author = Author.objects.get(pk=int(author_id))
    except (ValueError, Author.DoesNotExist):
        return f'Author not found for ID {author_id}.'
    name = parse_field(query, 'name')
    biography = parse_field(query, 'biography')
    if name is not None:
        author.name = name
    if biography is not None:
        author.biography = biography
    author.save()
    return f'Updated author {author.name} (ID: {author.id}).'


def delete_author_from_command(query):
    author_id = parse_field(query, 'id') or parse_field(query, 'author')
    if not author_id:
        return 'Please specify the author ID to delete using id:<author_id> or author:<author_id>.'
    try:
        author = Author.objects.get(pk=int(author_id))
    except (ValueError, Author.DoesNotExist):
        return f'Author not found for ID {author_id}.'
    name = author.name
    author.delete()
    return f'Deleted author {name} (ID: {author_id}).'


def create_category_from_command(query):
    name = parse_field(query, 'name')
    if not name:
        return 'Please provide a category name using name:"..." or name:<name>.'
    description = parse_field(query, 'description') or ''
    category = Category.objects.create(name=name, description=description)
    return f'Created category {category.name} (ID: {category.id}).'


def update_category_from_command(query):
    category_id = parse_field(query, 'id') or parse_field(query, 'category')
    if not category_id:
        return 'Please specify the category ID to update using id:<category_id> or category:<category_id>.'
    try:
        category = Category.objects.get(pk=int(category_id))
    except (ValueError, Category.DoesNotExist):
        return f'Category not found for ID {category_id}.'
    name = parse_field(query, 'name')
    description = parse_field(query, 'description')
    if name is not None:
        category.name = name
    if description is not None:
        category.description = description
    category.save()
    return f'Updated category {category.name} (ID: {category.id}).'


def delete_category_from_command(query):
    category_id = parse_field(query, 'id') or parse_field(query, 'category')
    if not category_id:
        return 'Please specify the category ID to delete using id:<category_id> or category:<category_id>.'
    try:
        category = Category.objects.get(pk=int(category_id))
    except (ValueError, Category.DoesNotExist):
        return f'Category not found for ID {category_id}.'
    name = category.name
    category.delete()
    return f'Deleted category {name} (ID: {category_id}).'


def create_publisher_from_command(query):
    name = parse_field(query, 'name')
    if not name:
        return 'Please provide a publisher name using name:"..." or name:<name>.'
    address = parse_field(query, 'address') or ''
    publisher = Publisher.objects.create(name=name, address=address)
    return f'Created publisher {publisher.name} (ID: {publisher.id}).'


def update_publisher_from_command(query):
    publisher_id = parse_field(query, 'id') or parse_field(query, 'publisher')
    if not publisher_id:
        return 'Please specify the publisher ID to update using id:<publisher_id> or publisher:<publisher_id>.'
    try:
        publisher = Publisher.objects.get(pk=int(publisher_id))
    except (ValueError, Publisher.DoesNotExist):
        return f'Publisher not found for ID {publisher_id}.'
    name = parse_field(query, 'name')
    address = parse_field(query, 'address')
    if name is not None:
        publisher.name = name
    if address is not None:
        publisher.address = address
    publisher.save()
    return f'Updated publisher {publisher.name} (ID: {publisher.id}).'


def delete_publisher_from_command(query):
    publisher_id = parse_field(query, 'id') or parse_field(query, 'publisher')
    if not publisher_id:
        return 'Please specify the publisher ID to delete using id:<publisher_id> or publisher:<publisher_id>.'
    try:
        publisher = Publisher.objects.get(pk=int(publisher_id))
    except (ValueError, Publisher.DoesNotExist):
        return f'Publisher not found for ID {publisher_id}.'
    name = publisher.name
    publisher.delete()
    return f'Deleted publisher {name} (ID: {publisher_id}).'


def handle_chat_crud(query, request):
    lower = query.strip().lower()
    if 'create book' in lower or 'add book' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can create books.'
        return create_book_from_command(query)
    if 'update book' in lower or 'edit book' in lower or 'change book' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can update books.'
        return update_book_from_command(query)
    if 'delete book' in lower or 'remove book' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can delete books.'
        return delete_book_from_command(query)
    if 'number of books' in lower or 'how many books' in lower or 'count books' in lower or 'total books' in lower or 'books count' in lower or 'books in catalog' in lower:
        return count_books(query)
    if 'list all books' in lower or 'list books' in lower or 'show books' in lower or 'find books' in lower or 'search books' in lower:
        return list_books(query)
    if 'create author' in lower or 'add author' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can create authors.'
        return create_author_from_command(query)
    if 'update author' in lower or 'edit author' in lower or 'change author' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can update authors.'
        return update_author_from_command(query)
    if 'delete author' in lower or 'remove author' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can delete authors.'
        return delete_author_from_command(query)
    if 'number of authors' in lower or 'how many authors' in lower or 'count authors' in lower or 'total authors' in lower or 'authors count' in lower:
        return count_authors(query)
    if 'list authors' in lower or 'show authors' in lower or 'find authors' in lower or 'search authors' in lower or 'list all authors' in lower:
        return list_authors(query)
    if 'create category' in lower or 'add category' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can create categories.'
        return create_category_from_command(query)
    if 'update category' in lower or 'edit category' in lower or 'change category' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can update categories.'
        return update_category_from_command(query)
    if 'delete category' in lower or 'remove category' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can delete categories.'
        return delete_category_from_command(query)
    if 'number of categories' in lower or 'how many categories' in lower or 'count categories' in lower or 'total categories' in lower or 'categories count' in lower:
        return count_categories(query)
    if 'list categories' in lower or 'show categories' in lower or 'find categories' in lower or 'search categories' in lower or 'list all categories' in lower:
        return list_categories(query)
    if 'create publisher' in lower or 'add publisher' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can create publishers.'
        return create_publisher_from_command(query)
    if 'update publisher' in lower or 'edit publisher' in lower or 'change publisher' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can update publishers.'
        return update_publisher_from_command(query)
    if 'delete publisher' in lower or 'remove publisher' in lower:
        if get_role(request) not in ['admin', 'librarian']:
            return 'Only admin or librarian users can delete publishers.'
        return delete_publisher_from_command(query)
    if 'number of publishers' in lower or 'how many publishers' in lower or 'count publishers' in lower or 'total publishers' in lower or 'publishers count' in lower:
        return count_publishers(query)
    if 'list publishers' in lower or 'show publishers' in lower or 'find publishers' in lower or 'search publishers' in lower or 'list all publishers' in lower:
        return list_publishers(query)
    return None


def get_role(request):
    if not request.user.is_authenticated:
        return "guest"
    try:
        return request.user.member.role
    except Exception:
        if request.user.is_superuser:
            return "admin"
        return "member"

def get_member_for_user(user):
    return Member.objects.filter(user=user).first()


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only admin or librarian can view dashboard stats.")
        stats = {
            "total_books": BOOK.objects.count(),
            "total_members": Member.objects.count(),
            "active_borrowings": Borrowing.objects.count(),
            "overdue_books": Borrowing.objects.filter(
                dueDate__lt=timezone.now().date()
            ).count(),
            "total_fines": Fine.objects.count(),
        }
        return Response(stats)


class BookViewSet(viewsets.ModelViewSet):
    queryset = BOOK.objects.select_related('author', 'publisher', 'category').all()
    serializer_class = BookSerializer
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def generate_summary(self, request, pk=None):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only admin or librarian can generate AI summaries.")
        
        book = self.get_object()
        
        try:
            # Generate AI summary using existing function
            summary = generate_book_summary(
                book.title,
                book.author.name if book.author else 'Unknown Author',
                book.category.name if book.category else 'Uncategorized'
            )
            
            if not summary or summary.strip() == "Summary not available.":
                return Response({
                    'success': False,
                    'error': 'AI service is currently unavailable. Please check your Ollama server or OpenAI API configuration.'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            logger.info(f"Generated summary for book {book.id}: {summary[:100]}...")
            
            # Update the book with the new summary
            book.summary = summary
            book.save(update_fields=['summary'])
            
            # Verify the save
            book.refresh_from_db()
            logger.info(f"Verified saved summary for book {book.id}: {book.summary[:100] if book.summary else 'None'}...")
            
            return Response({
                'success': True,
                'summary': summary,
                'message': 'AI summary generated successfully.'
            })
            
        except Exception as e:
            logger.error(f"Error generating AI summary for book {book.id}: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to generate AI summary. The AI service may be unavailable. Please try again later.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to add books.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.save()

        # Create notifications for all members (bulk create for performance)
        message = f"New book added to the library: '{book.title}' by {book.author.name if book.author else 'Unknown Author'}"
        members = Member.objects.values_list('id', flat=True)
        notifications = [
            Notification(member_id=member_id, message=message, type='general')
            for member_id in members
        ]
        Notification.objects.bulk_create(notifications)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to update books.")
        book = self.get_object()
        old_title = book.title
        response = super().update(request, *args, **kwargs)
        book.refresh_from_db()
        if book.title != old_title:
            # Create notifications for title change (bulk create for performance)
            message = f"Book title updated: '{old_title}' is now '{book.title}'"
            members = Member.objects.values_list('id', flat=True)
            notifications = [
                Notification(member_id=member_id, message=message, type='general')
                for member_id in members
            ]
            Notification.objects.bulk_create(notifications)
        return response

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to delete books.")
        book = self.get_object()
        book_title = book.title
        author_name = book.author.name if book.author else 'Unknown Author'

        # Store references for cleanup
        author_to_check = book.author
        publisher_to_check = book.publisher
        category_to_check = book.category

        # Create notifications before deleting (bulk create for performance)
        message = f"Book removed from the library: '{book_title}' by {author_name}"
        members = Member.objects.values_list('id', flat=True)
        notifications = [
            Notification(member_id=member_id, message=message, type='general')
            for member_id in members
        ]
        Notification.objects.bulk_create(notifications)

        # Delete the book
        response = super().destroy(request, *args, **kwargs)

        # Clean up orphaned authors, publishers, and categories
        # Only delete if they were automatically created and have no other books
        
        # Clean up orphaned authors
        if author_to_check:
            author_books_count = BOOK.objects.filter(author=author_to_check).count()
            if author_books_count == 0:
                # Check if this author has any biography (might be manually added)
                if not author_to_check.biography or author_to_check.biography.strip() == '':
                    author_to_check.delete()

        # Clean up orphaned publishers
        if publisher_to_check:
            publisher_books_count = BOOK.objects.filter(publisher=publisher_to_check).count()
            if publisher_books_count == 0:
                # Check if this publisher has no address (might be manually added)
                if not publisher_to_check.address or publisher_to_check.address.strip() == '':
                    publisher_to_check.delete()

        # Clean up orphaned categories (only if they have no description and no books)
        if category_to_check:
            category_books_count = BOOK.objects.filter(category=category_to_check).count()
            if category_books_count == 0:
                # Only delete auto-created categories (those without descriptions)
                if not category_to_check.description or category_to_check.description.strip() == '':
                    category_to_check.delete()

        return response


class MemberViewSet(viewsets.ModelViewSet):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return Member.objects.all()
        if role == "member":
            return Member.objects.filter(user=self.request.user)
        return Member.objects.none()

    def destroy(self, request, pk=None):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admins can delete members.")
        member = Member.objects.get(pk=pk)
        if member.user:
            member.user.delete()
        else:
            member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admins can add members.")
        data = request.data
        user = User.objects.create_user(
            username=data.get("email"),
            email=data.get("email"),
            password=data.get("password"),
        )
        member = Member.objects.create(
            user=user,
            name=data.get("name"),
            email=data.get("email"),
            phone=data.get("phone"),
            role=data.get("role", "member"),
        )
        serializer = MemberSerializer(member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admins can update members.")
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admins can update members.")
        return super().partial_update(request, *args, **kwargs)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return Reservation.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return Reservation.objects.none()
            return Reservation.objects.filter(member=member)
        return Reservation.objects.none()

    def create(self, request, *args, **kwargs):
        role = get_role(request)
        if role == "member":
            member = get_member_for_user(request.user)
            if not member:
                raise PermissionDenied("No member profile is linked to your account.")
            requested_member_id = request.data.get("member")
            if requested_member_id and str(requested_member_id) != str(member.id):
                raise PermissionDenied("You can only create reservations for yourself.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        role = get_role(request)
        if role == "member":
            obj = self.get_object()
            member = get_member_for_user(request.user)
            if not member or obj.member_id != member.id:
                raise PermissionDenied("You can only update your own reservations.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        role = get_role(request)
        if role == "member":
            obj = self.get_object()
            member = get_member_for_user(request.user)
            if not member or obj.member_id != member.id:
                raise PermissionDenied("You can only delete your own reservations.")
        return super().destroy(request, *args, **kwargs)


class FineViewSet(viewsets.ModelViewSet):
    queryset = Fine.objects.all()
    serializer_class = FineSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return Fine.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return Fine.objects.none()
            return Fine.objects.filter(borrowing__member=member)
        return Fine.objects.none()

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to add fines.")
        return super().create(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to delete fines.")
        return super().destroy(request, *args, **kwargs)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return Borrowing.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return Borrowing.objects.none()
            return Borrowing.objects.filter(member=member)
        return Borrowing.objects.none()

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can create borrowings.")
        
        with transaction.atomic():
            # Get the book and check availability
            book_id = request.data.get('book')
            book = BOOK.objects.get(id=book_id)
            
            if book.quantity <= 0:
                raise PermissionDenied("No copies available for borrowing.")
            
            # Create the borrowing record
            response = super().create(request, *args, **kwargs)
            
            # Update book quantity (decrease by 1)
            book.quantity -= 1
            book.save()
            
            # Create notification for member
            member_id = request.data.get('member')
            member = Member.objects.get(id=member_id)
            Notification.objects.create(
                member=member,
                message=f"Book borrowed: {book.title}. Due date: {response.data.get('dueDate')}",
                type='general',
                isRead=False
            )
            
            return response

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update borrowings.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete borrowings.")
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can access the Book returns")
        borrowing = self.get_object()
        with transaction.atomic():
            today = timezone.now().date()
            fine_amount = 0
            if today > borrowing.dueDate:
                overdue_days = (today - borrowing.dueDate).days
                policy = FinePolicy.objects.filter(category=borrowing.book.category).first()
                rate = policy.finePerDay if policy else 5
                fine_amount = overdue_days * rate

            BorrowingHistory.objects.create(
                book=borrowing.book,
                member=borrowing.member,
                borrowDate=borrowing.borrowDate,
                dueDate=borrowing.dueDate,
                returnDate=today,
                fineCharged=fine_amount,
            )

            # Create fine record if overdue
            if fine_amount > 0:
                Fine.objects.create(
                    borrowing=borrowing,
                    amount=fine_amount,
                    issuedDate=today
                )
                
                # Create overdue notification
                Notification.objects.create(
                    member=borrowing.member,
                    message=f"Overdue fine of ${fine_amount} charged for book: {borrowing.book.title}",
                    type='overdue',
                    isRead=False
                )

            book = borrowing.book
            book.quantity += 1
            book.save()

            # Mark borrowing as returned instead of deleting it
            borrowing.returned = True
            borrowing.returnDate = today
            borrowing.save()
            return Response(
                {
                    "message": "Book returned and history archived.",
                    "fineCharged": fine_amount,
                },
                status=status.HTTP_200_OK,
            )


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class FinePolicyViewSet(viewsets.ModelViewSet):
    queryset = FinePolicy.objects.all()
    serializer_class = FinePolicySerializer

    def create(self, request, *args, **kwargs):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admin can add fine policies.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admin can update fine policies.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admin can delete fine policies.")
        return super().destroy(request, *args, **kwargs)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return Notification.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return Notification.objects.none()
            return Notification.objects.filter(member=member)
        return Notification.objects.none()

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can create notifications.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        role = get_role(request)
        if role == "member":
            obj = self.get_object()
            member = get_member_for_user(request.user)
            if not member or obj.member_id != member.id:
                raise PermissionDenied("You can only update your own notifications.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete notifications.")
        return super().destroy(request, *args, **kwargs)


class BorrowingHistoryViewSet(viewsets.ModelViewSet):
    queryset = BorrowingHistory.objects.all()
    serializer_class = BorrowingHistorySerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return BorrowingHistory.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return BorrowingHistory.objects.none()
            return BorrowingHistory.objects.filter(member=member)
        return BorrowingHistory.objects.none()

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can create borrowing history records.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update borrowing history records.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete borrowing history records.")
        return super().destroy(request, *args, **kwargs)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    def create(self, request, *args, **kwargs):
        raise PermissionDenied("Authors cannot be created independently. They are created automatically when adding books.")

    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Authors cannot be updated. Delete and recreate through book management.")

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only admin or librarian can delete authors.")
        return super().destroy(request, *args, **kwargs)


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

    def create(self, request, *args, **kwargs):
        raise PermissionDenied("Publishers cannot be created independently. They are created automatically when adding books.")

    def update(self, request, *args, **kwargs):
        raise PermissionDenied("Publishers cannot be updated. Delete and recreate through book management.")

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only admin or librarian can delete publishers.")
        return super().destroy(request, *args, **kwargs)


class FinePaymentViewSet(viewsets.ModelViewSet):
    queryset = FinePayment.objects.all()
    serializer_class = FinePaymentSerializer

    def get_queryset(self):
        role = get_role(self.request)
        if role in ["admin", "librarian"]:
            return FinePayment.objects.all()
        if role == "member":
            member = get_member_for_user(self.request.user)
            if not member:
                return FinePayment.objects.none()
            return FinePayment.objects.filter(fine__borrowing__member=member)
        return FinePayment.objects.none()

    def create(self, request, *args, **kwargs):
        role = get_role(request)
        if role in ["admin", "librarian"]:
            return super().create(request, *args, **kwargs)
        if role == "member":
            fine_id = request.data.get("fine")
            member = get_member_for_user(request.user)
            if not member:
                raise PermissionDenied("No member profile is linked to your account.")
            allowed = Fine.objects.filter(id=fine_id, borrowing__member=member).exists()
            if not allowed:
                raise PermissionDenied("You can only pay your own fines.")
            return super().create(request, *args, **kwargs)
        raise PermissionDenied("Unauthorized role.")

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update fine payments.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete fine payments.")
        return super().destroy(request, *args, **kwargs)


class AdminReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if get_role(request) != "admin":
            raise PermissionDenied("Only admin can view admin reports.")

        role_filter = request.query_params.get("role")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        members_qs = Member.objects.all()
        if role_filter:
            members_qs = members_qs.filter(role=role_filter)

        borrowing_history_qs = BorrowingHistory.objects.all()
        if start_date:
            borrowing_history_qs = borrowing_history_qs.filter(returnDate__gte=start_date)
        if end_date:
            borrowing_history_qs = borrowing_history_qs.filter(returnDate__lte=end_date)

        members_with_borrow_counts = list(
            members_qs.annotate(
                total_borrowed=Count("borrowinghistory")
            ).values("id", "name", "role", "total_borrowed").order_by("-total_borrowed")
        )

        overdue_borrowings = Borrowing.objects.filter(
            dueDate__lt=timezone.now().date()
        ).values("id", "book__title", "member__name", "dueDate")

        borrowing_history_stats = borrowing_history_qs.aggregate(
            total_returns=Count("id"),
            total_fine_collected=Coalesce(Sum("fineCharged"), 0),
        )

        return Response({
            "filters": {
                "role": role_filter,
                "start_date": start_date,
                "end_date": end_date,
            },
            "member_activity": members_with_borrow_counts,
            "overdue_active_borrowings": list(overdue_borrowings),
            "history_summary": borrowing_history_stats,
        })


class LibrarianReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can view librarian reports.")

        category_id = request.query_params.get("category_id")
        due_before = request.query_params.get("due_before")

        books_qs = BOOK.objects.select_related("category", "author", "publisher")
        if category_id:
            books_qs = books_qs.filter(category_id=category_id)

        book_inventory = list(
            books_qs.values(
                "id", "title", "isbn", "quantity",
                "category__name", "author__name", "publisher__name",
            ).order_by("title")
        )

        borrowings_qs = Borrowing.objects.select_related("book", "member")
        if due_before:
            borrowings_qs = borrowings_qs.filter(dueDate__lte=due_before)

        active_borrowings = list(
            borrowings_qs.values(
                "id", "book__title", "member__name", "borrowDate", "dueDate",
            ).order_by("dueDate")
        )

        reservation_summary = list(
            Reservation.objects.values("status").annotate(total=Count("id")).order_by("status")
        )

        return Response({
            "filters": {"category_id": category_id, "due_before": due_before},
            "book_inventory": book_inventory,
            "active_borrowings": active_borrowings,
            "reservation_summary": reservation_summary,
        })


class MemberReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = get_role(request)
        if role not in ["admin", "librarian", "member"]:
            raise PermissionDenied("Unauthorized role.")

        requested_member_id = request.query_params.get("member_id")
        if role == "member":
            member = Member.objects.filter(user=request.user).first()
            if not member:
                raise PermissionDenied("No member profile is linked to your account.")
            target_member_id = member.id
        else:
            if not requested_member_id:
                return Response(
                    {"detail": "member_id query parameter is required for staff access."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            target_member_id = requested_member_id

        member_borrowing_history = list(
            BorrowingHistory.objects.filter(member_id=target_member_id)
            .select_related("book")
            .values("book__title", "borrowDate", "dueDate", "returnDate", "fineCharged")
            .order_by("-returnDate")
        )

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT member_id, member_name, book_title, fine_amount, issued_date
                FROM vw_unpaid_fines_report
                WHERE member_id = %s
                ORDER BY issued_date DESC
                """,
                [target_member_id],
            )
            unpaid_fines = [
                {
                    "member_id": row[0],
                    "member_name": row[1],
                    "book_title": row[2],
                    "fine_amount": float(row[3]),
                    "issued_date": row[4],
                }
                for row in cursor.fetchall()
            ]

        current_borrowings = list(
            Borrowing.objects.filter(member_id=target_member_id)
            .values("book__title", "borrowDate", "dueDate")
            .order_by("dueDate")
        )

        return Response({
            "member_id": target_member_id,
            "current_borrowings": current_borrowings,
            "borrowing_history": member_borrowing_history,
            "unpaid_fines": unpaid_fines,
        })


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({'error': 'Query is required'}, status=status.HTTP_400_BAD_REQUEST)

        crud_response = handle_chat_crud(query, request)
        if crud_response is not None:
            return Response({'response': crud_response})

        catalog_context = get_relevant_books_context(query)
        prompt = (
            "You are a helpful library assistant. You may perform CRUD operations on books, authors, categories, and publishers "
            "through commands like 'create book', 'update author', 'delete category', or 'list publishers'. "
            "Use the current library catalog information below to answer general questions. Do not invent books, authors, "
            "categories, publishers, or availability details outside the data provided."
        )
        prompt += f"\n\nCurrent catalog:\n{catalog_context}\n\nUser: {query}"

        ai_response = call_ai_text(prompt)
        if ai_response:
            return Response({'response': ai_response})

        return Response(
            {
                'error': 'AI service unavailable',
                'details': 'No AI provider responded. Ensure your local Ollama server is running or OPENAI_API_KEY is configured correctly.',
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )



def semantic_search_books(query, limit=10):
    """
    Perform semantic search using AI to understand user intent beyond keywords.
    """
    from django.db.models import Q, Case, When, Value, IntegerField
    from rest_framework import status
    
    # Extract search terms and intent using AI
    intent_prompt = f"""
    Analyze this book search query: "{query}"
    
    Extract and return ONLY the following in JSON format:
    {{
        "search_terms": ["term1", "term2", "term3"],
        "category_intent": "category_name_or_null",
        "author_intent": "author_name_or_null",
        "theme_intent": "theme_or_topic_or_null",
        "mood_intent": "mood_or_feeling_or_null"
    }}
    
    Focus on understanding what the user is looking for beyond literal keywords.
    """
    
    try:
        ai_analysis = call_ai_text(intent_prompt)
        
        # Parse AI response (simplified - in production would use proper JSON parsing)
        search_terms = []
        category_intent = None
        author_intent = None
        theme_intent = None
        mood_intent = None
        
        if ai_analysis:
            # Simple extraction (would be improved with proper JSON parsing)
            if "search_terms" in ai_analysis:
                search_terms = [term.strip() for term in ai_analysis.split('"search_terms":')[1].split("]")[0].replace('"', '').split(',') if term.strip()]
            if "category_intent" in ai_analysis and "null" not in ai_analysis.split("category_intent")[1].split(",")[0]:
                category_intent = ai_analysis.split("category_intent")[1].split('"')[1]
            if "author_intent" in ai_analysis and "null" not in ai_analysis.split("author_intent")[1].split(",")[0]:
                author_intent = ai_analysis.split("author_intent")[1].split('"')[1]
    except:
        # Fallback to basic keyword extraction
        search_terms = query.split()
    
    # Build semantic search query
    books_query = BOOK.objects.filter(quantity__gt=0)
    
    # Apply semantic filters
    q_objects = Q()
    
    # Add search terms with different weights
    for term in search_terms:
        q_objects |= Q(title__icontains=term)
        q_objects |= Q(description__icontains=term)
        q_objects |= Q(summary__icontains=term)
        q_objects |= Q(author__name__icontains=term)
        q_objects |= Q(category__name__icontains=term)
    
    # Apply intent-based filters
    if category_intent:
        books_query = books_query.filter(category__name__icontains=category_intent)
    
    if author_intent:
        books_query = books_query.filter(author__name__icontains=author_intent)
    
    # Execute search with semantic scoring
    books = books_query.filter(q_objects).select_related('author', 'category', 'publisher')
    
    # Calculate semantic relevance scores
    scored_books = []
    for book in books:
        score = 0
        
        # Title matches (highest weight)
        for term in search_terms:
            if term.lower() in book.title.lower():
                score += 10
        
        # Description/summary matches
        if book.description:
            for term in search_terms:
                if term.lower() in book.description.lower():
                    score += 5
        
        if book.summary:
            for term in search_terms:
                if term.lower() in book.summary.lower():
                    score += 5
        
        # Category matches
        if category_intent and book.category and category_intent.lower() in book.category.name.lower():
            score += 8
        
        # Author matches
        if author_intent and book.author and author_intent.lower() in book.author.name.lower():
            score += 8
        
        # Theme/mood matching in description
        if theme_intent and book.description and theme_intent.lower() in book.description.lower():
            score += 6
        
        if mood_intent and book.description and mood_intent.lower() in book.description.lower():
            score += 6
        
        scored_books.append((book, score))
    
    # Sort by semantic relevance score
    scored_books.sort(key=lambda x: x[1], reverse=True)
    
    # Return top results
    results = []
    for book, score in scored_books[:limit]:
        results.append({
            'id': book.id,
            'title': book.title,
            'author': book.author.name if book.author else 'Unknown',
            'category': book.category.name if book.category else 'Uncategorized',
            'description': book.description,
            'summary': book.summary,
            'isbn': book.isbn,
            'quantity': book.quantity,
            'cover_url': book.cover_url,
            'semantic_score': score,
            'relevance_reason': get_relevance_reason(query, book, score)
        })
    
    return results


def get_relevance_reason(query, book, score):
    """
    Generate a human-readable explanation for why this book was recommended.
    """
    if score >= 15:
        return f"Strong match: '{book.title}' highly relevant to your search for '{query}'"
    elif score >= 10:
        return f"Good match: '{book.title}' relates to your search interests"
    elif score >= 5:
        return f"Possible match: '{book.title}' may interest you based on '{query}'"
    else:
        return f"Related: '{book.title}' found in search results"