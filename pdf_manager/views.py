import os
from .models import AccessLog
from .models import PDFDocument
from django.conf import settings
from .forms import PDFUploadForm
from .forms import UserRegisterForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test

@login_required
def catalog_view(request):
    pdfs = PDFDocument.objects.all()
    return render(request, 'catalog/catalog.html', {'pdfs': pdfs})

def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.uploaded_by = request.user
            pdf.save()
            return redirect('catalog')
    else:
        form = PDFUploadForm()
    return render(request, 'admin_panel/admin_panel.html', {'form': form})

@login_required
def viewer_view(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)

    # Guardar log de acceso
    AccessLog.objects.create(user=request.user, pdf=pdf, action='view')

    return render(request, 'viewer/viewer.html', {'pdf': pdf})

def pdf_viewer_bypass(request, pdf_filename):
    pdf_path = os.path.join(settings.MEDIA_ROOT, 'pdfs', pdf_filename)
    if not os.path.exists(pdf_path):
        raise Http404("PDF no encontrado.")
    
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['X-Frame-Options'] = 'ALLOWALL'  # 🔥 Quitar restricción para iframes
    return response

def is_admin(user):
    return user.is_staff  # Cambiar según tu lógica de roles

@user_passes_test(is_admin)
def upload_pdf(request):
    if request.method == 'POST':
        form = PDFUploadForm(request.POST, request.FILES)
        if form.is_valid():
            pdf = form.save(commit=False)
            pdf.uploaded_by = request.user
            pdf.save()
            return redirect('catalog')
    else:
        form = PDFUploadForm()
    return render(request, 'admin_panel/admin_panel.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


