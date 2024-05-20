from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import connection
import re,os

from django.views.generic import ListView

from .models import Employee,AddresseEmail,Email, ReceiversMail, CoupleCommunication
from .forms import * 

import logging

# Configuration du logging
logging.basicConfig(filename='errors_views.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create your views here.

def index(request):
    return render(request, 'home.tmpl')

def page_accueil(request):
    return render(request,"index.tmpl")

def listeEmployees(request):
    listeEmployees = Employee.objects.all().order_by('lastname')
    paginator = Paginator(listeEmployees, 25)  # Show 25 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)  
    return render(request, 'listeEmployes.tmpl',{ 'page_obj' : page_obj})
 
def listeAddresseEmail(request):
    listeAddresseEmail = AddresseEmail.objects.all()
    paginator = Paginator(listeAddresseEmail, 30) 

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)  
    return render(request, 'listeAddresseemail.tmpl',{ 'page_obj' : page_obj})   
 
############# QUESTION 1    

def recherche_employees(request):
    if request.method == 'POST':
        form = EmployeeSearchForm(request.POST)
        if form.is_valid():
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
                
                return render(request, 'detailsEmployee.tmpl', {'employees': employees_with_addresses, 
                                                                'form': form})         
            else :
                return render(request, 'detailsEmployee.tmpl', {'form':form,'error_message': 'Aucun employé correspondant trouvé.'}) 
    else: # Si la méthode request n'est pas POST
        form = EmployeeSearchForm()
    return render(request, 'rechercheEmployee.tmpl', {'form': form})


#### Cette fonction a été ajoutée pour retourner les informations d'un employé depuis n'importe qu'elle autre page de l'application à partir de son addresse mail

def infos_sur_employee(request, addresse_email):
    addresse = addresse_email.split('/')[0]

    try:
        employee = Employee.objects.get(addresseemail__addresse=addresse)
        addresses = AddresseEmail.objects.filter(employee=employee)
        return render(request, 'infos.tmpl', {'employee': employee,
                                             'addresses': addresses})
    except Employee.DoesNotExist: 
        return render(request, 'infos.tmpl', {'error_message':"Aucune information n'est disponible sur cet employé"})
   
                    
############# QUESTION 2

def count_mails(request):
    """ Fonction pour récupérer les employés ayant recu et/ou envoyé plus de (resp. moins de) x mails par rapport aux autres """
    if request.method == 'POST':
        date_debut = request.POST.get('date_debut')
        date_fin = request.POST.get('date_fin')
        nombre_min = request.POST.get('nombre_min')
        nombre_max = request.POST.get('nombre_max')
        
        try:  
            nombre_max = nombre_max if nombre_max  else 100000  
            nombre_min = nombre_min if nombre_min  else 0 
        
            # Compte les mails envoyés et reçus par chaque employé
            query = """
                SELECT addresse, 
                    SUM(total_mails_envoyes_interne_interne) AS total_mails_envoyes_interne_interne,
                    SUM(total_mails_envoyes_interne_externe) AS total_mails_envoyes_interne_externe,
                    SUM(total_mails_recus_interne_interne) AS total_mails_recus_interne_interne,
                    SUM(total_mails_recus_interne_externe) AS total_mails_recus_interne_externe
                FROM (
                    -- total des mails envoyés entre interne et avec les autres
                    SELECT a1.addresse, 
                        SUM(CASE WHEN (a1.estInterne AND a2.estInterne) THEN 1 ELSE 0 END) AS total_mails_envoyes_interne_interne,
                        SUM(CASE WHEN NOT (a1.estInterne AND a2.estInterne) THEN 1 ELSE 0 END) AS total_mails_envoyes_interne_externe,
                        0 AS total_mails_recus_interne_interne,
                        0 AS total_mails_recus_interne_externe
                    FROM investigation_email e
                    INNER JOIN investigation_addresseemail a1 ON a1.id = e.sender_mail_id
                    INNER JOIN investigation_receiversmail_email re ON re.email_id = e.id
                    INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                    INNER JOIN investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                    WHERE a1.estInterne=True AND (a1.addresse=a2.addresse) 
                        AND (e.date BETWEEN %s AND %s)
                    GROUP BY a1.addresse
                    
                    UNION ALL

                    -- total des mails reçus entre interne et avec les autres
                    SELECT a1.addresse, 
                        0 AS total_mails_envoyes_interne_interne,
                        0 AS total_mails_envoyes_interne_externe,
                        SUM(CASE WHEN (a1.estInterne=True AND a2.estInterne=True) THEN 1 ELSE 0 END) AS total_mails_recus_interne_interne,
                        SUM(CASE WHEN (a1.estInterne=True AND a2.estInterne=False)  OR ( a1.estInterne=False AND a2.estInterne=True) THEN 1 ELSE 0 END) AS total_mails_recus_interne_externe
                    FROM investigation_email e
                    INNER JOIN investigation_addresseemail a1 ON a1.id = e.sender_mail_id
                    INNER JOIN investigation_receiversmail_email re ON re.email_id = e.id
                    INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                    INNER JOIN investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                    WHERE a1.estInterne =True AND (a1.addresse != a2.addresse) AND (e.date BETWEEN %s AND %s)
                    GROUP BY a1.addresse    
                ) AS combined
                GROUP BY addresse
                HAVING SUM(total_mails_envoyes_interne_interne + total_mails_envoyes_interne_externe + total_mails_recus_interne_interne + total_mails_recus_interne_externe)  BETWEEN %s AND %s
            """
            # Exécute la requête
            with connection.cursor() as cursor:
                cursor.execute(query, [date_debut, date_fin,date_debut, date_fin, nombre_min, nombre_max])
                resultats= cursor.fetchall()  

            return render(request, 'detailsCountEmails.tmpl', {'date_debut':date_debut,
                                                           'date_fin':date_fin, 
                                                           'nombre_max': nombre_max,
                                                           'nombre_min':nombre_min,
                                                           'resultats':resultats
                                                        })
        except Exception as e:
            logging.error(f"Erreur de type: {e} ")
            return render(request, 'detailsCountEmails.tmpl',{'error_message': "Aucune correspondance n'a été retrouvé pour cet employé à cette période."})
        
    else: # Si la méthode request n'est pas POST
        return render(request, 'countEmails.tmpl')


