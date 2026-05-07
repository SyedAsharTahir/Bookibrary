from django.db import migrations


VIEW_SQL = """
CREATE VIEW vw_unpaid_fines_report AS
SELECT
    m.id AS member_id,
    m.name AS member_name,
    b.title AS book_title,
    f.amount AS fine_amount,
    f."issuedDate" AS issued_date
FROM library_fine f
JOIN library_borrowing br ON f.borrowing_id = br.id
JOIN library_member m ON br.member_id = m.id
JOIN library_book b ON br.book_id = b.id
WHERE f.paid = FALSE;
"""


DROP_VIEW_SQL = "DROP VIEW IF EXISTS vw_unpaid_fines_report;"


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0006_author_publisher_alter_notification_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=VIEW_SQL,
            reverse_sql=DROP_VIEW_SQL,
        ),
    ]
