from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Category)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(BOOK)
admin.site.register(Borrowing)
admin.site.register(BorrowingHistory)
admin.site.register(Reservation)
admin.site.register(Notification)
admin.site.register(Fine)
admin.site.register(FinePayment)
admin.site.register(FinePolicy)
admin.site.register(Member)