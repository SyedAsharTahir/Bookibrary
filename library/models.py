from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timesince
# Create your models here.
class Category(models.Model):
    name=models.CharField(max_length=200)
    description=models.TextField(blank=True)

    def __str__(self):
        return self.name

class Author(models.Model):
    name=models.CharField(max_length=255)
    biography=models.TextField(blank=True)

    def __str__(self):
        return self.name

class Publisher(models.Model):
    name=models.CharField(max_length=255)
    address=models.TextField(blank=True)

    def __str__(self):
        return self.name

class BOOK(models.Model):
    title=models.CharField(max_length=2000)
    author=models.ForeignKey(Author,on_delete=models.CASCADE,null=True,blank=True)
    publisher=models.ForeignKey(Publisher,on_delete=models.SET_NULL,null=True,blank=True)
    isbn=models.CharField(max_length=20,unique=True)
    quantity=models.IntegerField(default=1)
    published_date=models.DateField(null=True)#store empty value as NULL in Database
    category=models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)#can be empty in forms and stored as null in DB

    
    def __str__(self):
        return self.title
    
class Member(models.Model):
    roleChoices=[
        ('admin','Administrator'),
        ('librarian','Librarian'),
        ('member','Member'),
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    name=models.CharField(max_length=2000)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=20)
    role=models.CharField(max_length=20,choices=roleChoices,default='member')
    joinedDate=models.DateField(auto_now_add=True)#sets the date to current date

    def __str__(self):
        return f"{self.name} ({self.role})"
    
class Borrowing(models.Model):
    book=models.ForeignKey(BOOK,on_delete=models.CASCADE)
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    borrowDate=models.DateField(auto_now_add=True)
    dueDate=models.DateField()
    returnDate=models.DateField(null=True,blank=True)#either no return date ,possible that it has not been borrowed yet
    #blank to allow it be left empty as well
    returned=models.BooleanField(default=False)#set intial to not returned

    def __str__(self):
        return f"{self.member} has borrowed {self.book}"
    
class Reservation(models.Model):
    statusChoice=[
        ('pending','Pending'),
        ('fulfilled','Fullfilled'),
        ('cancelled','Cancelled')
    ]
    book=models.ForeignKey(BOOK,on_delete=models.CASCADE)
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    reservedDate=models.DateField(auto_now_add=True)
    status=models.CharField(max_length=20,choices=statusChoice,default='pending')

    def __str__(self):
        return f"{self.member} has reserved the book:{self.book}"

class Fine(models.Model):
    borrowing=models.OneToOneField(Borrowing,on_delete=models.CASCADE)#one to one since each borrwoing book can have one fine
    amount=models.DecimalField(max_digits=6,decimal_places=2)
    paid=models.BooleanField(default=False)#initially not paid
    issuedDate=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.borrowing} => {self.amount}"
    

class BorrowingHistory(models.Model):
    book=models.ForeignKey(BOOK,on_delete=models.CASCADE)
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    borrowDate=models.DateField(auto_now_add=True)
    dueDate=models.DateField()
    returnDate=models.DateField(null=True,blank=True)
    fineCharged=models.DecimalField(max_digits=6,decimal_places=2,default=0)

    def save(self,*args,**kwargs):
        if not  self.borrowDate:
            from django.utils import timezone
            self.borrowDate=timezone.now().date()
        #automatically add a due date;for 14 days in this case if not set
        if not self.dueDate:
            self.dueDate=self.borrowDate +timedelta(14)
        super().save(*args,**kwargs)
    def __str__(self):
        return f"{self.member} returned {self.book}"

class Notification(models.Model):
    typeChoices=[
        ('overdue','Overdue'),
        ('reservation','Reservation'),
        ('general','General'),
    ]
    member=models.ForeignKey(Member,on_delete=models.CASCADE)
    message=models.TextField()
    type=models.CharField(max_length=20,choices=typeChoices,default='general')
    isRead=models.BooleanField(default=False)
    dateOfCreation=models.DateField(auto_now_add=True)

    class Meta:
        ordering=['-dateOfCreation']

    def __str__(self):
        return f"{self.member}:{self.type}({'Read' if self.isRead else 'Unread'})"


class FinePolicy(models.Model):
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    finePerDay=models.DecimalField(max_digits=6,decimal_places=2)
    maxFineDays=models.IntegerField(default=30)
    dateOfCreation=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name}=>Rs.{self.finePerDay}/day"
    
class FinePayment(models.Model):
    PaymentMethods=[('cash','Cash'),('online','Online')]
    fine=models.ForeignKey(Fine,on_delete=models.CASCADE,related_name='payments')
    amountpaid=models.DecimalField(max_digits=6,decimal_places=2)
    paymentdate=models.DateTimeField(auto_now_add=True)
    method=models.CharField(max_length=20,choices=PaymentMethods,default='cash')

    def __str__(self):
        return f"Payment of {self.amountpaid} for Fine ID :{self.fine.id}"