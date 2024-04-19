import os
import django
import time

#Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetBDDR.settings')
django.setup()

#Importation des modules
from investigation.modules import *

# Chemin vers le fichier emlpoyes.XML
xml_file_path = r"C:\Users\utilisateur\Desktop\BDDR\projetBDDR\employes_enron.xml"
# Chemin vers le répertoire maildir
maildir_path = r"C:\Users\utilisateur\Desktop\BDDR\maildir"

if __name__ == '__main__':
    debut = time.time()
    
    # Extraction des données du fichier XML
    traitment_file_xml(xml_file_path)
    
    # Extraction des données du dossier maildir
    for file_path  in parcours_directory(maildir_path):
        parcours_file(file_path)  
    
    fin=time.time()
    print("\nTemps d'exécution du processus : ", (fin-debut)//60," min") 

        

