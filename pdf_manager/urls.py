from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog_view, name='catalog'),
    path('upload/', views.upload_pdf, name='upload_pdf'),
        path('register/', views.register_view, name='register'),
    path('pdf/<int:pdf_id>/', views.viewer_view, name='viewer'),
    path('media_bypass/<str:pdf_filename>/', views.pdf_viewer_bypass, name='pdf_bypass'),
]
