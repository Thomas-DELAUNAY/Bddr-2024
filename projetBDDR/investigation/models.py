from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


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
    estInterne = models.BooleanField(default=False)
    employee = models.ForeignKey('Employee',null=True,default=None, on_delete=models.CASCADE)
    receiver_emails = models.ManyToManyField('Email',related_name='receive_addresses')
    
    class Meta:
        unique_together = ['addresse', 'employee']


    def clean(self):
        try:
            validate_email(self.addresse)
        except ValidationError :
            raise ValidationError({'Adresse e-mail non valide : {self.addresse}'})
        
        
class ReceiversMail(models.Model):
    TO='TO'
    CC='CC'
    BCC='BCC'
    choices=[(TO,'To'), (CC,'Cc'),(BCC,'Bcc')]
    email = models.ForeignKey('Email',on_delete=models.CASCADE)
    addresse_email=models.ForeignKey('AddresseEmail', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=choices) 
    
    class Meta:
        unique_together = ('email', 'addresse_email')
        
class Email(models.Model):
    date = models.DateTimeField()
    sender_mail = models.ForeignKey('AddresseEmail',null=True,default=None, on_delete=models.CASCADE, related_name='sent_email')
    subject = models.CharField(max_length=200, default=None)
    contenu = models.TextField(default='')
    receivers = models.ManyToManyField('AddresseEmail', through='ReceiversMail', related_name='received_emails')
        
    
    
