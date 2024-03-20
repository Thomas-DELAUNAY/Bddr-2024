from django.shortcuts import render
#from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import connection

from .models import Employee,AddresseEmail,Email
from .forms import * 


# Create your views here.
def index(request):
    return render(request, 'home.tmpl')

def listeClients(request):
    return render(request, 'listeEmployes.tmpl', 
        {                                          
            'listeEmployes': Employee.objects.all(),
        })
    

def employee_details(request):
    if request.method == 'POST':
        # Si la méthode de la requête est POST, cela signifie qu'un formulaire a été soumis
        form = EmployeeSearchForm(request.POST)
        if form.is_valid():
            # Si le formulaire est valide, extrayons les données du formulaire
            employee_name_or_email = form.cleaned_data['employee_name_or_email']
            # Recherche des employés dont le nom, prénom ou adresse e-mail correspond à la recherche de l'utilisateur
            employees = Employee.objects.filter(
                Q(lastname__icontains=employee_name_or_email) |
                Q(firstname__icontains=employee_name_or_email) |
                Q(addresseemail__addresse__icontains=employee_name_or_email)
            ).distinct()            
            # Rendu du template avec les résultats de la recherche
            return render(request, 'detailsEmployee.tmpl', {'employees': employees})
    else:
        # Si la méthode de la requête n'est pas POST, initialisons un formulaire vide
        form = EmployeeSearchForm()
    
    # Rendu du template de recherche d'employés avec le formulaire
    return render(request, 'rechercheEmployee.tmpl', {'form': form})
    
def details_about_employee(request, name):
    if request.method == 'GET':
        form = EmployeeSearchForm(request.GET)
        if form.is_valid():
            # Récupérer les données du formulaire
            employee_name_or_email = form.cleaned_data['employee_name_or_email']

            # Construire la requête SQL
            query = """
                SELECT DISTINCT e.id, e.lastname, e.firstname, e.category, ae.addresse
                FROM investigation_employee e
                LEFT JOIN investigation_addresseemail ae ON e.id = ae.employee_id
                WHERE e.lastname ILIKE %s 
                OR e.firstname ILIKE %s
                OR ae.addresse ILIKE %s
            """
            # ILIKE : Dans PostgreSQL, ILIKE est un opérateur qui effectue une recherche de chaîne de caractères insensible à la casse, ce qui signifie qu'il correspondra à des chaînes de caractères indépendamment de la casse (majuscules ou minuscules)

            # Exécuter la requête avec les paramètres
            with connection.cursor() as cursor:
                cursor.execute(query, ['%' + employee_name_or_email + '%', '%' + employee_name_or_email + '%', '%' + employee_name_or_email + '%'])
                employees = cursor.fetchall()

            # Rendre le template avec les résultats de la recherche
            return render(request, 'detailsEmployee.tmpl', {'employees': employees, 'form': form})
    else:
        form = EmployeeSearchForm()
    return render(request, 'rechercheEmployee.tmpl', {'form': form})

# Fonction bonus sans SQL
#def details_employee1(request,name):
#    if request.method == 'GET':
#        form = EmployeeSearchForm(request.GET)
#        employee = get_object_or_404(Employee, )
#        if form.is_valid():
#            return render(request, 'detailsEmployee.tmpl', {'employees': employee})
#    else:
#        form = EmployeeSearchForm()
#    return render(request, 'rechercheEmploye.tmpl', {'form': form})