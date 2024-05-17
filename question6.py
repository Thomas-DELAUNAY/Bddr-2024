from django.db import connection

def search_emails_by_keywords(keywords):
    with connection.cursor() as cursor:
        sql_query = '''
            SELECT
                em.id AS email_id,
                e1.last_name AS sender_last_name,
                e1.first_name AS sender_first_name,
                e2.last_name AS receiver_last_name,
                e2.first_name AS receiver_first_name,
                em.subject,
                em.content
            FROM
                Email em
            JOIN
                Employee e1 ON em.sender_id = e1.id
            JOIN
                receivers_mail rm ON em.id = rm.email_id
            JOIN
                Employee e2 ON rm.addresse_email_id = e2.id
            WHERE
        '''

        for i in range(len(keywords)):
            if i != 0:
                sql_query += ' OR '
            sql_query += "em.content LIKE %s"
        sql_query += " ORDER BY em.id;"
        
        cursor.execute(sql_query, [f'%{keyword}%' for keyword in keywords])
        

        results = cursor.fetchall()
    
    return results


keywords = ['mot1', 'mot2', 'mot3']  
results = search_emails_by_keywords(keywords)


for row in results:
    print(f"Email ID: {row[0]}, Sender: {row[2]} {row[1]}, Receiver: {row[4]} {row[3]}, Subject: {row[5]}, Content: {row[6]}")
