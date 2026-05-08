from rest_framework import serializers
from .models import BOOK,Member,Borrowing,Reservation,Fine,FinePolicy,Category,BorrowingHistory,Notification,Author,FinePayment,Publisher
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
            token=super().get_token(user)
            try:
                token['role']=user.member.role
                token['name']=user.member.name
            except:
                token['role']='admin'
                token['name']=user.username
            return token

class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for book list - only essential fields"""
    author_name = serializers.CharField(source='author.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)

    class Meta:
        model = BOOK
        fields = ['id', 'title', 'author_name', 'category_name', 'publisher_name', 'isbn', 'quantity', 'published_date']

class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(write_only=True, required=False)
    category_name = serializers.CharField(write_only=True, required=False)
    publisher_name = serializers.CharField(write_only=True, required=False)
    
    # Keep read-only fields for responses
    author_display_name = serializers.CharField(source='author.name', read_only=True)
    category_display_name = serializers.CharField(source='category.name', read_only=True)
    publisher_display_name = serializers.CharField(source='publisher.name', read_only=True)

    class Meta:
        model = BOOK
        fields = '__all__'
    
    def create(self, validated_data):
        author_name = validated_data.pop('author_name', None)
        category_name = validated_data.pop('category_name', None)
        publisher_name = validated_data.pop('publisher_name', None)
        
        # Create or get author
        if author_name:
            author, created = Author.objects.get_or_create(name=author_name.strip())
            validated_data['author'] = author
        
        # Create or get category
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name.strip())
            validated_data['category'] = category
        
        # Create or get publisher
        if publisher_name:
            publisher, created = Publisher.objects.get_or_create(name=publisher_name.strip())
            validated_data['publisher'] = publisher
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        author_name = validated_data.pop('author_name', None)
        category_name = validated_data.pop('category_name', None)
        publisher_name = validated_data.pop('publisher_name', None)
        
        # Update author
        if author_name:
            author, created = Author.objects.get_or_create(name=author_name.strip())
            validated_data['author'] = author
        
        # Update category
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name.strip())
            validated_data['category'] = category
        
        # Update publisher
        if publisher_name:
            publisher, created = Publisher.objects.get_or_create(name=publisher_name.strip())
            validated_data['publisher'] = publisher
        
        return super().update(instance, validated_data)

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model=Member
        fields='__all__'

class BorrowingSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            'id',
            'book',
            'book_title',
            'member',
            'member_name',
            'borrowDate',
            'dueDate',
            'returnDate',
            'returned'
        ]
class ReservationSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    member_name = serializers.CharField(source='member.name', read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id',
            'book',
            'book_title',
            'member',
            'member_name',
            'status',
            'reservedDate'
        ]
class FineSerializer(serializers.ModelSerializer):
    borrowing_id = serializers.IntegerField(source='borrowing.id', read_only=True)
    member_name = serializers.CharField(source='borrowing.member.name', read_only=True)
    book_title = serializers.CharField(source='borrowing.book.title', read_only=True)

    class Meta:
        model = Fine
        fields = [
            'id',
            'borrowing',
            'borrowing_id',
            'member_name',
            'book_title',
            'amount',
            'issuedDate',
            'paid'
        ]

class FinePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model=FinePolicy
        fields='__all__'

class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.SerializerMethodField()

    class Meta:
        model=Category
        fields='__all__'

    def get_book_count(self, obj):
        from library.models import BOOK
        return BOOK.objects.filter(category=obj).count()

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Notification
        fields='__all__'

class BorrowingHistorySerializer(serializers.ModelSerializer):
    book_title=serializers.CharField(source='book.title',read_only=True)
    member_name=serializers.CharField(source='member.name',read_only=True)
    class Meta:
        model=BorrowingHistory
        fields='__all__'

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Author
        fields='__all__'

class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model=Publisher
        fields='__all__'

class FinePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=FinePayment
        fields='__all__'
