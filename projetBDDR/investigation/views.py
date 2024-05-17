from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
from django.http import HttpResponse

from django.views.generic import ListView

from .models import Employee,AddresseEmail,Email, ReceiversMail, CoupleCommunication
from .forms import * 

import logging

# Configuration du logging
logging.basicConfig(filename='errors_views.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create your views here.

def index(request):
    return render(request, 'home.tmpl')

def listeEmployees(request):
    listeEmployees = ReceiversMail.objects.all()
    paginator = Paginator(listeEmployees, 25)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)  
    return render(request, 'listeEmployes.tmpl',{ 'page_obj' : page_obj})
 
def listeEmails(request):
    listeEmployees = Email.objects.all()
    paginator = Paginator(listeEmployees, 25)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)  
    return render(request, 'listeEmails.tmpl',{ 'page_obj' : page_obj})   
 
#### QUESTION 1    

def details_about_employee(request):
    if request.method == 'POST':
        form = EmployeeSearchForm(request.POST)
        if form.is_valid():
            # Récupère les données du formulaire
            data = form.cleaned_data['employee_name_or_email']
            
            employees = Employee.objects.filter(
                    Q(lastname__icontains=data) |
                    Q(firstname__icontains=data) |
                    Q(addresseemail__addresse__icontains=data)
                ).distinct()
            
            if employees:
                employees_with_addresses = {}
                
                # Récupère les adresses e-mail associées à l'employé
                addresses = AddresseEmail.objects.filter(employee__in=employees)
                
                for employee in employees:
                    addresses = AddresseEmail.objects.filter(employee=employee)
                    employees_with_addresses[employee] = addresses
                
                return render(request, 'rechercheEmployee.tmpl', {'employees': employees_with_addresses, 'form': form})
                    
            else :
                return render(request, 'rechercheEmployee.tmpl', {'form':form,'error_message': 'Aucun employé correspondant trouvé.'})
                
    else:
        form = EmployeeSearchForm()
    return render(request, 'rechercheEmployee.tmpl', {'form': form})


###### QUESTION 2

def count_mails(request):
    """ Fonction pour récupérer les employés ayant recu et/ou envoyé plus de (resp. moins de) x mails par rapport aux autres """
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        nombre_min = request.POST.get('nombre_min')
        nombre_max = request.POST.get('nombre_max')
        
        try: 
            
            nombre_max = nombre_max if nombre_max  else 0  
            nombre_min = nombre_min if nombre_min  else 0 
            
            # Compte les mails envoyés et reçus par chaque employé
            query = """
                SELECT addresse, 
                    SUM(total_mails_envoyes_interne) AS total_mails_envoyes_interne,
                    SUM(total_mails_envoyes_externe) AS total_mails_envoyes_externe
                FROM (
                    SELECT a.addresse, 
                        COUNT(DISTINCT e.id) AS total_mails_envoyes_interne,
                        0 AS total_mails_envoyes_externe
                    FROM investigation_addresseemail a
                    INNER JOIN investigation_email e ON a.id = e.sender_mail_id
                    WHERE a.estInterne = True
                        AND e.date BETWEEN %s AND %s
                    GROUP BY a.addresse
                    HAVING COUNT(DISTINCT e.id) BETWEEN %s AND %s
                    
                    UNION ALL
                    
                    SELECT a.addresse, 
                        0 AS total_mails_envoyes_interne,
                        COUNT(DISTINCT e.id) AS total_mails_envoyes_externe
                    FROM investigation_addresseemail a
                    INNER JOIN investigation_email e ON a.id = e.sender_mail_id
                    WHERE a.estInterne = False
                        AND e.date BETWEEN %s AND %s
                    GROUP BY a.addresse
                    HAVING COUNT(DISTINCT e.id) BETWEEN %s AND %s
                ) AS combined_results
                GROUP BY addresse
                ORDER BY total_mails_envoyes_interne DESC
            """
            
            query1 = """
                SELECT addresse, 
                    SUM(total_mails_recus_interne) AS total_mails_recus_interne,
                    SUM(total_mails_recus_externe) AS total_mails_recus_externe
                FROM (
                    SELECT a.addresse, 
                        COUNT(DISTINCT e.id) AS total_mails_recus_interne,
                        0 AS total_mails_recus_externe
                    FROM investigation_addresseemail a
                    INNER JOIN investigation_receiversmail r ON a.id = r.addresse_email_id
                    INNER JOIN investigation_receiversmail_email re ON re.receiversmail_id  = r.id
                    INNER JOIN investigation_email e ON  e.id = re.email_id
                    WHERE a.estInterne = True
                        AND e.date BETWEEN %s AND %s
                    GROUP BY a.addresse
                    HAVING COUNT(DISTINCT e.id) BETWEEN %s AND %s
                      
                    UNION ALL
                    
                    SELECT a.addresse, 
                        0 AS total_mails_recus_interne,
                        COUNT(DISTINCT e.id) AS total_mails_recus_externe
                    FROM investigation_addresseemail a
                    INNER JOIN investigation_receiversmail r ON a.id = r.addresse_email_id
                    INNER JOIN investigation_receiversmail_email re ON re.receiversmail_id  = r.id
                    INNER JOIN investigation_email e ON  e.id = re.email_id
                    WHERE a.estInterne = False
                        AND e.date BETWEEN %s AND %s
                    GROUP BY a.addresse
                    HAVING COUNT(DISTINCT e.id) BETWEEN %s AND %s
                ) AS received_results
                GROUP BY addresse
                ORDER BY total_mails_recus_interne DESC
            """
            
            # Exécute la requête
            with connection.cursor() as cursor:
                cursor.execute(query, [date_debut, date_fin, nombre_min, nombre_max,
                                       date_debut, date_fin, nombre_min, nombre_max])
                employes_avec_plus_de_x_mails = cursor.fetchall()
                
                cursor.execute(query1, [date_debut, date_fin, nombre_min, nombre_max,
                                        date_debut, date_fin, nombre_min, nombre_max])
                employes_avec_plus_de_x = cursor.fetchall()                     

            
            return render(request, 'detailsCountEmails.tmpl', {'date_debut':date_debut,
                                                           'date_fin':date_fin, 
                                                           'nombre_max': nombre_max,
                                                           'nombre_min':nombre_min,
                                                           'plus_de_x_mails_envoyes': employes_avec_plus_de_x_mails,
                                                           'plus_de_x_mails_recus': employes_avec_plus_de_x})
        except Exception as e:
            print(f" Erreur de type : \n {e}")
            return HttpResponse("Une erreur s'est produite lors du traitement de votre demande.")
    else: 
        print(" Erreur Erreur Erreur ")
        return render(request, 'countEmails.tmpl')


