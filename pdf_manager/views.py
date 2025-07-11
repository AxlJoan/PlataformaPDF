import os
from user_agents import parse
from .models import AccessLog
from .models import PDFDocument
from django.conf import settings
from .forms import PDFUploadForm
from .forms import UserRegisterForm
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required

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
    
    ip = get_client_ip(request)  # Obtener IP
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_ua = parse(user_agent)

    # Guardar log de acceso
    AccessLog.objects.create(
        user=request.user,
        pdf=pdf,
        action='view',
        ip_address=ip,
        browser=parsed_ua.browser.family,
        os=parsed_ua.os.family,
        device=parsed_ua.device.family,
    )

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

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@login_required
def pdf_download(request, pdf_id):
    pdf = get_object_or_404(PDFDocument, id=pdf_id)
    pdf_filename = pdf.file_path.name  # Ahora sí existe, porque ya se cargó el PDF
    pdf_path = os.path.join(settings.MEDIA_ROOT, pdf_filename)
    
    if not os.path.exists(pdf_path):
        raise Http404("PDF no encontrado.")

    # Registrar el log
    ip = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    parsed_ua = parse(user_agent)
    AccessLog.objects.create(user=request.user, 
                             pdf=pdf, 
                             action='download', 
                             ip_address=ip,
                             browser=parsed_ua.browser.family,
                             os=parsed_ua.os.family,
                             device=parsed_ua.device.family,)

    # Descargar
    response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
    return response

from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def user_logs(request):
    logs = AccessLog.objects.select_related('user', 'pdf').order_by('-accessed_at')

    # Filtros opcionales (usuario, acción)
    user_filter = request.GET.get('user', '')
    action_filter = request.GET.get('action', '')

    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if action_filter:
        logs = logs.filter(action=action_filter)

    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Para AJAX solo renderizamos la tabla (partial)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('admin_panel/partials/user_logs_table.html', {
            'page_obj': page_obj,
        }, request=request)
        return JsonResponse({'html': html})

    # Documentos más vistos
    top_docs = AccessLog.objects.values('pdf__title').annotate(total=Count('id')).order_by('-total')[:5]
    doc_labels = [d['pdf__title'] for d in top_docs]
    doc_data = [d['total'] for d in top_docs]

    # Usuarios más activos
    top_users = AccessLog.objects.values('user__username').annotate(total=Count('id')).order_by('-total')[:5]
    user_labels = [u['user__username'] for u in top_users]
    user_data = [u['total'] for u in top_users]

    # Accesos por hora
    hours = AccessLog.objects.annotate(hour=ExtractHour('accessed_at')).values('hour').annotate(total=Count('id')).order_by('hour')
    hour_labels = [f"{h['hour']}:00" for h in hours]
    hour_data = [h['total'] for h in hours]

    # Comparativa vistas vs descargas
    action_counts = AccessLog.objects.values('action').annotate(total=Count('id'))
    action_data = [next((a['total'] for a in action_counts if a['action'] == 'view'), 0),
                   next((a['total'] for a in action_counts if a['action'] == 'download'), 0)]
    
    # Distribución por Navegador
    browsers = AccessLog.objects.values('browser').annotate(total=Count('id')).order_by('-total')
    browser_labels = [b['browser'] for b in browsers]
    browser_data = [b['total'] for b in browsers]
    
    # Dispositivos Más Utilizados
    devices = AccessLog.objects.values('device').annotate(total=Count('id')).order_by('-total')
    device_labels = [d['device'] for d in devices]
    device_data = [d['total'] for d in devices]
    
    # Sistemas Operativos Más Comunes
    oses = AccessLog.objects.values('os').annotate(total=Count('id')).order_by('-total')
    os_labels = [o['os'] for o in oses]
    os_data = [o['total'] for o in oses]

    context = {
        'page_obj': page_obj,
        'user_filter': user_filter,
        'action_filter': action_filter,
        'doc_labels': doc_labels,
        'doc_data': doc_data,
        'user_labels': user_labels,
        'user_data': user_data,
        'hour_labels': hour_labels,
        'hour_data': hour_data,
        'action_data': action_data,
        'browser_labels': browser_labels,
        'browser_data': browser_data,
        'device_labels': device_labels,
        'device_data': device_data,
        'os_labels': os_labels,
        'os_data': os_data,
    }
    return render(request, 'admin_panel/user_logs.html', context)
