import os
import django
import time

#Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projetBDDR.settings')
django.setup()

#Importation des modules
from investigation.modules import *

# Chemin vers le fichier emlpoyes.XML
xml_file_path = "/users/2024/ds1/123010405/Documents/Bddr-2024/projetBDDR/employes_enron.xml"
# Chemin vers le répertoire maildir
maildir_path = "/users/2024/ds1/123010405/Documents/Bddr-2024/maildir/cash-m"

if __name__ == '__main__':
    debut = time.time()
    #pour assurer le remplissage de notre table Employee
    #traitment_file_xml(xml_file_path)
    
    files_paths = parcours_directory(maildir_path)
    
    traitment_files(files_paths)  # Traitement des fichiers en parallèle
    
    fin=time.time()
    print("\nTemps d'exécution du processus: ", fin-debut,"sec")
    print('Tout est OK')
        

