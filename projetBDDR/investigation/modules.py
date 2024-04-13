import re,os
from django.db.utils import IntegrityError
from django.db import transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from dateutil.parser import parse

import xml.etree.ElementTree as ET
from multiprocessing import Pool # pour optimiser le temps d'exécution du programme

import logging
# Configuration du logging
logging.basicConfig(filename='errors_daily.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Import des modèles 
from .models import Employee,AddresseEmail,ReceiversMail,Email



# Fonction pour extraire toutes les adresses email d'une instance 'employee' du fichier xml
def extract_emails(employee):
    emails = [] # pour stocker toutes les adresses mails d'un employé
    for email_tag in employee.findall('email'):
        address = email_tag.get('address')
        if address:
            emails.append(address)
    return emails  

#Fonction pour traiter le fichier XML

def traitment_file_xml(xml_file_path):
    
    def _traitment():
                
        try:
            with open(xml_file_path, 'r') as file: # Lecture du contenu du fichier xml
                xml_content = file.read()
        except FileNotFoundError:
            print(f" Le fichier {xml_file_path} n'existe pas! ")
            exit()
                
        # Parser le contenu du fichier xml
        try:
            root= ET.fromstring(xml_content)
        except ET.ParseError:
            logging.error("Erreur survenue lors de l'analyse du fichier xml ")
            exit()
            
        # Boucle pour parcourir les  différents éléments
        for employee in root.findall('employee'):
            
            # Récuperation des attributs de chaque employé
            firstname = employee.find('firstname').text
            lastname = employee.find('lastname').text
            category = employee.get('category')
            mailbox= employee.find('mailbox').text
            emails = extract_emails(employee) # récupère les adresses
            
            # Vérifier si l'employé existe déjà dans la base de données
            estemployee = Employee.objects.filter(firstname=firstname, lastname=lastname).first()
            if estemployee:# Si l'employé existe déjà, passer à l'employé suivant
                continue
            
            # Peuplement de la table Employee
            try:
                if firstname and lastname and category and mailbox:
                    emp = Employee.objects.create(lastname=lastname, firstname=firstname, category=category,mailbox=mailbox)
                    
                    for e in emails:
                        #création de l'addresseEmail
                        ad = AddresseEmail.objects.get_or_create(addresse=e,estInterne=True, employee=emp)[0]
                            
            except Employee.DoesNotExist as e:
                logging.error(f" Erreur lors de la création de l'employé {lastname}: {e} ")
                
    print("    Traitement du fichier xml terminé     ")                                       
    _traitment()


#Fonction pour parcourir les répertoires

def parcours_directory(directory):
    files_list = []
    for element in os.listdir(directory): # Parcours tous les éléments dans le répertoire
        element_path = os.path.join(directory, element) # Construis le chemin complet de l'élément
        if os.path.isfile(element_path): # Vérifie si c'est un fichier
            if element_path not in files_list: # s'il n'existe pas, le rajouter dans la liste
                files_list.append(element_path)
        elif os.path.isdir(element_path): # Vérifie si c'est un dossier
            files_list.extend(parcours_directory(element_path)) # appelle récursivement parcours_directory() pour parcourir le sous-répertoire
    return files_list  


#Fonction pour parcourir les fichiers du dossier maildir 
 
def parcours_file(file_path):
    emplacement = file_path
    
    if os.path.isfile(file_path): #vérifie s'il s'agit bien d'un fichier et non d'un répertoire
        with open(file_path, 'r', encoding='latin1') as f:
            contenu = f.read()
            
            # Extraction des informations nécessaires: sender, recipient, subject, content, timestamp
            sender_match = re.search(r"From: (.+)", contenu) #ok
            receiver_match = re.search(r"To: ((?:.+\n)+)(?=Subject)", contenu)  #ok
            cc_receiver_match = re.search(r"Cc: ((?:.+\n)+)(?=Mime-Version)", contenu)  #ok
            bcc_receiver_match = re.search(r"Bcc: ((?:.+\n)+)(?=X-From)", contenu)  #ok
            subject_match = re.search(r"Subject: (.+)", contenu) #ok
            timestamp_match = re.search(r"Date: (.+)", contenu) #ok 
            content_start_index = contenu.find("\n\n") +2 # Trouver le début du contenu, en excluant les deux premiers sauts de ligne (+2)
            content = contenu[content_start_index:]

            #Extraction des données
            timestamp_str = timestamp_match.group(1)
            sender_email = sender_match.group(1)
            receivers_email = receiver_match.group(1) if receiver_match else ""
            subject = subject_match.group(1) if subject_match else ""
            cc_receivers_email = cc_receiver_match.group(1)  if cc_receiver_match else ""
            bcc_receivers_email = bcc_receiver_match.group(1)  if bcc_receiver_match else "" 
            
            # Conversion du format en objet de date Django
            date = parse(timestamp_str) if timestamp_str else None
                       
            # Nettoyage et division de la chaîne de destinataires
            to_emails = re.findall(r'[\w\.-]+@[\w\.-]+', receivers_email) # il s'agit ici d'une liste pouvant contenir d'autres listes
            cc_emails = re.findall(r'[\w\.-]+@[\w\.-]+', cc_receivers_email)
            bcc_emails = re.findall(r'[\w\.-]+@[\w\.-]+', bcc_receivers_email)
            
            
            # Enregistrement des données dans la BDD               
            try:
                with transaction.atomic():    
                                         
                # Si l'addresse de l'expéditeur n'existe pas, nous la créons
                    if '@enron.com' in sender_email:
                        sender = AddresseEmail.objects.get_or_create(addresse=sender_email,estInterne=True)[0]
                    else:
                        sender = AddresseEmail.objects.get_or_create(addresse=sender_email)[0]    
                    #print(f" addresse {sender.addresse} a été ajouté avec succès.  ")

                    # Dictionnaire pour stocker les adresses e-mail par type
                    email_types = {
                        'TO': to_emails,
                        'CC': cc_emails,
                        'BCC': bcc_emails
                    }

                    # Création de l'Email
                    email = Email.objects.create(
                        date=date,
                        sender_mail=sender,
                        subject=subject,
                        content=content
                    )

                    for type, emails in email_types.items():  # Boucle sur chaque type d'e-mail
                        for email_address in emails:  # Boucle sur chaque adresse e-mail dans le groupe
                            if clean(email_address):
                                
                                #Crée ou récupère l'adresse e-mail
                                ad, _ = AddresseEmail.objects.get_or_create(addresse=email_address, estInterne=email_address.endswith('@enron.com'))
                                
                                # Associe les destinataires aux e-mails 
                                ReceiversMail.objects.update_or_create(email=email, addresse_email=ad, type=type) #  update_or_create pour associer cette adresse e-mail à l'e-mail en cours de création avec le bon type.
                                print(" Ajout des destinataires terminé   ")
                                                 
            except Email.DoesNotExist as e:
                logging.error(f" Erreur lors de l'enregistrement de l'email: {email}")  
                 
            except IntegrityError as e:
                logging.error(f"Erreur d'intégrité: {e}") 
                pass
              
          
# Fonction pour traiter les fichiers en parallèle et optimiser le temps d'exécution. Actuellement le peuplement se fait en moins d'une heure

def traitment_files(files_paths):
    with Pool() as pool:
        pool.map(parcours_file,files_paths)
    print("    Traitement du dossier maildir terminé !    ") 
    
# Fonction pour valider le format des addresses email
 
def clean(ad):
    try:
        validate_email(ad)
        return True  # Retourne True si l'adresse e-mail est valide
    except ValidationError:
        return False  # Retourne False si l'adresse e-mail n'est pas valide

