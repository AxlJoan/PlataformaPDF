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
    pdf = models.ForeignKey('PDFDocument', on_delete=models.CASCADE)
    action = models.CharField(max_length=20)  # 'view' o 'download'
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    browser = models.CharField(max_length=100, blank=True)
    os = models.CharField(max_length=100, blank=True)
    device = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.pdf.title} at {self.accessed_at}"
