import re,os
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.conf import settings
import xml.etree.ElementTree as ET
import datetime, time
import multiprocessing
from multiprocessing import Pool # pour optimiser le temps d'exécution du programme
from django.db import transaction
import traceback


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
                # Lecture du contenu du fichier xml
        try:
            with open(xml_file_path, 'r') as file:
                xml_content = file.read()
        except FileNotFoundError:
            print(f" Le fichier {xml_file_path} n'existe pas! ")
            exit()
                
        # Parser le contenu du fichier xml
        try:
            root= ET.fromstring(xml_content)
        except ET.ParseError:
            print("Erreur survenue lors de l'analyse du fichier xml ")
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
                    #print(emp)
                    
                    for e in emails:
                        if '@enron' in e:
                            #création de l'addresseEmail
                            ad,et = AddresseEmail.objects.get_or_create(
                                addresse=e,estInterne=True, employee=emp)
                            
            except Employee.DoesNotExist as e:
                print(f" Erreur lors de la création de l'employé {lastname}: {e} ")
                
    print("    Traitement du fichier xml terminé     ")                                       
    return _traitment()


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


#Fonction pour parcourir les fichiers
 
def parcours_file(file_path):
    if os.path.isfile(file_path): #vérifie s'il s'agit bien d'un fichier et non d'un répertoire
        with open(file_path, 'r', encoding='latin1') as f:
            contenu = f.read()
            # Extraction des informations nécessaires: sender, recipient, subject, content, timestamp
            #id_match = re.search(r"Message-ID: <(.+).J", contenu) #ok
            sender_match = re.search(r"From: (.+)", contenu) #ok
            receiver_match = re.search(r"To:  (.+)", contenu)  #ok
            cc_receiver_match = re.search(r"Cc:  (.+)", contenu)  #ok
            bcc_receiver_match = re.search(r"Bcc:  (.+)", contenu)  #ok
            subject_match = re.search(r"Subject: (.+)", contenu) #ok
            timestamp_match = re.search(r"Date: (.+) \S+", contenu) #ok 
            content_start_index = contenu.find("\n\n") + 2  # Trouver l'indice de début du contenu
            content = contenu[content_start_index:]
            #print(subject_match)
            
            # Vérification des correspondances:


            #Extraction des données
            #email_id=id_match.group(1)
            date_send = timestamp_match.group(1)
            sender_email = sender_match.group(1)
            receivers_email = receiver_match.group(1) if receiver_match else ""
            subject = subject_match.group(1) if subject_match else ""
            cc_receivers_email = cc_receiver_match.group(1)  if cc_receiver_match else ""
            bcc_receivers_email = bcc_receiver_match.group(1)  if bcc_receiver_match else ""
            print(receivers_email)
            
            # Convertir le timestamp en objet datetime
            try:
                if date_send:
                    date_send = datetime.datetime.strptime(date_send, "%a, %d %b %Y %H:%M:%S %z")
            except ValueError as e:
                print(f"Erreur lors de la conversion de la date: {e}")
                return  
                       
            # Nettoyage et division de la chaîne de destinataires
            chaine1 = re.findall(r'[\w\.-]+@[\w\.-]+', receivers_email) # il s'agit ici d'une liste pouvant contenir d'autres listes
            chaine2 = re.findall(r'[\w\.-]+@[\w\.-]+', cc_receivers_email)
            chaine3 = re.findall(r'[\w\.-]+@[\w\.-]+', bcc_receivers_email)
            
            # Création des destinataires d'un email
            to_ = [AddresseEmail.objects.get_or_create(addresse=elt)[0]  for elt in chaine1]
            cc_ = [AddresseEmail.objects.get_or_create(addresse=elt)[0] for elt in chaine2 ]
            bcc_ = [AddresseEmail.objects.get_or_create(addresse=elt)[0] for elt in chaine3]
                  
            # Enregistrement des données dans la BDD               
            try:
                with transaction.atomic():
                    
                    # Vérification de l'existence de l'adresse
                    sender = AddresseEmail.objects.filter(addresse=sender_email).first()
                    
                    if sender is None:
                        # Si l'expéditeur n'existe pas, nous le créons
                        sender,test = AddresseEmail.objects.get_or_create(addresse=sender_email)
                        print(f" L'addresse {sender_email} a été ajouté avec succès.  ")
                    else:
                        print(f"{sender_email} est déja dans la base.")
                    
                    # Création de l' Email
                    email = Email.objects.create(
                                dateSend=date_send,
                                sender_mail= sender,
                                subject=subject,
                                contenu=content
                        )

                    # Ajouter les destinataires (To), (Cc) et (Bcc) à l'Email qu'on vient de créer
                    [ReceiversMail.objects.create(email=email, addresse_email=to, type=ReceiversMail.TO) for to in to_]
                    [ReceiversMail.objects.create(email=email, addresse_email=cc, type=ReceiversMail.CC) for cc in cc_]
                    [ReceiversMail.objects.create(email=email, addresse_email=bcc, type=ReceiversMail.BCC) for bcc in bcc_]
                                    
            except Email.DoesNotExist as e:
                print(f" Erreur lors de l'enregistrement de l'email: {email}")   
            except IntegrityError as e:
                print(f"Erreur d'intégrité: {e}")  # Imprimer l'erreur d'intégrité sans la trace complète
                #traceback.print_exc()  # Afficher la trace complète de l'exception seulement pour le débogage
          
# fonction pour traiter les fichiers en parallèle
def traitment_files(files_paths):
    with Pool() as pool:
        pool.map(parcours_file,files_paths)
    print("    Traitement du dossier maildir terminé     ") 
    
    



