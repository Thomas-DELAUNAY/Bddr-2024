import re,os
from django.db.utils import IntegrityError
import xml.etree.ElementTree as ET
import datetime
import multiprocessing
from multiprocessing import Pool # pour optimiser le temps d'exécution du programme
from django.db import transaction

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

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
                pass
            
            # Peuplement de la table Employee
            try:
                if firstname and lastname and category and mailbox:
                    emp = Employee.objects.create(lastname=lastname, firstname=firstname, category=category,mailbox=mailbox)
                    
                    for e in emails:
<<<<<<< HEAD
                        #création de l'addresseEmail
                        ad = AddresseEmail.objects.get_or_create(addresse=e,estInterne=True, employee=emp)[0]
=======
                        if '@enron' in e:
                            #création de l'addresseEmail
                            ad= AddresseEmail.objects.get_or_create(
                                addresse=e,estInterne=True, employee=emp)[0]
                            ad.clean()
>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
                            
            except Employee.DoesNotExist as e:
                print(f" Erreur lors de la création de l'employé {lastname}: {e} ")
                
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


#Fonction pour parcourir les fichiers
 
def parcours_file(file_path):
    if os.path.isfile(file_path): #vérifie s'il s'agit bien d'un fichier et non d'un répertoire
        with open(file_path, 'r', encoding='latin1') as f:
            contenu = f.read()
<<<<<<< HEAD
            
=======

>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
            # Extraction des informations nécessaires: sender, recipient, subject, content, timestamp
            sender_match = re.search(r"From: (.+)", contenu) #ok
            receiver_match = re.search(r"To:  (.+)", contenu)  #ok
            cc_receiver_match = re.search(r"Cc:  (.+)", contenu)  #ok
            bcc_receiver_match = re.search(r"Bcc:  (.+)", contenu)  #ok
            subject_match = re.search(r"Subject: (.+)", contenu) #ok
            timestamp_match = re.search(r"Date: (\w+, \d+ \w+ \d+ \d+:\d+:\d+)", contenu) #ok
            content_start_index = contenu.find("\n\n") + 2  # Trouver l'indice de début du contenu
            content = contenu[content_start_index:]

            #Extraction des données
<<<<<<< HEAD
=======

>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
            date = timestamp_match.group(1)
            sender_email = sender_match.group(1)
            receivers_email = receiver_match.group(1) if receiver_match else ""
            subject = subject_match.group(1) if subject_match else ""
            cc_receivers_email = cc_receiver_match.group(1)  if cc_receiver_match else ""
            bcc_receivers_email = bcc_receiver_match.group(1)  if bcc_receiver_match else ""
<<<<<<< HEAD
            
=======


>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
            # Convertir le timestamp en objet datetime
            try:
                if date:
                    date = datetime.datetime.strptime(date, "%a, %d %b %Y %H:%M:%S")
            except ValueError as e:
                print(f"Erreur lors de la conversion de la date: {e}")
                return  
                       
            # Nettoyage et division de la chaîne de destinataires
            chaine1 = re.findall(r'[\w\.-]+@[\w\.-]+', receivers_email) # il s'agit ici d'une liste pouvant contenir d'autres listes
            chaine2 = re.findall(r'[\w\.-]+@[\w\.-]+', cc_receivers_email)
            chaine3 = re.findall(r'[\w\.-]+@[\w\.-]+', bcc_receivers_email)
            
            # Création des destinataires d'un email
            to_=[]
            cc_=[]
            bcc_=[]
<<<<<<< HEAD
            
            for elt1 in chaine1 :
                if clean(elt1) :
                    if '@enron.com' in elt1:
                        to_.append(AddresseEmail.objects.get_or_create(addresse=elt1,estInterne=True)[0])
                    else:
                        to_.append(AddresseEmail.objects.get_or_create(addresse=elt1)[0])
            
            for elt2 in chaine2 :
                if clean(elt2) :
                    if '@enron.com' in elt2:
                        cc_.append(AddresseEmail.objects.get_or_create(addresse=elt2,estInterne=True)[0])
                    else:
                        cc_.append(AddresseEmail.objects.get_or_create(addresse=elt2)[0])             
          
            for elt3 in chaine3 :
                if clean(elt3) :
                    if '@enron.com' in elt3:
                        bcc_.append(AddresseEmail.objects.get_or_create(addresse=elt3,estInterne=True)[0]) 
                    else:
                        bcc_.append(AddresseEmail.objects.get_or_create(addresse=elt3)[0])            
            
                  
