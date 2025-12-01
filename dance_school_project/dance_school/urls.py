from django.urls import path
from . import views
from . import views_additional

urlpatterns = [
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('admin-panel/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/add/<str:table_name>/', views.admin_add_record, name='admin_add'),
    path('admin-panel/edit/<str:table_name>/<str:record_id>/', views.admin_edit_record, name='admin_edit'),
    path('admin-panel/delete/<str:table_name>/<str:record_id>/', views.admin_delete_record, name='admin_delete'),
    
    # Новые маршруты для демонстрации объектов БД
    path('db-functions/', views_additional.function_demo, name='function_demo'),
    path('db-views/', views_additional.views_demo, name='views_demo'),
    path('db-triggers/', views_additional.triggers_demo, name='triggers_demo'),
]