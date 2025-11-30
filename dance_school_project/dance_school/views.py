# dance_school/views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .services.auth_service import AuthService
from .services.admin_service import AdminService
from .services.database_service import DatabaseService

def admin_dashboard(request):
    # Проверяем, что пользователь админ
    if 'user' not in request.session or request.session['user'].get('role') != 'admin':
        return redirect('home')
    
    # Получаем данные для всех таблиц
    context = {
        'clients': AdminService.get_all_clients(),
        'dance_styles': AdminService.get_all_dance_styles(),
        'trainers': AdminService.get_all_trainers(),
        'halls': AdminService.get_all_halls(),
        'training_periods': AdminService.get_all_training_periods(),
        'training_slots': AdminService.get_all_training_slots(),
        'administrators': AdminService.get_all_administrators(),
        'schedules': AdminService.get_all_schedules(),
        'registrations': AdminService.get_all_registrations(),
    }
    
    return render(request, 'dance_school/admin_dashboard.html', context)

def admin_add_record(request, table_name):
    if 'user' not in request.session or request.session['user'].get('role') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        try:
            if table_name == 'clients':
                AdminService.insert_client(
                    request.POST['phone'],
                    request.POST['full_name'],
                    request.POST['birth_date'],
                    request.POST.get('email'),
                    request.POST.get('parent_name'),
                    request.POST.get('status', 'активен')
                )
            elif table_name == 'dance_styles':
                AdminService.insert_dance_style(
                    request.POST['style_name'],
                    request.POST['difficulty_level'],
                    request.POST['target_age_group'],
                    request.POST.get('status', 'активно')
                )
            # Добавьте обработку для других таблиц по аналогии
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {e}")
    
    return render(request, 'dance_school/admin_add.html', {'table_name': table_name})

def admin_edit_record(request, table_name, record_id):
    if 'user' not in request.session or request.session['user'].get('role') != 'admin':
        return redirect('home')
    
    if request.method == 'POST':
        try:
            if table_name == 'clients':
                AdminService.update_client(
                    record_id,
                    request.POST.get('phone'),
                    request.POST.get('full_name'),
                    request.POST.get('birth_date'),
                    request.POST.get('email'),
                    request.POST.get('parent_name'),
                    request.POST.get('status')
                )
            # Добавьте обработку для других таблиц по аналогии
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {e}")
    
    # Получаем данные записи для редактирования
    record = DatabaseService.execute_query(f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE {table_name[:-1]}_id = %s", [record_id])
    return render(request, 'dance_school/admin_edit.html', {
        'table_name': table_name,
        'record': record[0] if record else None
    })

def admin_delete_record(request, table_name, record_id):
    if 'user' not in request.session or request.session['user'].get('role') != 'admin':
        return redirect('home')
    
    try:
        if table_name == 'clients':
            AdminService.delete_client(record_id)
        elif table_name == 'dance_styles':
            AdminService.delete_dance_style(record_id)
        # Добавьте обработку для других таблиц по аналогии
        
        return redirect('admin_dashboard')
    except Exception as e:
        return HttpResponse(f"Ошибка: {e}")

def home(request):

    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        from .services.auth_service import AuthService
        user = AuthService.authenticate(username, password)
        
        if user:
            # Сохраняем пользователя в сессии
            request.session['user'] = user
            # TODO: Перенаправлять на разные страницы в зависимости от роли
        else:
            error_message = "Неверный логин или пароль"
    # Получаем реальные данные из БД
    try:
        db_data = DatabaseService.get_schedule_data()
        schedule_data = []
        for item in db_data:
            schedule_data.append({
                'day': item[0],
                'time': str(item[1]) if item[1] else '',  # Преобразуем время в строку
                'style': item[2],
                'trainer': item[3]
            })
    except Exception as e:
        # Если ошибка - используем демо данные
        schedule_data = [
            {'day': 'Понедельник', 'time': '18:00', 'style': 'Сальса', 'trainer': 'Иванова Мария'},
            {'day': 'Вторник', 'time': '19:00', 'style': 'Бачата', 'trainer': 'Петров Алексей'},
            {'day': 'Среда', 'time': '17:00', 'style': 'Танго', 'trainer': 'Сидорова Анна'},
        ]
        print(f"Database error: {e}")  # Для отладки
    
    context = {
        'schedule_data': schedule_data
    }
    return render(request, 'dance_school/home.html', context)