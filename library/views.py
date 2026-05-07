from django.shortcuts import render
from rest_framework.exceptions import PermissionDenied
from django.db import connection, transaction
from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.decorators import action
from django.utils import timezone
from django.db.models import Count, Sum, Case, When, Value, IntegerField
from django.db.models.functions import Coalesce
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView


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
    queryset = BOOK.objects.all()
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to add books.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to update books.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("You do not have permission to delete books.")
        return super().destroy(request, *args, **kwargs)


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
        return super().create(request, *args, **kwargs)

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

            book = borrowing.book
            book.quantity += 1
            book.save()

            borrowing.delete()
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

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can add categories.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update categories.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete categories.")
        return super().destroy(request, *args, **kwargs)


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
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can add authors.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update authors.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete authors.")
        return super().destroy(request, *args, **kwargs)


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer

    def create(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can add publishers.")
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can update publishers.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if get_role(request) not in ["admin", "librarian"]:
            raise PermissionDenied("Only staff can delete publishers.")
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
                "id",
                "title",
                "isbn",
                "quantity",
                "category__name",
                "author__name",
                "publisher__name",
            ).order_by("title")
        )

        borrowings_qs = Borrowing.objects.select_related("book", "member")
        if due_before:
            borrowings_qs = borrowings_qs.filter(dueDate__lte=due_before)

        active_borrowings = list(
            borrowings_qs.values(
                "id",
                "book__title",
                "member__name",
                "borrowDate",
                "dueDate",
            ).order_by("dueDate")
        )

        reservation_summary = list(
            Reservation.objects.values("status").annotate(total=Count("id")).order_by("status")
        )

        return Response({
            "filters": {
                "category_id": category_id,
                "due_before": due_before,
            },
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


class RecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = get_role(request)
        requested_member_id = request.query_params.get("member_id")
        limit = int(request.query_params.get("limit", 5))
        limit = max(1, min(limit, 20))

        if role == "member":
            member = Member.objects.filter(user=request.user).first()
            if not member:
                raise PermissionDenied("No member profile is linked to your account.")
            target_member_id = member.id
        else:
            if requested_member_id:
                target_member_id = requested_member_id
            else:
                member = Member.objects.filter(user=request.user).first()
                if not member:
                    return Response(
                        {"detail": "member_id is required for this account."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                target_member_id = member.id

        history = BorrowingHistory.objects.filter(member_id=target_member_id).values(
            "book_id", "book__category_id", "book__author_id"
        )
        active = Borrowing.objects.filter(member_id=target_member_id).values(
            "book_id", "book__category_id", "book__author_id"
        )

        seen_book_ids = {row["book_id"] for row in history} | {row["book_id"] for row in active}

        category_weights = {}
        author_weights = {}
        for row in list(history) + list(active):
            category_id = row["book__category_id"]
            author_id = row["book__author_id"]
            if category_id:
                category_weights[category_id] = category_weights.get(category_id, 0) + 3
            if author_id:
                author_weights[author_id] = author_weights.get(author_id, 0) + 2

        score_expr = Value(0, output_field=IntegerField())
        for category_id, weight in category_weights.items():
            score_expr = score_expr + Case(
                When(category_id=category_id, then=Value(weight)),
                default=Value(0),
                output_field=IntegerField(),
            )
        for author_id, weight in author_weights.items():
            score_expr = score_expr + Case(
                When(author_id=author_id, then=Value(weight)),
                default=Value(0),
                output_field=IntegerField(),
            )

        recommendations_qs = (
            BOOK.objects.filter(quantity__gt=0)
            .exclude(id__in=seen_book_ids)
            .annotate(ai_score=score_expr, popularity=Count("borrowinghistory"))
            .order_by("-ai_score", "-popularity", "title")
        )

        recommendations = list(
            recommendations_qs.values(
                "id",
                "title",
                "isbn",
                "quantity",
                "category__name",
                "author__name",
                "publisher__name",
                "ai_score",
                "popularity",
            )[:limit]
        )

        if not recommendations:
            recommendations = list(
                BOOK.objects.filter(quantity__gt=0)
                .annotate(popularity=Count("borrowinghistory"))
                .order_by("-popularity", "-quantity", "title")
                .values(
                    "id",
                    "title",
                    "isbn",
                    "quantity",
                    "category__name",
                    "author__name",
                    "publisher__name",
                    "popularity",
                )[:limit]
            )
            for item in recommendations:
                item["ai_score"] = 0

        return Response(
            {
                "member_id": target_member_id,
                "algorithm": "Weighted content-based filtering (category + author + popularity)",
                "recommendations": recommendations,
            }
        )