#############   QUESTION 3

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
    else : # Si la méthode request n'est pas POST
        return render(request, 'rechercheEmployee.tmpl')
 
def dates(request):
    if request.method == 'POST':
        selected_employee_id = request.POST.get('selected_employee')
        try:
            selected_employee = Employee.objects.get(id=selected_employee_id)
            return render(request, 'communicationEmployees.tmpl', {'selected_employee': selected_employee})
        
        except Employee.DoesNotExist:
            messages.error(request,"erreur aucun employé trouvé")
    else: # Si la méthode request n'est pas POST
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
                logging.error("Problème avec le formulaire dans la fonction \'employees_communication\' : %s", form.errors)
                
        except Exception as e:
            logging.error(f"Une erreur s'est produite lors de l'exécution de la requête : {e}")  
            return render(request, 'communicationEmployees.tmpl')       
    else:
        form = CommunicationSearchForm()
    return render(request, 'communicationEmployees.tmpl', {'form': form})   



############# QUESTION 4

def couple_employees_ayant_communique(request):
    if request.method == 'POST':
        form = CoupleEmployeesForm(request.POST)
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut').strftime('%Y-%m-%d')
            date_fin = form.cleaned_data.get('date_fin').strftime('%Y-%m-%d')
            seuil = form.cleaned_data.get('seuil')
            nombre_max = form.cleaned_data.get('nombre_max', 100000000)
            
            try:
                if nombre_max :  
                    query = """
                        SELECT 
                            a1.addresse AS employee_id_1,
                            a2.addresse AS employee_id_2,
                            COUNT(DISTINCT e1.id) AS total_mails_echanges
                        FROM investigation_addresseemail a1
                        INNER JOIN  investigation_email e1 ON a1.id = e1.sender_mail_id
                        INNER JOIN investigation_receiversmail_email re ON re.email_id = e1.id
                        INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                        INNER JOIN  investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                        WHERE e1.date BETWEEN %s AND %s 
                            AND a1.employee_id < a2.employee_id
                        GROUP BY a1.addresse, a2.addresse
                        HAVING COUNT (DISTINCT e1.id) <= %s
                        ORDER BY total_mails_echanges DESC
                    """
                    with connection.cursor() as cursor:
                        cursor.execute(query, [date_debut, date_fin, nombre_max])
                        couple_employees_ayant_communique = cursor.fetchall()

                # Redirection vers la vue CoupleCommunicationView avec les données recupérées
                request.session['Couples'] = couple_employees_ayant_communique
                request.session['seuil'] = seuil
                return redirect('detailsCouples')

            except Exception as e:
                logging.error(f"Erreur survenue : {e}")
                          
        else:
            messages.error(request, "Le formulaire n'est pas valide.")
            logging.error("Problème avec le formulaire dans la fonction \'couple_employees_ayant_communique\' : %s", form.errors)
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
            couple_instance,_ = CoupleCommunication.objects.get_or_create(employee_addresse_1=employee_addresse_1, employee_addresse_2=employee_addresse_2, total_mails_echanges=total_mails_echanges)
            queryset.append(couple_instance)  
        return queryset
    
    def get_context_data(self, **kwargs):
        """ Gère les objets de type paginator """
        context = super().get_context_data(**kwargs)
        context['page_obj'] = context['paginator'].page(context['page_obj'].number)  # Utilisez votre propre nom de variable de contexte ici
        return context
    
    def get_paginate_by(self):  # Utilisez le seuil stocké dans la session pour la pagination
        seuil = self.request.session.get('seuil')
        return seuil if seuil else 10  # Valeur par défaut si le seuil n'est pas défini dans la session


