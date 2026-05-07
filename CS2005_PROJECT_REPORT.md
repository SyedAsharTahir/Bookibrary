# CS 2005: Database Systems Project Report

## Project Title

**Bookibrary - AI-Enhanced Web-Based Library Management System**

## 1. Introduction and System Description

Bookibrary is a web-based library management system designed to digitize and automate core library operations.  
The system addresses common manual problems such as inconsistent record keeping, difficulty tracking borrowed books, overdue fine mismanagement, and limited reporting visibility for staff.

The project is implemented as a full-stack web application with a SQL-backed relational database.

## 2. System Functionality

The system provides the following core functions:

- Book catalog management (create, update, delete, list books)
- Category, author, and publisher management
- Member registration and account management
- Book borrowing and return workflows
- Reservation handling for members
- Fine generation and fine payment tracking
- Notifications for users
- Role-based dashboards and reporting endpoints

## 3. Users and Role-Based Access

### 3.1 Administrator

- Manage members/users
- Manage system master records (books, categories, authors, publishers)
- Configure fine policy
- Access full administrative reports

### 3.2 Librarian

- Manage day-to-day circulation (borrowing and returns)
- View librarian reports (inventory, due-date and reservation summaries)
- Manage fines and fine payments

### 3.3 Member

- View own borrowing activity and unpaid fines
- Reserve books
- Access member-focused information through protected APIs

## 4. Technologies Used

- **Front-End:** React, JavaScript, Tailwind CSS, Axios
- **Back-End:** Python, Django, Django REST Framework, JWT Authentication
- **Database:** PostgreSQL (SQL)

This satisfies the course requirement of a web application with mandatory SQL database implementation.

## 5. Scope of the System

### In Scope

- Library catalog and member management
- Borrowing, returns, reservations, and fines
- Role-based access control (admin/librarian/member)
- SQL queries, reporting, and database view usage
- CRUD operations and transaction handling

### Out of Scope

- Third-party payment gateway integration
- Multi-branch inter-library operations
- E-book reading or digital rights management

## 6. Assumptions

- Each member has a unique account and email.
- Each borrowing transaction refers to one member and one book.
- Fine rates may depend on category-level policy.
- Only authorized staff can perform operational updates such as returns and fine management.

## 7. Database Design

## 7.1 Main Entities/Tables

The project contains more than the minimum required entity/table count (non-toy design). Core tables include:

1. `library_member`
2. `library_category`
3. `library_author`
4. `library_publisher`
5. `library_book`
6. `library_borrowing`
7. `library_reservation`
8. `library_fine`
9. `library_finepayment`
10. `library_borrowinghistory`
11. `library_notification`
12. `library_finepolicy`

## 7.2 Relationship Summary

- Member and Book: many-to-many via Borrowing
- Member and Book: many-to-many via Reservation
- Borrowing and Fine: one-to-one
- Fine and FinePayment: one-to-many
- Book to Category/Author/Publisher: many-to-one
- Member to Notification: one-to-many

## 8. Normalization (Up to BCNF)

Normalization was applied from an initially denormalized combined relation of member-book-borrow-fine data.

### 8.1 Functional Dependencies (FDs) Used

- `member_id -> member_name, member_email, member_phone`
- `author_id -> author_name`
- `publisher_id -> publisher_name`
- `category_id -> category_name`
- `book_id -> book_title, isbn, author_id, publisher_id, category_id`
- `isbn -> book_id`
- `borrowing_id -> member_id, book_id, borrow_date, due_date, return_date`
- `fine_id -> borrowing_id, fine_amount, fine_paid, issued_date`
- `reservation_id -> member_id, book_id, reserved_date, status`

### 8.2 Steps

- **1NF:** ensured atomic attributes.
- **2NF:** removed partial dependencies by splitting member/book data from transaction data.
- **3NF:** removed transitive dependencies by separating category/author/publisher.
- **BCNF:** ensured each determinant in non-trivial FD is a candidate key or superkey in decomposed relations.

