from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('result-report/<int:id>/', views.Result_report, name='ResultReport'),
    path('download-report/<int:id>/', views.download_report_pdf, name='download_report_pdf'),
    path('suggestions/', views.hiring_suggestions, name='hiring_suggestions'),
    path('manual-schedule/', views.manual_schedule, name='manual_schedule'),
    path('interview/delete/<int:id>/', views.delete_interview, name='delete_interview'),
]