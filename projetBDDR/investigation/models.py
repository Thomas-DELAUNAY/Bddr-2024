from django.db import models

# Create your models here.
class Employee(models.Model):
    lastname = models.CharField(max_length=50) 
    firstname = models.CharField(max_length=50)
    category = models.CharField(max_length=50, null=True)
    mailbox = models.CharField(max_length=50)
    
    #ici on définira le couple (lastname,firstname) comme clé primaire,unique
    class Meta:
        # Spécifier l'unicité du couple (firstname, lastname)
        unique_together = ['firstname', 'lastname']
    
    def __str__(self):
        return f"{self.lastname} {self.firstname},{self.category}, {self.mailbox}"

    def __repr__(self):
        return f"{self.lastname} {self.firstname},{self.category}, {self.mailbox}"
    

class AddresseEmail(models.Model):
    addresse = models.EmailField(unique=True)
    estinterne = models.BooleanField(default=False)
    employee = models.ForeignKey('Employee',null=True,default=None, on_delete=models.CASCADE)
  
    class Meta:
        unique_together = ['addresse', 'employee']
        
        
class ReceiversMail(models.Model):
    TO='To'
    CC='Cc'
    BCC='Bcc'
    choices=[(TO,'To'), (CC,'Cc'),(BCC,'Bcc')]
    email = models.ManyToManyField('Email')
    addresse_email=models.ForeignKey('AddresseEmail', on_delete=models.CASCADE,related_name='recipient_email')
    type = models.CharField(max_length=3, choices=choices)
   
         
    def __str__(self):
        return f" {self.addresse_email} - {self.type}"
    
    def create_with_emails(cls, addresse_email, type, emails):  # Ajout du paramètre cls
        receivers_mail = cls(addresse_email=addresse_email, type=type)  # Utilisation de cls pour instancier ReceiversMail
        receivers_mail.save()
        receivers_mail.email.set(emails)
        return receivers_mail
    
        
class Email(models.Model):
    date = models.DateTimeField()
    sender_mail = models.ForeignKey('AddresseEmail',null=True,default=None, on_delete=models.CASCADE, related_name='sent_email')
    subject = models.CharField(max_length=200, default=None)
    content = models.TextField(default='')
    
# Cette classe gère les objets de type couple d'employées et le nombre de mails echangés entre ces derniers
class CoupleCommunication(models.Model):
    employee_addresse_1 = models.EmailField(max_length=100)
    employee_addresse_2 = models.EmailField(max_length=100)
    total_mails_echanges = models.IntegerField()
    
    class Meta:
        unique_together = ['employee_addresse_1', 'employee_addresse_2']   