########   QUESTION 3

def search_employee(request):
    if request.method == 'POST':
        employee= request.POST.get('employee', '')
        try: 
            # Recherche tous les employés correspondant à la requête
            employees = Employee.objects.filter(
                Q(lastname__icontains=employee) |
                Q(firstname__icontains=employee) |
                Q(addresseemail__addresse__icontains=employee)
            ).distinct()
            return render(request, 'communicationEmployees.tmpl', {'employees': employees,
                                                                   'error_message': 'Aucun employé correspondant trouvé.'})
        
        except Exception as e:
            print(f" Erreur détectée : {e}")
    else :
        return render(request, 'rechercheEmployee.tmpl', {'error_message': 'Aucun employé correspondant trouvé.'})
 
def dates(request):
    if request.method == 'POST':
        selected_employee_id = request.POST.get('selected_employee')
        try:
            selected_employee = Employee.objects.get(id=selected_employee_id)
            return render(request, 'communicationEmployees.tmpl', {'selected_employee': selected_employee})
        
        except Employee.DoesNotExist:
            messages.error(request,"erreur aucun employé trouvé")
    else: # Si la méthode de la requête n'est pas POST
        return render(request, 'communicationEmployees.tmpl')
            
def employees_communication(request):
    """ Fonction pour obtenir les employés ayant échangé avec un autre en particulier, et sur quelle période """
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', None)
        form = CommunicationSearchForm(request.POST)
        
        try:
            if form.is_valid():
                date_debut = form.cleaned_data['date_debut'].strftime('%d/%m/%Y') 
                date_fin = form.cleaned_data['date_fin'].strftime('%d/%m/%Y') 
                
                if employee_id is not None:
                    employee = Employee.objects.get(pk=employee_id)
                     
                    # Requete SQL
                    
                    query="""
                        SELECT DISTINCT rm.type, ae.addresse, e.date
                        FROM investigation_receiversmail rm
                        INNER JOIN investigation_receiversmail_email re ON re.receiversmail_id = rm.id
                        INNER JOIN investigation_email e ON e.id = re.email_id 
                        INNER JOIN investigation_addresseemail ae ON ae.id = e.sender_mail_id
                        WHERE e.date BETWEEN %s AND %s
                        AND e.sender_mail_id NOT IN (
                            SELECT a.id
                            FROM investigation_addresseemail a
                            WHERE a.employee_id = %s
                        )
                        """
                        
                    # Exécute la requête
                    with connection.cursor() as cursor:
                        cursor.execute(query, [date_debut, date_fin, employee.id])
                        employees = cursor.fetchall()
                   
                        
                    return render(request, 'detailsCommunication.tmpl', {'employees': employees,
                                                                            'form': form,
                                                                            'date_debut':date_debut,
                                                                            'date_fin':date_fin,
                                                                            'employee_id':employee,
                                                                            
                                                                            })
            else:
                messages.error(request, "Le formulaire n'est pas valide.")
                logging.error("Problème avec le formulaire : %s", form.errors)
                
        except Exception as e:
            logging.error(f"Une erreur s'est produite lors de l'exécution de la requête : {e}")  
            return render(request, 'communicationEmployees.tmpl')       
    else:
        form = CommunicationSearchForm()
    return render(request, 'communicationEmployees.tmpl', {'form': form})   


