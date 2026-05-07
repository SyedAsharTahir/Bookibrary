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

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=BOOK
        fields='__all__'#include every firld from the model

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
            'borrow_date',
            'due_date',
            'return_date',
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
            'reserved_date'
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
            'issued_date',
            'paid'
        ]

class FinePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model=FinePolicy
        fields='__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'

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
