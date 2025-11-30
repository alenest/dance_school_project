from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add/<str:table_name>/', views.admin_add_record, name='admin_add'),
    path('admin/edit/<str:table_name>/<int:record_id>/', views.admin_edit_record, name='admin_edit'),
    path('admin/delete/<str:table_name>/<int:record_id>/', views.admin_delete_record, name='admin_delete'),
]