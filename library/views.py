from django.shortcuts import render
# Create your views here.
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth.models import User
from rest_framework import viewsets,status
from rest_framework.decorators import action
from django.utils import timezone
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
#view is a class or perhaps a function that recieves a web request and returns a legible response
def get_role(request):
    if not request.user.is_authenticated:
        return 'guest'
    try:
        return request.user.member.role
    except:
        if request.user.is_superuser:
            return 'admin'
        return 'member'


class CustomTokenView(TokenObtainPairView):
    serializer_class=CustomTokenSerializer

class BookViewSet(viewsets.ModelViewSet):
    #api endpoint to allow users to be viewed or edited
    queryset=BOOK.objects.all()
    serializer_class=BookSerializer
    def create(self,request,*args,**kwargs):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Dont posses Permission To Add Books")
        return super().create(request,*args,**kwargs)
    
    def update(self,request,*args,**kwargs):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Dont posses Permission To Update Books")
        return super().update(request,*args,**kwargs)
    
    def destroy(self,request,*args,**kwargs):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Dont posses Permission To Delete Books")
        return super().destroy(request,*args,**kwargs)

class MemberViewSet(viewsets.ModelViewSet):
    queryset=Member.objects.all()
    serializer_class=MemberSerializer
    def destroy(self,request,pk=None):
        if get_role(request)!='admin':
            raise PermissionDenied("Only Admins Possess The Ability to Delete Member")
        member=Member.objects.get(pk=pk)
        if member.user:
            member.user.delete()
        else:
            member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    #creating a personal create function to override the default create
    #because the default creat would save whatever the frontend  sends to database
    def create(self,request):
        if get_role(request)!='admin':
            raise PermissionDenied("Only Admins Possess The Ability to Add Member")
        data=request.data#this has whatever the frontend sent
        #creating a django login account
        user=User.objects.create_user(
            username=data.get('email'),#using email as username,so log in is done via email
            email=data.get('email'),
            password=data.get('password')
        )
        #creating the memebr record
        member=Member.objects.create(
            user=user,#linking it to django user weve created 
            name=data.get('name'),
            email=data.get('email'),
            phone=data.get('phone'),
            role=data.get('role','member')
        )
        serializer=MemberSerializer(member)#member here is a python objectadn we cant send python object directly to frontend
        #MemberSerializer is used to convert it into a JSON format so it can be sent over internet
        return Response(serializer.data,status=status.HTTP_201_CREATED)#Response is a way to send data back to whoever has made the request(frontend in this case)
         #status=status.HTTP_201_CREATED indicates that the request succeeded and new user was created
class ReservationViewSet(viewsets.ModelViewSet):
    queryset=Reservation.objects.all()
    serializer_class=ReservationSerializer

class FineViewSet(viewsets.ModelViewSet):
    queryset=Fine.objects.all()
    serializer_class=FineSerializer
    
    def create(self,request,*args,**kwargs):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Dont posses Permission To Add Fines")
        return super().create(request,*args,**kwargs)
    def destroy(self,request,*args,**kwargs):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Dont posses Permission To Delete Fines")
        return super().destroy(request,*args,**kwargs)

class BorrowingViewSet(viewsets.ModelViewSet):
    queryset=Borrowing.objects.all()
    serializer_class=BorrowingSerializer
    @action(detail=True,methods=['post'])  
    def return_book(self,request,pk=None):
        if get_role(request) not in ['admin','librarian']:
            raise PermissionDenied("Only staff can access the Book returns")
        borrowing=self.get_object()
        with transaction.atomic():
            today=timezone.now().date()
            #calcualting fine using the fine Policy
            fineAmount=0
            if today>borrowing.dueDate:
                OverDueDays=(today-borrowing.dueDate).days
                policy=FinePolicy.objects.filter(category=borrowing.book.category).first()
                rate=policy.finePerDay if policy else 5 #5 if no policy 
                fineAmount=OverDueDays*rate
            #creating history record
            BorrowingHistory.objects.create(
                book=borrowing.book,
                member=borrowing.member,
                borrowDate=borrowing.borrowDate,
                dueDate=borrowing.dueDate,
                returnDate=today,
                fineCharged=fineAmount
            )
            #update the book stock
            book=borrowing.book
            book.quantity+=1
            book.save()
            #remove from active borrowing
            borrowing.delete()
            return Response({"message":"Book returned and History Archived","fineCharged":fineAmount},status=status.HTTP_200_OK)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset=Category.objects.all()
    serializer_class=CategorySerializer

class FinePolicyViewSet(viewsets.ModelViewSet):
    queryset=FinePolicy.objects.all()
    serializer_class=FinePolicySerializer

class NotificationViewSet(viewsets.ModelViewSet):
    queryset=Notification.objects.all()
    serializer_class=NotificationSerializer

class BorrowingHistoryViewSet(viewsets.ModelViewSet):
    queryset=BorrowingHistory.objects.all()
    serializer_class=BorrowingHistorySerializer

class AuthorViewSet(viewsets.ModelViewSet):
    queryset=Author.objects.all()
    serializer_class=AuthorSerializer

class PublisherViewSet(viewsets.ModelViewSet):
    queryset=Publisher.objects.all()
    serializer_class=PublisherSerializer

class FinePaymentViewSet(viewsets.ModelViewSet):
    queryset=FinePayment.objects.all()
    serializer_class=FinePaymentSerializer