from django.db import models

# Create your models here.
class Register(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    age = models.IntegerField()
    place = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    role = models.CharField(max_length=50, default='user')

    def __str__(self):
        return self.name
    



class tbl_doctor(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    age = models.IntegerField()
    qualification = models.CharField(max_length=255)
    address = models.TextField()
    email = models.EmailField()
    phno = models.CharField(max_length=15)
    doctor_image = models.ImageField(upload_to='doctor_images/')
    id_proof = models.ImageField(upload_to='id_proofs/')
    expirience = models.CharField(max_length=100)
    hospital_name = models.CharField(max_length=255)
    hospital_address = models.TextField()
    hospital_phno = models.CharField(max_length=20)
    hospital_place = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    doctor_id = models.CharField(max_length=100)
    role = models.CharField(max_length=50, default='doctor')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name






#pcod prediction model
from django.db import models
from .models import Register   # your user model

class PredictionResult(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to="medical_reports/")
    result = models.CharField(max_length=50)
    extracted_data = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.result}"
