from django.db import connection
from datetime import datetime

def get_top_days_with_most_emails(start_date, end_date, limit=10):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                DATE(em.date_send) AS email_date,
                COUNT(CASE WHEN em.estInterne = 'internal' THEN 1 ELSE NULL END) AS internal_emails,
                COUNT(CASE WHEN em.estInterne != 'internal' THEN 1 ELSE NULL END) AS external_emails,
                COUNT(*) AS total_emails
            FROM
                Email em
            WHERE
                em.date_send BETWEEN %s AND %s
            GROUP BY
                email_date
            ORDER BY
                total_emails DESC
            LIMIT %s;
        ''', [start_date, end_date, limit])
        
        results = cursor.fetchall()
    
    if results:
        for result in results:
            print(f"Date: {result[0]}, Internal Emails: {result[1]}, External Emails: {result[2]}, Total Emails: {result[3]}")
    else:
        print("No data found for the given period.")

# Utilisation de la fonction
start_date = '2024-01-01'
end_date = '2024-12-31'
limit = 10

get_top_days_with_most_emails(start_date, end_date, limit)