The resulting schema avoids insertion, update, and deletion anomalies and is BCNF-compliant for project scope.

## 9. E-R Diagram

The ERD is derived from the implemented Django models and FK/PK constraints.  
The submitted ERD should include:

- All core entities listed in Section 7.1
- PK/FK markers
- Cardinalities (1:1, 1:M, M:N via junction/transaction tables)
- Unique constraint on Fine -> Borrowing mapping

Reference schema notes are prepared in `ERD_SCHEMA_SPEC.md`.

## 10. Implementation Phase Evidence

## 10.1 Tables

Implemented via Django models and migrations in the `library` app.

## 10.2 Views

Implemented SQL view:

- `vw_unpaid_fines_report`

Purpose: returns unpaid fines using joins between fine, borrowing, member, and book tables.

## 10.3 Queries per User Role

Role-specific API query endpoints are implemented:

- **Admin:** `/api/reports/admin/`
- **Librarian:** `/api/reports/librarian/`
- **Member:** `/api/reports/member/`

These endpoints support dynamic user inputs through query parameters (for example role/date/category/member filters).

## 10.4 SQL Features Coverage

Implemented/used in project:

- Joins (in SQL view and related report retrieval)
- Aggregate functions (`COUNT`, `SUM`)
- Null-safe aggregation (`COALESCE`)
- Sorting and filtering
- Dynamic user input handling through API query params

## 10.5 CRUD Operations

Implemented through DRF ViewSets for books, members, borrowing, reservations, fines, categories, authors, publishers, notifications, fine policies, and fine payments.

## 10.6 Transaction Handling

Book return operation uses atomic transaction control:

- compute overdue fine
- archive borrowing to history
- restore book quantity
- delete active borrowing

All steps are executed in a single `transaction.atomic()` block to ensure consistency.

## 11. AI Integration Module

To align the system with AI course requirements, an AI-powered recommendation module was integrated into the existing database project.

### 11.1 AI Objective

Recommend books to users based on their past borrowing patterns and content similarity.

### 11.2 AI Method Used

The implemented method is a **hybrid recommender**:

- **Content-based component:** higher score for books matching categories/authors frequently seen in the member's borrowing data.
- **Collaborative component:** user-to-user similarity is computed with cosine similarity on category interaction vectors.
- **Hybrid ranking:** final score combines content score and collaborative score, with popularity as a tie-break signal.
- Already seen/borrowed books are excluded from recommendations.
- If no useful history exists, the system falls back to globally popular available books.

### 11.3 AI Endpoint and Integration

- Backend API endpoint: `/api/recommendations/`
- Optional parameters: `limit`, `member_id` (role-aware access)
- Frontend page: `/recommendations` (shown in sidebar as **AI Recs**)
- Response includes ranked list with `ai_score`, `popularity`, and book metadata.

### 11.4 AI Performance Evaluation Plan

The recommendation module can be evaluated using:

- Precision@K (how many suggested books are later borrowed)
- Recall@K
- Click/selection rate on recommended books
- Average API response time per recommendation request
- User-level qualitative feedback on recommendation relevance

## 12. Mapping to Project Requirements

- Web app: satisfied
- SQL DB: satisfied
- Non-toy schema size: satisfied
- Tables and views: satisfied
- Joins and SQL functions: satisfied
- Role-based queries: satisfied
- Dynamic input: satisfied
- Insert/update/delete: satisfied
- Transaction handling: satisfied
- Proposal + normalization + ERD documentation: provided in report and companion files

## 13. Conclusion

Bookibrary fulfills the technical implementation goals of the CS 2005 database project with a practical, role-based web application built on a normalized SQL schema.  
The system demonstrates complete CRUD operations, SQL view/query usage, transactional integrity, and practical AI integration through personalized book recommendations.
