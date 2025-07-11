from django import forms
from .models import PDFDocument
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class PDFUploadForm(forms.ModelForm):
    class Meta:
        model = PDFDocument
        fields = ['title', 'file_path']

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
