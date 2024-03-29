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
maildir_path = "/users/2024/ds1/123010405/Documents/Bddr-2024/maildir/"

if __name__ == '__main__':
    debut = time.time()
    #pour assurer le remplissage de notre table Employee
    traitment_file_xml(xml_file_path)
    
<<<<<<< HEAD
    files_paths = parcours_directory(maildir_path)  
=======
    files_paths = parcours_directory(maildir_path)
>>>>>>> 90ac3f11320c1a770795b1434495743f716b0650
    
    traitment_files(files_paths)  # Traitement des fichiers en parallèle
    
    fin=time.time()
    print("\nTemps d'exécution du processus : ", (fin-debut)//60,"min")

        

