# ERD/Table Specification (Bookibrary)

Use this section directly in your report and for drawing the ERD.

## Core Entities and Relationships

1. `Member` borrows many `BOOK` records through `Borrowing` (M:N resolved by `Borrowing`)
2. `Member` reserves many `BOOK` records through `Reservation` (M:N resolved by `Reservation`)
3. `Borrowing` has one optional `Fine` (1:1)
4. `Fine` has many `FinePayment` (1:M)
5. `BOOK` belongs to one `Category`, one optional `Author`, and one optional `Publisher` (M:1)
6. `Member` has many `Notification` (1:M)
7. Returned borrowings are archived in `BorrowingHistory`
8. `FinePolicy` defines category-level fine rules (`Category` 1:M `FinePolicy`)

## Table-Level PK/FK Summary

### `library_member`
- **PK:** `id`
- **FK:** `user_id -> auth_user.id` (1:1 by unique one-to-one relation)

### `library_category`
- **PK:** `id`

### `library_author`
- **PK:** `id`

### `library_publisher`
- **PK:** `id`

### `library_book`
- **PK:** `id`
- **Unique:** `isbn`
- **FKs:**  
  - `author_id -> library_author.id`  
  - `publisher_id -> library_publisher.id`  
  - `category_id -> library_category.id`

### `library_borrowing`
- **PK:** `id`
- **FKs:**  
  - `book_id -> library_book.id`  
  - `member_id -> library_member.id`

### `library_reservation`
- **PK:** `id`
- **FKs:**  
  - `book_id -> library_book.id`  
  - `member_id -> library_member.id`

### `library_fine`
- **PK:** `id`
- **FK:** `borrowing_id -> library_borrowing.id` (**unique**, enforcing 1:1)

### `library_finepayment`
- **PK:** `id`
- **FK:** `fine_id -> library_fine.id`

### `library_borrowinghistory`
- **PK:** `id`
- **FKs:**  
  - `book_id -> library_book.id`  
  - `member_id -> library_member.id`

### `library_notification`
- **PK:** `id`
- **FK:** `member_id -> library_member.id`

### `library_finepolicy`
- **PK:** `id`
- **FK:** `category_id -> library_category.id`

## Required SQL View in Current System

- `vw_unpaid_fines_report`
  - Joins `library_fine`, `library_borrowing`, `library_member`, `library_book`
  - Returns unpaid fines by member/book

## Suggested ERD Drawing Notes

- Show crow's-foot cardinalities
- Mark optional FKs (`author_id`, `publisher_id`, `category_id` nullable in code)
- Highlight `library_fine.borrowing_id` as unique to indicate one-to-one with borrowing
