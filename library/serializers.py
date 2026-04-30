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
    class Meta:
        model=Borrowing
        fields='__all__'

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model=Reservation
        fields='__all__'

class FineSerializer(serializers.ModelSerializer):
    class Meta:
        model=Fine
        fields='__all__'

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
