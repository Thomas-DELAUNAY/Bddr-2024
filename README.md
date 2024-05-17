# Documentation de notre application web Enron
 Implémentation d'une application web permettant de passer des requêtes paramétrées et de visualiser les réponses, en utilisant Django+PostegreSQL


Réalisé par Jennifer NGOUNA et Thomas DELAUNAY 
M1 DS, Universtié d'Angers


## Contexte

L’affaire Enron (https://fr.wikipedia.org/wiki/Scandale_Enron) est connue comme l’un des plus
grands cas de manipulation financière aux États-Unis. Parmi les diverses enquêtes judiciaires
menées, la fouille des contenus des e-mails a constitué une piste essentielle pour comprendre la
dynamique entre les différents acteurs et leur rôle dans l’affaire. D'où l'intérêt de notre travail reposant principalement sur la fouille des contenus des e-mails.

L'objectif étant de développer une application destinée aux enquêteurs (non informaticiens ou tout autre utilsateur).  Elle leur propose un jeu de formulaires leur permettant d'explorer, de visualiser et d'analyser des données. Un formulaire correspond à une interrogation/visualisation, il fixe certains paramètres de la requête ainsi que d'éventuelles options  pour la visualisation.  Il a été necessaire de se mettre dans la peau d'un enquêteur afin d'imaginer quelles requêtes sont
pertinentes, et quelles visualisations sont judicieuses.


## Prérequis

Les données sont une arborescence de boîtes mails et un fichier XML. L’archive est
récupérable depuis https://math.univ-angers.fr/perso/jaclin/enron/.

L'utilisation de ce projet avec votre ordinateur  nécessite de disposer, sur sa machine:
- d'un connexion internet pour récupérer l'archive
- d'un éditeur de code source telle que Visual Studio Code, Notepad++, Sublime ou tout autre éditeur disponible sous windows, linux,mac.
- d'un navigateur.

[](#description)Description
-----------------------------
Ce projet se compose de six classes:
- Employee: gère les informations des employés issus du fichier XML uniquement.
- AddresseEmail : gère les addresses mail.
- ReceiversMail : gère les destinataires associés au différents emails.
- Email : gère les messages de type email ou mail.
- CoupleCommunication : gère les couple d'envoyées ayant communiqué entre eux.
- Conversation: gère l'email que l'on considère comme étant une converstation qui retourne les differentes échanges la composant.

[](#librairies_python) Librairies python utilisées
----------------------------------------


