import os
import django
from django.conf import settings

#Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetBDDR.settings')
django.setup()

#Importation des modules
from investigation.modules import *

# Chemin vers le fichier emlpoyes.XML
xml_file_path = r"C:\Users\utilisateur\Desktop\BDDR\projetBDDR\employes_enron.xml"
# Chemin vers le répertoire maildir
maildir_path = r"C:\Users\utilisateur\Desktop\BDDR\maildir"

#pour assurer le remplissage de notre table Employee
#traitment_file_xml(xml_file_path)

if __name__ == '__main__':
    #pass
    debut = time.time()
    files_paths = parcours_directory(maildir_path) 
    traitment_files(files_paths)  # Traitement des fichiers en parallèle
    fin=time.time()
    print("\nTemps d'exécution du processus: ", (fin-debut)//60," minutes")
        
