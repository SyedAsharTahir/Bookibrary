# Normalization and BCNF (Bookibrary)

## 1) Initial Unnormalized Relation (UNF)

Consider a combined transaction-style relation:

`R(member_id, member_name, member_email, member_phone, book_id, book_title, isbn, author_id, author_name, publisher_id, publisher_name, category_id, category_name, borrow_date, due_date, return_date, fine_amount, fine_paid, reservation_status)`

This mixes member, book, loan, reservation, and fine data in one place.

## 2) Functional Dependencies (FDs)

Key dependencies used for normalization:

1. `member_id -> member_name, member_email, member_phone`
2. `author_id -> author_name`
3. `publisher_id -> publisher_name`
4. `category_id -> category_name`
5. `book_id -> book_title, isbn, author_id, publisher_id, category_id`
6. `isbn -> book_id` (ISBN is unique)
7. `borrowing_id -> member_id, book_id, borrow_date, due_date, return_date, returned`
8. `fine_id -> borrowing_id, fine_amount, fine_paid, issued_date`
9. `reservation_id -> member_id, book_id, reserved_date, reservation_status`
10. `notification_id -> member_id, message, type, is_read, created_date`

## 3) 1NF

All attributes are atomic (no repeating groups/lists per column).  
Move repeated multi-value data into separate tuples if present.

## 4) 2NF

If we assume a composite key in a transaction table (for example `(member_id, book_id, borrow_date)`), partial dependencies exist:

- `member_id -> member_name, member_email, member_phone`
- `book_id -> book_title, isbn, author_id, publisher_id, category_id`

Decompose to remove partial dependencies:

- `MEMBER(member_id, member_name, member_email, member_phone, role, joined_date, user_id)`
- `BOOK(book_id, book_title, isbn, quantity, published_date, author_id, publisher_id, category_id)`
- `BORROWING(borrowing_id, member_id, book_id, borrow_date, due_date, return_date, returned)`

## 5) 3NF

Transitive dependencies in `BOOK`:

- `book_id -> category_id -> category_name`
- `book_id -> author_id -> author_name`
- `book_id -> publisher_id -> publisher_name`

Decompose transitive attributes into separate lookup/master tables:

- `CATEGORY(category_id, category_name, description)`
- `AUTHOR(author_id, author_name, biography)`
- `PUBLISHER(publisher_id, publisher_name, address)`

Keep only FKs in `BOOK`.

## 6) BCNF Check

A relation is in BCNF if every non-trivial FD `X -> Y` has `X` as a superkey.

Final core relations satisfy BCNF:

- `MEMBER(member_id PK, ...)`
- `CATEGORY(category_id PK, ...)`
- `AUTHOR(author_id PK, ...)`
- `PUBLISHER(publisher_id PK, ...)`
- `BOOK(book_id PK, isbn UNIQUE, author_id FK, publisher_id FK, category_id FK, ...)`
- `BORROWING(borrowing_id PK, book_id FK, member_id FK, ...)`
- `FINE(fine_id PK, borrowing_id UNIQUE FK, amount, paid, issued_date)`
- `RESERVATION(reservation_id PK, member_id FK, book_id FK, status, reserved_date)`
- `BORROWING_HISTORY(history_id PK, member_id FK, book_id FK, borrow_date, due_date, return_date, fine_charged)`
- `NOTIFICATION(notification_id PK, member_id FK, ...)`
- `FINE_POLICY(policy_id PK, category_id FK, fine_per_day, max_fine_days, created_at)`
- `FINE_PAYMENT(payment_id PK, fine_id FK, amount_paid, payment_date, method)`

## 7) Conclusion

The schema decomposition removes update, insert, and delete anomalies and reaches BCNF for practical project requirements.