#############    QUESTION 5 

def jour_avec_plus_echanges(request):
    if request.method == 'POST':
        form = SearchDayWithMoreExchangesForm(request.POST)
        if form.is_valid():
            date_debut = form.cleaned_data.get('date_debut').strftime('%Y-%m-%d')
            date_fin = form.cleaned_data.get('date_fin').strftime('%Y-%m-%d')
            
            try:
                # Compte les mails envoyés par jour sur une période
                query = """
                    SELECT DISTINCT e.date,
                        SUM(CASE WHEN (a1.estInterne AND a2.estInterne) THEN 1 ELSE 0 END)  AS total_mails_interne
                    FROM investigation_email e
                    INNER JOIN investigation_addresseemail a1 ON e.sender_mail_id = a1.id
                    INNER JOIN investigation_receiversmail_email re ON re.email_id = e.id
                    INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                    INNER JOIN investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                    WHERE e.date BETWEEN %s AND %s
                    GROUP BY e.date
                    ORDER BY total_mails_interne DESC, e.date
                    LIMIT 15
                """
                # Compte les mails reçus par jour sur une période
                query2= """
                    SELECT DISTINCT e.date,
                        SUM(CASE WHEN (a1.estInterne=True AND a2.estInterne=False)  OR ( a1.estInterne=False AND a2.estInterne=True) THEN 1 ELSE 0 END) AS total_mails_interne_externe
                    FROM investigation_email e
                    INNER JOIN investigation_addresseemail a1 ON e.sender_mail_id = a1.id
                    INNER JOIN investigation_receiversmail_email re ON re.email_id = e.id
                    INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                    INNER JOIN investigation_addresseemail a2 ON a2.id = rm.addresse_email_id
                    WHERE e.date BETWEEN %s AND %s
                    GROUP BY e.date
                    ORDER BY total_mails_interne_externe DESC, e.date
                    LIMIT 15
                """
                with connection.cursor() as cursor:
                    cursor.execute(query, [date_debut, date_fin])
                    echanges_interne = cursor.fetchall() 
                    
                    cursor.execute(query2, [date_debut, date_fin])
                    echanges_externe = cursor.fetchall()
                    
                plot = render_histogram(echanges_interne,echanges_externe)
               
                return render(request,'detailsSearchHotDay.tmpl', {'form':form,
                                                                   'resultats':echanges_interne,
                                                                   'resultats1': echanges_externe
                                                                   })  
            except Exception as e:
                logging.error(f"Erreur survenue: \n {e}")

        else:
            messages.error(request, "Le formulaire n'est pas valide.")
            logging.error("Problème avec le formulaire dans la focntion \'jour_avec_plus_echanges\' : %s", form.errors)
       
    else:
        form = SearchDayWithMoreExchangesForm()
    return render(request,'searchHotDay.tmpl',{'form':form}) 


