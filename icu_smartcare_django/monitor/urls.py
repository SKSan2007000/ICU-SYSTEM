from django.urls import path
from . import views
path('doctor-watch/', views.doctor_watch, name='doctor_watch'),

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add-patient/', views.add_patient, name='add_patient'),
    path('simulate/<int:patient_id>/', views.simulate_vitals, name='simulate_vitals'),
    path('manual-alert/<int:patient_id>/<str:alert_type>/', views.manual_alert, name='manual_alert'),
    path('nurse-room/', views.nurse_room, name='nurse_room'),
    path('watch/', views.watch, name='watch'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor-watch/', views.doctor_watch, name='doctor_watch'),
    path('clear-alert/<int:alert_id>/', views.clear_alert, name='clear_alert'),
    path('history/', views.history, name='history'),
    path('seed-demo/', views.seed_demo, name='seed_demo'),
]
