from django.db import models
from django.contrib.auth.models import User

class PDFDocument(models.Model):
    title = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='pdfs/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class AccessLog(models.Model):
    ACTION_CHOICES = (
        ('view', 'Visualización'),
        ('download_attempt', 'Intento de Descarga'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pdf = models.ForeignKey(PDFDocument, on_delete=models.CASCADE)
    accessed_at = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
