from django.db import connection
from datetime import datetime

def get_employee_email_interactions(start_date, end_date, threshold):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT 
                e1.id AS employee1_id,
                e1.last_name AS employee1_last_name,
                e1.first_name AS employee1_first_name,
                e2.id AS employee2_id,
                e2.last_name AS employee2_last_name,
                e2.first_name AS employee2_first_name,
                COUNT(*) AS number_of_emails
            FROM 
                Employee e1
            JOIN 
                Email em ON e1.id = em.sender_id
            JOIN 
                receivers_mail rm ON em.id = rm.email_id
            JOIN 
                Employee e2 ON rm.address_email_id = e2.id
            WHERE 
                em.date_send BETWEEN %s AND %s
            GROUP BY 
                e1.id, e1.last_name, e1.first_name, e2.id, e2.last_name, e2.first_name
            HAVING 
                COUNT(*) > %s
            ORDER BY 
                number_of_emails DESC;
        ''', [start_date, end_date, threshold])
        
        results = cursor.fetchall()
    
    for row in results:
        print(f"Employee 1 ID: {row[0]}, Last Name: {row[1]}, First Name: {row[2]}, "
              f"Employee 2 ID: {row[3]}, Last Name: {row[4]}, First Name: {row[5]}, "
              f"Number of Emails: {row[6]}")

# Utilisation de la fonction
start_date = '2001-01-01'
end_date = '2001-12-31'
threshold = 50

get_employee_email_interactions(start_date, end_date, threshold)