from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
    path('user-logs/', views.user_logs, name='user_logs'),
    path('register/', views.register_view, name='register'),
    path('pdf/<int:pdf_id>/', views.viewer_view, name='viewer'),
    path('pdf_download/<int:pdf_id>/', views.pdf_download, name='pdf_download'),
    path('media_bypass/<str:pdf_filename>/', views.pdf_viewer_bypass, name='pdf_bypass'),
]