=======

            #if chaine1 and chaine2 and chaine3:

            for elt1,elt2,elt3 in zip(chaine1,chaine2, chaine3):
                if elt1.endsWith('@enron') or elt2.endsWith('@enron') or elt3.endsWith('@enron'):
                    if elt1:
                        ad1 = AddresseEmail.objects.get_or_create(addresse=elt1, estInterne=True)[0]
                        ad1.clean()
                        to_.append(ad1)
                    if elt2:
                        ad2 = AddresseEmail.objects.get_or_create(addresse=elt2, estInterne=True)[0]
                        ad2.clean()
                        cc_.append(ad2)
                    if elt:
                        ad3 = AddresseEmail.objects.get_or_create(addresse=elt3, estInterne=True)[0]
                        ad3.clean()
                        bcc_.append(ad3)

            else:
                #print("Erreur au moins une des chaines est vide")
                pass

>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
            # Enregistrement des données dans la BDD               
            try:
                with transaction.atomic():
                    
                    # Vérification de l'existence de l'adresse
                    sender = AddresseEmail.objects.filter(addresse=sender_email).first()
                    
<<<<<<< HEAD
                    if sender:
                        #print(f"{sender} est déja dans la base.")
                        pass                        
                        
                    else: # Si l'addresse de l'expéditeur n'existe pas, nous la créons
                        if '@enron.com' in sender_email:
                            sender = AddresseEmail.objects.get_or_create(addresse=sender_email,estInterne=True)[0]
                        else:
                            sender = AddresseEmail.objects.get_or_create(addresse=sender_email)[0]    
                        print(f" addresse {sender_email} a été ajouté avec succès.  ")

=======
                    if sender is None:
                        # Si l'expéditeur n'existe pas, nous le créons
                        sender = AddresseEmail.objects.get_or_create(addresse=sender_email)[0]
                        sender.clean()
                        print(f" L'addresse email {sender} a été ajouté avec succès.  ")
                    else:
                        #print(f"{sender_email} est déja dans la base.")
                        pass
>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
                    
                    # Création de l' Email
                    email = Email.objects.create(
                                date=date,
                                sender_mail= sender,
                                subject=subject,
                                contenu=content
                        )

                    # Ajouter les destinataires (To), (Cc) et (Bcc) à l'Email qu'on vient de créer
                    [ReceiversMail.objects.create(email=email, addresse_email=to, type=ReceiversMail.TO) for to in to_]
                    [ReceiversMail.objects.create(email=email, addresse_email=cc, type=ReceiversMail.CC) for cc in cc_]
                    [ReceiversMail.objects.create(email=email, addresse_email=bcc, type=ReceiversMail.BCC) for bcc in bcc_]
                    print(' to be continued ')
                                    
            except Email.DoesNotExist as e:
                print(f" Erreur lors de l'enregistrement de l'email: {email}")  
                 
            except IntegrityError as e:
                #print(f"Erreur d'intégrité: {e}") 
                pass
              
          
# fonction pour traiter les fichiers en parallèle et optimiser le temps d'exécution. Actuellement le peuplement se fait en moins d'une heure
def traitment_files(files_paths):
    with Pool() as pool:
        pool.map(parcours_file,files_paths)
    print("    Traitement du dossier maildir terminé !    ") 
    
    
def clean(ad):
    try:
        validate_email(ad)
        return True  # Retourne True si l'adresse e-mail est valide
    except ValidationError:
        return False  # Retourne False si l'adresse e-mail n'est pas valide
