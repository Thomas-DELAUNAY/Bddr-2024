import os
import django
import re
import logging
from dateutil import parser as date_parser
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetBDDR.settings')
django.setup()

from investigation.models import Employee,AddresseEmail,ReceiversMail,Email

# Configuration du logging
logging.basicConfig(filename='email_extraction.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def extract_emails(text):
    if not text:
        return []
    
    regex = r'[\w\.-]+@[\w\.-]+\.\w+'
    return re.findall(regex, text)

def extract_and_populate_email_info(content):
    try:
        patterns = {
            "sender": r"From: (.+)",
            "receiver": r"To: ((?:.+\n)+)(?=Subject:)",
            "cc": r"Cc: ((?:.+\n)+)(?=Mime-Version:)",
            "bcc": r"Bcc: ((?:.+\n)+)(?=X-From:)",
            "subject": r"Subject: ((?:.+\n)+)(?=Cc:|Mime-Version:|$)",
            "date": r"Date: (.+)",
            "content": r"\n\n(.+)"
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                value = match.group(1).strip() if match.group(1) else None
                if value:
                    if key in ["receiver", "cc", "bcc"]:
                        patterns[key] = extract_emails(value)
                    else:
                        patterns[key] = value
                        
        date = date_parser.parse(patterns["date"]) if patterns["date"] else None
            
        with transaction.atomic():
            sender_email = patterns.get("sender") 
         
            if is_valid_email(sender_email):
                sender_address, _ = AddresseEmail.objects.get_or_create(addresse=sender_email)
                
                email_instance, _ = Email.objects.get_or_create(
                    date=date,
                    sender_mail=sender_address,
                    subject=patterns.get("subject", " "),
                    content=patterns.get("content", " ")
                )
                print(email_instance)
                
                for email_type, field_name in [("TO", "receiver"), ("CC", "cc"), ("BCC", "bcc")]:
                    for ad in patterns.get(field_name, []):
                        adress, _ = AddresseEmail.objects.get_or_create(addresse=ad)
                        r, _ = ReceiversMail.objects.get_or_create(email=email_instance, addresse_email=adress, type=email_type)
                         
    except IntegrityError as ie:
        logging.error(f"Erreur d'intégrité lors de la création des objets : {ie}")
        pass
    except Exception as e:
        logging.error(f"Erreur lors de l'extraction et du peuplement des informations de l'e-mail : {e}")
        pass
    return True

def lire_donnees_arborescence(repertoire):
    """
    Lit les fichiers d'un répertoire et extrait les informations des e-mails pour les insérer dans la base de données.
    """
    try:
        donnees = []
        for racine, _, fichiers in os.walk(repertoire):
            for nom_fichier in fichiers:
                chemin_fichier = os.path.join(racine, nom_fichier)
                with open(chemin_fichier, 'r', encoding='ISO-8859-1') as fichier:
                    contenu = fichier.read()
                    extract_and_populate_email_info(contenu)
                    donnees.append((chemin_fichier, contenu))
    except Exception as e:
        logging.error(f"Erreur lors de la lecture des données de l'arborescence : {e}")
        pass
    return True

directory_path = r"C:\Users\utilisateur\Desktop\BDDR\maildir\lay-k"

if lire_donnees_arborescence(directory_path):
    logging.info("Data insertion into the database completed successfully.")
    pass
else:
    logging.warning("Data insertion into the database failed.")
    pass