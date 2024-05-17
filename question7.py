from django.db import connection

def get_emails_in_conversation(email_id):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT
                em.id AS email_id,
                e1.last_name AS sender_last_name,
                e1.first_name AS sender_first_name,
                em.subject,
                em.content
            FROM
                Email em
            JOIN
                Employee e1 ON em.sender_id = e1.id
            JOIN
                (
                    SELECT DISTINCT
                        conversation_id
                    FROM
                        (
                            SELECT
                                CASE
                                    WHEN sender_id < receiver_id THEN CONCAT(sender_id, '-', receiver_id)
                                    ELSE CONCAT(receiver_id, '-', sender_id)
                                END AS conversation_id
                            FROM
                                (
                                    SELECT
                                        sender_id,
                                        adresse_id AS receiver_id
                                    FROM
                                        Email em
                                    JOIN
                                        receivers_mail rm ON em.id = rm.email_id
                                    WHERE
                                        em.id = %s
                                ) AS conversation_participants
                        ) AS conversation_ids
                ) AS conversation ON em.id = conversation_id
            ORDER BY
                em.date_send;
        ''', [email_id])
        
        results = cursor.fetchall()
    
    return results


email_id = 'ID_du_mail_donné'  
results = get_emails_in_conversation(email_id)


for row in results:
    print(f"Email ID: {row[0]}, Sender: {row[2]} {row[1]}, Subject: {row[3]}, Content: {row[4]}")