def render_histogram(liste1, liste2):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    
    dates1 = [item[0].strftime('%Y-%m-%d') for item in liste1]
    dates2 = [item[0].strftime('%Y-%m-%d') for item in liste2]
    
    total_mails_interne1 = [item[1] for item in liste1]
    total_mails_interne_externe2 = [item[1] for item in liste2]

    # Largeur des barres
    bar_width = 0.35

    # Création de la figure et des sous-graphiques
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # Création du premier diagramme en bâtons
    ax1.bar(dates1, total_mails_interne1, color='b', width=bar_width, edgecolor='grey', label='Total mails internes')
    # Création du deuxième diagramme en bâtons
    ax2.bar(dates2, total_mails_interne_externe2, color='r', width=bar_width, edgecolor='grey', label='Total mails internes-externes')

    # Ajout des étiquettes et des titres
    for ax in [ax1, ax2]:
        ax.set_xlabel('Jour', fontweight='bold')
        ax.set_ylabel('Nombre de mails', fontweight='bold')
        ax.legend()
        
    # Ajustement des étiquettes de l'axe x
    ax1.set_xticks(range(len(dates1)))  # Positions des étiquettes
    ax1.set_xticklabels(dates1, rotation=90)  # Étiquettes elles-mêmes et rotation

    ax2.set_xticks(range(len(dates2)))  # Positions des étiquettes
    ax2.set_xticklabels(dates2, rotation=90)  # Étiquettes elles-mêmes et rotation

    # Ajustement automatique de la disposition des sous-graphiques
    plt.tight_layout()
    plt.savefig('./investigation/static/histogramme.png')
    plt.clf()


############# QUESTION 6  

def get_emailIDs(liste):
    return liste.split(",") if liste else []


def afficher_contenu_email(request, email_id):
    try:
        email= Email.objects.get(id=email_id) # Accéder à l'objet Email associé
        
        if est_conversation(email.content): # S'il s'agit d'une conversation, retourne l'ensemble de cette dernière
            return contenu_conversation(request, email_id)
        else: 
            pass #Sinon affiche juste le contenu du message
        
        # Récupérer les destinataires de l'email
        receivers_mail = ReceiversMail.objects.filter(email=email)
        
        # Séparer les destinataires en fonction de leur type
        to_addresses = [rm.addresse_email.addresse for rm in receivers_mail if rm.type == "TO"]
        cc_addresses = [rm.addresse_email.addresse for rm in receivers_mail if rm.type == "CC"]
        bcc_addresses = [rm.addresse_email.addresse for rm in receivers_mail if rm.type =="BCC"]

        return render(request, 'contenuEmail.tmpl', {
            'email': email,
            #'contenu':affiche_contenu,
            'to_addresses': to_addresses,
            'cc_addresses': cc_addresses,
            'bcc_addresses': bcc_addresses
        })
            
    except Email.DoesNotExist as e:
        logging.error(f"Erreur survenue lors de l'affichage du contenu d'un email : \n {e}")
        return render(request, 'contenuEmail.tmpl', {'erreur': 'Le contenu de l\'email n\'existe pas.'})
        

def recherche_par_mots(request):
    if request.method == 'POST':
        form = SearchEmailByWordsForm(request.POST)
        if form.is_valid():
            liste = form.cleaned_data['liste']
            affichage_par = form.cleaned_data['affichage_par']
            
            try:
                mots_cles = [mot.strip() for mot in liste.split(',')]
                
                if mots_cles:
                
                    # Créer une liste de conditions LIKE pour chaque mot de la liste
                    conditions_like = []
                    for mot in mots_cles:
                        condition_like = "content LIKE '%" + mot + "%'"
                        conditions_like.append(condition_like)

                        # Join des conditions LIKE avec l'opérateur OR
                        conditions_combined = " OR ".join(conditions_like)
                    
                    if affichage_par == 'option2': #par destinataire
                        query = f"""
                            SELECT a.addresse, STRING_AGG(CAST(e.id AS VARCHAR), ',') as email_ids
                            FROM investigation_email e
                            INNER JOIN investigation_receiversmail_email re ON re.email_id = e.id
                            INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                            INNER JOIN investigation_addresseemail a ON a.id = rm.addresse_email_id
                            WHERE {conditions_combined}
                            GROUP BY a.addresse
                        """    
                        
                    elif affichage_par == 'option3': # par sujet
                        query = f"""
                            SELECT e.subject, STRING_AGG(CAST(e.id AS VARCHAR), ',') as email_ids
                            FROM investigation_email e
                            INNER JOIN investigation_addresseemail a ON a.id = e.sender_mail_id 
                            WHERE {conditions_combined}
                            GROUP BY e.subject
                        """   
                        
                    elif affichage_par == 'option1':  #par expéditeur
                        query = f"""
                            SELECT a.addresse, STRING_AGG(CAST(e.id AS VARCHAR), ',') as email_ids
                            FROM investigation_email e
                            INNER JOIN investigation_addresseemail a ON a.id = e.sender_mail_id 
                            WHERE {conditions_combined}
                            GROUP BY a.addresse
                        """
                    else:
                       pass
    
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    emails = cursor.fetchall()
                            
                    # Appel de la fonction get_emailIDs pour diviser les identifiants d'email
                    for i, email in enumerate(emails):
                        email = list(email)  # Convertir le tuple en liste
                        email[1] = get_emailIDs(email[1])  # Modifier la liste
                        emails[i] = tuple(email)  # Reconvertir la liste en tuple et mettre à jour la liste de tuple  
                  
                return render(request, 'detailsRechercheParMots.tmpl', {'form': form, 'emails': emails,
                                                                        'filtre':affichage_par})
                    
            except Exception as e:
                logging.error(f'Type d\'erreur survenu: \n{e}')
        else:
            logging.error("Problème avec le formulaire fonction 'recherche_par_mots': %s", form.errors)
    else:
        form = SearchEmailByWordsForm()
    return render(request, 'rechercheParMots.tmpl', {'form': form})


        