###### QUESTION 4

def couple_employees_ayant_communique(request):
    if request.method == 'POST':
        form = CoupleEmployeesForm(request.POST)
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut').strftime('%Y-%m-%d')
            date_fin = form.cleaned_data.get('date_fin').strftime('%Y-%m-%d')
            seuil = form.cleaned_data.get('seuil')
            nombre_max = form.cleaned_data.get('nombre_max', None)
            
            try:
                if nombre_max :
                    query = """
                        SELECT 
                            a1.addresse AS employee_id_1,
                            a2.addresse AS employee_id_2,
                            COUNT(*) AS total_mails_echanges
                        FROM 
                            investigation_addresseemail a1
                        INNER JOIN 
                            investigation_email e1 ON a1.id = e1.sender_mail_id
                        INNER JOIN
                            investigation_receiversmail_email re ON re.email_id = e1.id
                        INNER JOIN
                            investigation_receiversmail rm ON rm.id = re.receiversmail_id
                        INNER JOIN 
                            investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                        WHERE 
                            e1.date BETWEEN %s AND %s
                            AND a1.employee_id < a2.employee_id
                        GROUP BY 
                            a1.addresse, a2.addresse
                        HAVING
                            COUNT(*) <= %s
                        ORDER BY total_mails_echanges DESC
                    """
                    with connection.cursor() as cursor:
                        cursor.execute(query, [date_debut, date_fin, nombre_max])
                        couple_employees_ayant_communique = cursor.fetchall()
                    
                else:
                    query = """
                        SELECT 
                            a1.addresse AS employee_id_1,
                            a2.addresse AS employee_id_2,
                            COUNT(*) AS total_mails_echanges
                        FROM 
                            investigation_addresseemail a1
                        INNER JOIN 
                            investigation_email e1 ON a1.id = e1.sender_mail_id
                        INNER JOIN
                            investigation_receiversmail_email re ON re.email_id = e1.id
                        INNER JOIN
                            investigation_receiversmail rm ON rm.id = re.receiversmail_id
                        INNER JOIN 
                            investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                        WHERE 
                            e1.date BETWEEN %s AND %s
                            AND a1.employee_id < a2.employee_id
                        GROUP BY 
                            a1.addresse, a2.addresse
                        
                        ORDER BY total_mails_echanges DESC
                    """
                    
                    with connection.cursor() as cursor:
                        cursor.execute(query, [date_debut, date_fin])
                        couple_employees_ayant_communique = cursor.fetchall()

                # Rediriger vers la vue CoupleCommunicationView avec les données
                request.session['Couples'] = couple_employees_ayant_communique
                request.session['seuil'] = seuil
                return redirect('detailsCouples')

            except Exception as e:
                logging.error(f"Erreur survenue : {e}")
                          
        else:
            messages.error(request, "Le formulaire n'est pas valide.")
            logging.error("Problème avec le formulaire : %s", form.errors)
    else:
        form = CoupleEmployeesForm()
    return render(request, 'coupleEmployees.tmpl', {'form': form})

class CoupleCommunicationView(ListView):
    """ Cette classe gère la pagination  dans mon template, les méthodes sont appelées directement """
    model = CoupleCommunication
    template_name = 'detailsCoupleEmployees.tmpl'
    context_object_name = 'Couples'

    def get_queryset(self):
        """ Cette methode transforme le résultat de ma requete SQL en queryset, utilisable par cette classe"""
        couples = self.request.session.get('Couples', [])
        queryset = []
        for couple in couples:
            employee_addresse_1, employee_addresse_2, total_mails_echanges = couple
            couple_instance = CoupleCommunication(employee_addresse_1=employee_addresse_1, employee_addresse_2=employee_addresse_2, total_mails_echanges=total_mails_echanges)
            queryset.append(couple_instance)  
        return queryset
    
    def get_context_data(self, **kwargs):
        """ Gère les objets de type paginator """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context['paginator'].page(context['page_obj'].number)  # Utilisez votre propre nom de variable de contexte ici
        return context
    
    def get_paginate_by(self, queryset):  # Utilisez le seuil stocké dans la session pour la pagination
        seuil = self.request.session.get('seuil')
        return seuil if seuil else 10  # Valeur par défaut si le seuil n'est pas défini dans la session


###### QUESTION 5


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
start_date = '2000-01-01'
end_date = '2001-12-31'
limit = 10

get_top_days_with_most_emails(start_date, end_date, limit)

###### QUESTION 6

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

###### QUESTION 7


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
