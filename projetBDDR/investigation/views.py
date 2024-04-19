from django.shortcuts import render
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.db import connection

from .models import Employee,AddresseEmail,Email, ReceiversMail
from .forms import * 


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


#Fonction pour obtenir les employés ayant échangé avec un autre en particulier, et sur quelle période

def employees_communication(request):
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id', None)

        form = CommunicationSearchForm(request.POST)
        try:
            if form.is_valid():
                date_debut = form.cleaned_data['date_debut'].strftime('%Y-%m-%d')
                date_fin = form.cleaned_data['date_fin'].strftime('%Y-%m-%d')
                
                if employee_id is not None:
                
                    employee = Employee.objects.get(pk=employee_id)
                        
                        # Requete SQL
                    query="""
                            -- Combine les adresses des e-mails envoyés et reçus par cet employé
                            
                            -- Toutes les addresses emails des messages que l'employé a envoyé
                            SELECT DISTINCT em.date, rm.type, ae.addresse
                            FROM investigation_addresseemail ae
                            JOIN investigation_email em ON ae.id = em.sender_mail_id
                            JOIN investigation_receiversmail rm ON em.id = rm.email_id
                            JOIN investigation_addresseemail recipient_ae ON rm.addresse_email_id = recipient_ae.id
                            JOIN investigation_employee recipient_e ON recipient_ae.employee_id = recipient_e.id
                            JOIN investigation_employee sender_e ON ae.employee_id = sender_e.id
                            WHERE sender_e.lastname ILIKE %s AND sender_e.firstname ILIKE %s
                            
                            UNION
                            
                            
                            -- Ici on a tous les destinataires des emails envoyés par 
                            SELECT  DISTINCT  em.date, rm.type, ae.addresse
                            FROM investigation_addresseemail ae
                            JOIN investigation_receiversmail rm ON ae.id = rm.addresse_email_id
                            JOIN investigation_email em ON rm.email_id = em.id
                            JOIN investigation_addresseemail sender ON em.sender_mail_id = sender.id
                            JOIN investigation_employee e ON sender.employee_id = e.id
                            WHERE e.lastname NOT ILIKE %s AND e.firstname  NOT ILIKE %s
                            AND em.date >= %s AND em.date <= %s
                        """

                        # Exécute la requête
                    with connection.cursor() as cursor:
                        cursor.execute(query, ['%' + employee.lastname + '%', '%' + employee.firstname + '%', 
                                                '%' + employee.lastname + '%', '%' + employee.firstname + '%',
                                                '%'+ date_debut + '%' , '%' + date_fin + '%'])
                        employees = cursor.fetchall()
                            
                        # Récupérer toutes les adresses e-mails où l'employé est destinataire en TO, CC ou BCC

                        
                    return render(request, 'detailsCommunication.tmpl', {'employees_data': employees,
                                                                            'form': form,
                                                                            'date_debut':date_debut,
                                                                            'date_fin':date_fin,
                                                                            'employee_id':employee,
                                                                            
                                                                            })
            else:
                print("problème de formulaire ")    
                
        except Exception as e:
            print(f"Une erreur s'est produite lors de l'exécution de la requête : {e}")         
    else:
        form = CommunicationSearchForm()
    return render(request, 'communicationEmployees.tmpl', {'form': form})   



def search_employee(request):
    employees = set()
    if request.method == 'POST':
        employee= request.POST.get('employee', '')
        
        try: 

            # Recherchez tous les employés correspondant à la requête
            employees = Employee.objects.filter(
                Q(lastname__icontains=employee) |
                Q(firstname__icontains=employee) |
                Q(addresseemail__addresse__icontains=employee)
            ).distinct()
            
            return render(request, 'communicationEmployees.tmpl', {'employees': employees})
        except Exception as e:
            print(f" Erreur détectée : {e}")
        
    else :
        return render(request, 'rechercheEmployee.tmpl', {'error_message': 'Aucun employé correspondant trouvé.'})
            


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
    # Si la méthode de la requête n'est pas POST, renvoyer simplement un rendu de template vide
    return render(request, 'communicationEmployees.tmpl')
 
 
# Fonction pour récupérer les employés ayant recu et/ou envoyé plus de (resp.moins de) mails que les autres.

def count_mails(request):
    if request.method == 'POST':
        form = CountEmailsForm(request.POST)

        if form.is_valid():
            date_debut = request.POST.get('date_debut', None)
            date_fin = request.POST.get('date_fin', None)
            nombre_min = request.POST.get('nombre_min', None)
            nombre_max = request.POST.get('nombre_max', None)

            # Compter les mails envoyés et reçus par chaque employé
            employes_avec_plus_de_x_mails = Employee.objects.annotate(
                total_mails_envoyes=Count('sent_emails', distinct=True),
                total_mails_recus=Count('received_emails', distinct=True)
            ).filter(
                total_mails_envoyes__gt=nombre_max,
                total_mails_recus__gt=nombre_max,
                total_mails_envoyes__lt=nombre_min,
                total_mails_recus__lt=nombre_min,
                sent_emails__date__range=(date_debut, date_fin),
                received_emails__date__range=(date_debut, date_fin),
            )

            employes_avec_moins_de_x_mails = Employee.objects.annotate(
                total_mails_envoyes=Count('sent_emails', distinct=True),
                total_mails_recus=Count('received_emails', distinct=True)
            ).filter(
                total_mails_envoyes__lt=nombre_max,
                total_mails_recus__lt=nombre_max,
                total_mails_envoyes__gt=nombre_min,
                total_mails_recus__gt=nombre_min,
                sent_emails__date__range=(date_debut, date_fin),
                received_emails__date__range=(date_debut, date_fin),
            )

            return render(request, 'detailsCountEmails.tmpl', {
                'form': form,
                'employes_avec_plus_de_x_mails': employes_avec_plus_de_x_mails,
                'employes_avec_moins_de_x_mails': employes_avec_moins_de_x_mails,
                'date_debut': date_debut,
                'date_fin': date_fin,
                'nombre_max': nombre_max,
                'nombre_min': nombre_min
            })
        else:
            print("le format du formulaire n'est pas valide ")
    else:
        form = CountEmailsForm()
    return render(request, 'countEmails.tmpl', {'form': form})

def dates2(request):
    
    
    
    return render(request, 'detailsCountEmails.tmpl')

 