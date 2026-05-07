from rest_framework import routers
from django.urls import include, path
from . import views

router = routers.DefaultRouter()
router.register(r"members", views.MemberViewSet)
router.register(r"categories", views.CategoryViewSet)
router.register(r"authors", views.AuthorViewSet)
router.register(r"publishers", views.PublisherViewSet)
router.register(r"reservations", views.ReservationViewSet)
router.register(r"fines", views.FineViewSet)
router.register(r"notifications", views.NotificationViewSet)
router.register(r"books", views.BookViewSet)
router.register(r"borrowings", views.BorrowingViewSet)
router.register(r"borrowinghistory", views.BorrowingHistoryViewSet)
router.register(r"finepolicies", views.FinePolicyViewSet)
router.register(r"finepayments", views.FinePaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/stats/", views.DashboardStatsView.as_view(), name="dashboard-stats"),
    path("reports/admin/", views.AdminReportView.as_view(), name="admin-report"),
    path("reports/librarian/", views.LibrarianReportView.as_view(), name="librarian-report"),
    path("reports/member/", views.MemberReportView.as_view(), name="member-report"),
]