############# QUESTION 7

# On entend par conversation tous les emails dans lesquels on retrouve l'expression "-----origin message-----" 
# et tous ceux dans les lesquels on retrouve l'expression "---Forwarded---" ou "--Fwd--" sont des messages transférés


#Pour commencer nos allons trié les emails pour regrouper les conversations, les messages transférés et les messages simples
def get_conversation(email_id):
    query = """
            WITH conversation AS (
                SELECT CASE WHEN em.sender_mail_id < rm.addresse_email_id THEN CONCAT(em.sender_mail_id, '-', rm.addresse_email_id)
                        ELSE CONCAT(rm.addresse_email_id, '-', em.sender_mail_id) END AS conversation_id
                FROM investigation_email em
                INNER JOIN investigation_receiversmail_email re ON re.email_id = em.id
                INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
                WHERE em.id = %s
            )
            SELECT  em.id, em.subject, em.content, em.date
            FROM investigation_email em
            INNER JOIN investigation_receiversmail_email re ON re.email_id = em.id
            INNER JOIN investigation_receiversmail rm ON rm.id = re.receiversmail_id
            WHERE CASE WHEN em.sender_mail_id < rm.addresse_email_id THEN CONCAT(em.sender_mail_id, '-', rm.addresse_email_id)
                       ELSE CONCAT(rm.addresse_email_id, '-', em.sender_mail_id) END IN (SELECT conversation_id FROM conversation)
            ORDER BY em.date;
        """

    with connection.cursor() as cursor:
        cursor.execute(query, [email_id])
        results = cursor.fetchall()
        
    return results

def est_conversation(content):
    # Motifs de séparation pour les messages originaux et transférés
    split_pattern = re.compile(r'(-----Original Message-----|-----Message d\'origine-----|----- Forwarded by|-----Message transféré-----)', re.IGNORECASE)
    return bool(split_pattern.search(content))


def split_email_content(content):
    split_pattern = re.compile(r'(-----Original Message-----|-----Message d\'origine-----|----- Forwarded by|-----Message transféré-----)', re.IGNORECASE)
    parts = split_pattern.split(content) # sépare le contenu en utilisant les motifs trouvés
    
    # Listes pour stocker les messages originaux, transférés et autres
    messages_originaux , messages_transferes,  autres_messages= [], [], []
    
    # Initialisation d'une variable pour stocker le message précédent
    previous_message = ""
    for i, part in enumerate(parts):
        part = part.strip()
        if i % 2 == 1:  # s'il rencontre un séparateur
            previous_message = part
        else:  # s'il rencontre le contenu du message
            if previous_message.lower().startswith('-----original message-----') or previous_message.lower().startswith('-----message d\'origine-----'):
                messages_originaux.append(part)
            elif previous_message.lower().startswith('----- forwarded by') or previous_message.lower().startswith('-----message transféré-----'):
                messages_transferes.append(part)
            else:
                autres_messages.append(part)
            previous_message = ""  # réinitialisation
    return messages_transferes, messages_originaux, autres_messages

def reconstruction_conversation(email_id):
    emails = get_conversation(email_id)
    processed_emails = []
    
    for email in emails:
        email_id, subject, content, date = email
        if est_conversation(content):
            transferes, originaux, autres = split_email_content(content)
            for part in originaux + transferes + autres:
                processed_emails.append((email_id, subject, part, date))
    return list(reversed(processed_emails))


def contenu_conversation(request, email_id):
    subject = Email.objects.get(id=email_id).subject
    conversation = reconstruction_conversation(email_id)
    return render(request, 'detailsConversation.tmpl', {'conversation': conversation,
                                                        'subject':subject})
    
    

   