CREATE TABLE Employee (
  id INT PRIMARY KEY,  
  lastname VARCHAR(50) NOT NULL,
  firstname VARCHAR(50) NOT NULL,
  category_id INTEGER  , 
  mailbox VARCHAR(50) NOT NULL,
  UNIQUE(firstname, lastname)  
);

CREATE TABLE Groupe (
  id INT PRIMARY KEY,
  nom_groupe VARCHAR(100) UNIQUE NOT NULL  
);

CREATE TABLE AddresseEmail (
  id INTEGER PRIMARY KEY,
  addresse VARCHAR(254) UNIQUE NOT NULL, 
  estinterne BOOLEAN DEFAULT FALSE
);

CREATE TABLE ReceiversMail (
  id INTEGER PRIMARY KEY,
  addresse_email_id INT ,
  type VARCHAR(3) CHECK(type IN ('To', 'Cc', 'Bcc')),  
  UNIQUE(addresse_email_id, type) 
);

CREATE TABLE ReceiversMail_email ( 
  receiversmail_id INT ,
  email_id INT 
);

CREATE TABLE Email (
  id INTEGER PRIMARY KEY,
  date TIMESTAMP DEFAULT NULL,
  sender_mail_id INT ,
  subject VARCHAR(200) DEFAULT NULL,
  content TEXT DEFAULT NULL
);

CREATE TABLE CoupleCommunication (
  id INTEGER PRIMARY KEY,
  employee_addresse_1 VARCHAR(100) NOT NULL,
  employee_addresse_2 VARCHAR(100) NOT NULL,
  total_mails_echanges INT NOT NULL,
  UNIQUE(employee_addresse_1, employee_addresse_2, total_mails_echanges)  
);

-- Ajouter les clés étrangères pour la table Employee
ALTER TABLE Employee
ADD CONSTRAINT fk_employee_category_id
FOREIGN KEY (category_id) REFERENCES Groupe(id) ON DELETE CASCADE;

-- Ajouter les clés étrangères pour la table ReceiversMail
ALTER TABLE ReceiversMail
ADD CONSTRAINT fk_receiversmail_addresse_email_id
FOREIGN KEY (addresse_email_id) REFERENCES AddresseEmail(id) ON DELETE CASCADE;

-- Ajouter les clés étrangères pour la table ReceiversMail_email
ALTER TABLE ReceiversMail_email
ADD CONSTRAINT fk_receiversmail_email_receiversmail_id
FOREIGN KEY (receiversmail_id) REFERENCES ReceiversMail(id) ON DELETE CASCADE;

ALTER TABLE ReceiversMail_email
ADD CONSTRAINT fk_receiversmail_email_email_id
FOREIGN KEY (email_id) REFERENCES Email(id) ON DELETE CASCADE;

-- Ajouter les clés étrangères pour la table Email
ALTER TABLE Email
ADD CONSTRAINT fk_email_sender_mail_id
FOREIGN KEY (sender_mail_id) REFERENCES AddresseEmail(id) ON DELETE CASCADE;