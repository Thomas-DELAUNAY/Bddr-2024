from django.shortcuts import render
from django.db.models import Q
from django.db import connection
from datetime import date

from .models import Employee,AddresseEmail,Email
from .forms import * 


# Create your views here.
def index(request):
    return render(request, 'home.tmpl')

def listeEmployees(request):
    return render(request, 'listeEmployes.tmpl', 
        {                                          
            'listeEmployes': Employee.objects.all(),
        })
    
     
def details_about_employee(request):
    if request.method == 'POST':
        form = EmployeeSearchForm(request.POST)
        if form.is_valid():
            # Récupère les données du formulaire
            employee_name_or_email = form.cleaned_data['employee_name_or_email']

            # Construit la requête SQL
            query = """
                SELECT DISTINCT e.id, e.lastname, e.firstname, e.category,
                (SELECT array_agg(ae.addresse) 
                FROM investigation_addresseemail ae 
                WHERE ae.employee_id = e.id) AS email_addresses
                FROM investigation_employee e
                WHERE e.lastname ILIKE %s 
                OR e.firstname ILIKE %s
            """
            # ILIKE : Dans PostgreSQL, ILIKE est un opérateur qui effectue une recherche de chaîne de caractères insensible à la casse, ce qui signifie qu'il correspondra à des chaînes de caractères indépendamment de la casse (majuscules ou minuscules)

            # Exécute la requête
            with connection.cursor() as cursor:
                cursor.execute(query, ['%' + employee_name_or_email + '%', '%' + employee_name_or_email + '%'])
                employees = cursor.fetchall()
 
            return render(request, 'detailsEmployee.tmpl', {'employees': employees, 'form': form})
    else:
        form = EmployeeSearchForm()
    return render(request, 'rechercheEmployee.tmpl', {'form': form})


#Fonction pour obtenir les employés ayant échangé avec un en particulier, et sur quelle période?
def employees_communication(request):
    if request.method == 'POST':
        form = CommunicationSearchForm(request.POST)
        employee_id = request.POST.get('selected_employee')
        if form.is_valid():
            date_debut = form.cleaned_data['date_debut'].strftime('%Y-%m-%d')
            date_fin = form.cleaned_data['date_fin'].strftime('%Y-%m-%d')
              
            # Requête SQL
            query = """
                SELECT DISTINCT ae.addresse, em.date
                FROM investigation_employee e
                JOIN investigation_addresseemail ae ON e.id = ae.employee_id
                JOIN investigation_receiversmail rm ON ae.id = rm.addresse_email_id
                JOIN investigation_email em ON em.id = rm.email_id
                JOIN investigation_addresseemail sender ON em.sender_mail_id = sender.id
                WHERE em.date BETWEEN %s AND %s 
           		;
            """

            # Exécution de la requête SQL
            try:
                with connection.cursor() as cursor:
                    cursor.execute(query, [date_debut, date_fin])
                    results = cursor.fetchall()
                    
                    # Structure des résultats en un dictionnaire d'employés avec leurs e-mails associés
                    employees_data = {}
                    for row in results:
                        email, email_date = row
                        if email not in employees_data:
                            employees_data[email] = []
                        employees_data[email].append(email_date.strftime('%Y-%m-%d'))
                        
                    return render(request, 'communicationEmployees.tmpl', {'employees_data': employees_data, 
                                                                           'form': form, 
                                                                           'date_debut':date_debut,
                                                                           'date_fin':date_fin,
                                                                           'employee_id':employee_id})
            except Exception as e:
                print(f"Une erreur s'est produite lors de l'exécution de la requête SQL : {e}")         
    else:
        form = CommunicationSearchForm()
    return render(request, 'communicationEmployees.tmpl', {'form': form})


def search_employee(request):
    employees = set()
    if request.method == 'POST':
        employee_query = request.POST.get('employee', '')

        # Recherchez tous les employés correspondant à la requête
        employees = Employee.objects.filter(
            Q(lastname__icontains=employee_query) |
            Q(firstname__icontains=employee_query) |
            Q(addresseemail__addresse__icontains=employee_query)
        ).distinct()

    return render(request, 'communicationEmployees.tmpl', {'employees': employees})


def dates(request):
    if request.method == 'POST':
        selected_employee_id = request.POST.get('selected_employee')

        try:
            selected_employee = Employee.objects.get(id=selected_employee_id)
            context = {
                'selected_employee': selected_employee
            }
            return render(request, 'communicationEmployees.tmpl', context)
        except Employee.DoesNotExist:
            print("erreur aucun employé trouvé")
 
