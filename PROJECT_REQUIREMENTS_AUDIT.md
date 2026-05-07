# CS 2005 Requirement Compliance Audit (Bookibrary)

## Overall Status

Your project is **partially compliant**. The implementation phase is mostly covered in code, but documentation deliverables (proposal write-up, full normalization proof, and ERD artifact) must be submitted explicitly.

## Requirement-by-Requirement Checklist

| Requirement | Status | Evidence in Project | Gap / Action Needed |
|---|---|---|---|
| Web application | Done | React frontend in `bookibrary-frontend`, Django backend in `library` + `myProject` | None |
| SQL database mandatory | Done | PostgreSQL in `myProject/settings.py` | None |
| Proposal: introduction + purpose | Missing as artifact | Not found as a separate proposal document | Add proposal section in report |
| Proposal: system functionality | Missing as artifact | Functionality exists in endpoints/pages | Document in report |
| Proposal: user roles + permissions | Partial | Roles in `Member.role`; role checks in `library/views.py` | Add explicit role matrix in report |
| Proposal: technologies | Partial | Stack visible from code (`React`, `Django`, `DRF`, `PostgreSQL`) | Add explicit tech section in report |
| Proposal: scope + exclusions | Missing as artifact | Not found in repo docs | Add scope section in report |
| Normalization to BCNF + FDs + steps | Missing as artifact | Normalized-style schema exists but no written proof | Add full normalization section |
| ERD | Missing as artifact | Relational structure exists in Django models | Draw ERD and include in report |
| 5-6 entities and 8-9 tables (non-toy) | Done (exceeds) | 12+ tables/models in `library/models.py` | None |
| Implement tables | Done | Django models + migrations | None |
| Implement views (DB view) | Done | `vw_unpaid_fines_report` in migration `0007` | None |
| At least one query per user role | Done | `AdminReportView`, `LibrarianReportView`, `MemberReportView` | None |
| Joins | Done | SQL view joins in migration `0007` | None |
| Built-in SQL functions | Partial | Aggregation in ORM (`Count`, `Sum`, `Coalesce`) | Add explicit SQL-function query samples in report |
| Advanced SQL features | Partial | SQL view + grouped reports | Add explicit advanced SQL examples if required by instructor (e.g., CTE/subquery/window) |
| Dynamic user input handling | Done | Query params (`role`, `start_date`, `end_date`, `category_id`, `due_before`, `member_id`) | None |
| Insert / Update / Delete | Done | DRF ModelViewSet CRUD routes | None |
| Transaction handling | Done | `transaction.atomic()` in `BorrowingViewSet.return_book` | None |
| One program/subprogram per role | Partial/Done | Role-specific report endpoints and protected routes | Add explicit demo mapping in report/screenshots |

## High-Priority Fix Applied

To reduce runtime/API issues during demo, serializer field names were corrected to match model fields in `library/serializers.py`:

- `borrow_date` -> `borrowDate`
- `due_date` -> `dueDate`
- `return_date` -> `returnDate`
- `reserved_date` -> `reservedDate`
- `issued_date` -> `issuedDate`

## Submission Readiness

If you submit now, the code quality is strong for implementation marks, but you still risk losing marks on:

1. Missing formal proposal write-up
2. Missing BCNF/FD proof
3. Missing ERD figure
4. Limited explicit "advanced SQL" evidence in report
