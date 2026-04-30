from rest_framework import routers
from django.urls import include,path
from . import views

router=routers.DefaultRouter()
router.register(r"books",views.BookViewSet)
router.register(r"member",views.MemberViewSet)
router.register(r"fine",views.FineViewSet)
router.register(r"borrowing",views.BorrowingViewSet)
router.register(r"reservation",views.ReservationViewSet)
router.register(r"borrowinghistory",views.BorrowingHistoryViewSet)
router.register(r"finepolicy",views.FinePolicyViewSet)
router.register(r"notification",views.NotificationViewSet)
router.register(r"category",views.CategoryViewSet)
router.register(r"author",views.AuthorViewSet)
router.register(r"publisher",views.PublisherViewSet)
router.register(r"finepayment",views.FinePaymentViewSet)
urlpatterns=[
    path("",include(router.urls)),

]