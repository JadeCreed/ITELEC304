from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.add_log, name='add_log'),
    path('import/', views.import_data, name='import_data'),
    path('analytics/', views.analytics_page, name='analytics'),
    path('logs/', views.activity_logs, name='activity_logs'),
    path('productivity/', views.productivity_score_page, name='productivity'),
    path('reports/', views.reports_page, name='reports'),
    path('delete/<int:pk>/', views.delete_log, name='delete_log'),
]