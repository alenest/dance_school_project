from django.urls import path
from . import views

urlpatterns = [
    # Основные маршруты
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    
    # Публичное расписание
    path('public-schedule/', views.public_schedule, name='public_schedule'),
    
    # Тренерская панель
    path('trainer-panel/', views.trainer_dashboard, name='trainer_dashboard'),
    path('trainer-panel/edit-schedule/<int:schedule_id>/', views.trainer_edit_schedule, name='trainer_edit_schedule'),
    
    # Админ панель
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
]