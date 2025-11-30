from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from .services.database_service import DatabaseService
from .services.auth_service import AuthService
from .services.admin_service import AdminService

def home(request):
    error_message = None
    user_info = None
    
    # Проверяем пользователя через куки (простая реализация)
    user_cookie = request.COOKIES.get('user_info')
    if user_cookie:
        try:
            user_info = json.loads(user_cookie)
        except:
            pass
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = AuthService.authenticate(username, password)
        
        if user:
            user_info = user
            response = redirect('home')
            # Сохраняем в куки
            response.set_cookie('user_info', json.dumps(user_info))
            return response
        else:
            error_message = "Неверный логин или пароль"
    
    # Получаем данные расписания
    try:
        db_data = DatabaseService.get_schedule_data()
        schedule_data = []
        for item in db_data:
            schedule_data.append({
                'day': item[0],
                'time': str(item[1]) if item[1] else '',
                'style': item[2],
                'trainer': item[3]
            })
    except Exception as e:
        schedule_data = [
            {'day': 'Понедельник', 'time': '18:00', 'style': 'Сальса', 'trainer': 'Иванова Мария'},
            {'day': 'Вторник', 'time': '19:00', 'style': 'Бачата', 'trainer': 'Петров Алексей'},
            {'day': 'Среда', 'time': '17:00', 'style': 'Танго', 'trainer': 'Сидорова Анна'},
        ]
        print(f"Database error: {e}")
    
    context = {
        'schedule_data': schedule_data,
        'error_message': error_message,
        'user_info': user_info
    }
    return render(request, 'dance_school/home.html', context)

def logout(request):
    """Выход из системы"""
    response = redirect('home')
    response.delete_cookie('user_info')
    return response

def admin_dashboard(request):
    # Проверяем, что пользователь админ через куки
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    # Получаем данные для всех таблиц
    try:
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
    except Exception as e:
        context = {
            'error': f"Ошибка загрузки данных: {e}"
        }
    
    return render(request, 'dance_school/admin_dashboard.html', context)

def admin_add_record(request, table_name):
    # Проверяем авторизацию
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
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
            elif table_name == 'trainers':
                AdminService.insert_trainer(
                    request.POST['phone'],
                    request.POST['full_name'],
                    request.POST.get('email')
                )
            elif table_name == 'halls':
                AdminService.insert_hall(
                    int(request.POST['hall_number']),
                    int(request.POST['capacity'])
                )
            elif table_name == 'training_periods':
                AdminService.insert_training_period(
                    request.POST['start_date'],
                    request.POST['end_date']
                )
            elif table_name == 'training_slots':
                AdminService.insert_training_slot(
                    request.POST['start_time'],
                    request.POST['end_time']
                )
            elif table_name == 'administrators':
                AdminService.insert_administrator(
                    request.POST['username'],
                    request.POST['full_name'],
                    request.POST['position'],
                    request.POST['phone'],
                    request.POST['password_hash']
                )
            elif table_name == 'schedules':
                AdminService.insert_schedule(
                    int(request.POST['trainer_id']),
                    request.POST['weekday'],
                    request.POST['period_start_date'],
                    request.POST['class_start_time'],
                    int(request.POST['hall_number']),
                    int(request.POST['dance_style_id']),
                    float(request.POST['price']),
                    request.POST.get('status', 'активно')
                )
            elif table_name == 'registrations':
                AdminService.insert_registration(
                    int(request.POST['client_id']),
                    int(request.POST['schedule_id']),
                    request.POST['registration_datetime'],
                    request.POST['admin_username']
                )
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {str(e)}")
    
    return render(request, 'dance_school/admin_add.html', {'table_name': table_name})

def admin_edit_record(request, table_name, record_id):
    # Проверяем авторизацию
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
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
            elif table_name == 'dance_styles':
                AdminService.update_dance_style(
                    record_id,
                    request.POST.get('style_name'),
                    request.POST.get('difficulty_level'),
                    request.POST.get('target_age_group'),
                    request.POST.get('status')
                )
            elif table_name == 'trainers':
                AdminService.update_trainer(
                    record_id,
                    request.POST.get('phone'),
                    request.POST.get('full_name'),
                    request.POST.get('email')
                )
            elif table_name == 'halls':
                AdminService.update_hall(
                    int(request.POST['hall_number']),
                    int(request.POST['capacity'])
                )
            elif table_name == 'training_periods':
                AdminService.update_training_period(
                    request.POST['start_date'],
                    request.POST['end_date']
                )
            elif table_name == 'training_slots':
                AdminService.update_training_slot(
                    request.POST['start_time'],
                    request.POST['end_time']
                )
            elif table_name == 'administrators':
                AdminService.update_administrator(
                    request.POST['username'],
                    request.POST.get('full_name'),
                    request.POST.get('position'),
                    request.POST.get('phone'),
                    request.POST.get('password_hash')
                )
            elif table_name == 'schedules':
                AdminService.update_schedule(
                    record_id,
                    int(request.POST.get('trainer_id')) if request.POST.get('trainer_id') else None,
                    request.POST.get('weekday'),
                    request.POST.get('period_start_date'),
                    request.POST.get('class_start_time'),
                    int(request.POST.get('hall_number')) if request.POST.get('hall_number') else None,
                    int(request.POST.get('dance_style_id')) if request.POST.get('dance_style_id') else None,
                    float(request.POST.get('price')) if request.POST.get('price') else None,
                    request.POST.get('status')
                )
            elif table_name == 'registrations':
                AdminService.update_registration(
                    record_id,
                    int(request.POST.get('client_id')) if request.POST.get('client_id') else None,
                    int(request.POST.get('schedule_id')) if request.POST.get('schedule_id') else None,
                    request.POST.get('registration_datetime'),
                    request.POST.get('admin_username')
                )
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {str(e)}")
    
    # Получаем данные записи для редактирования
    try:
        if table_name == 'training_periods':
            record = DatabaseService.execute_query(
                f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE period_start_date_nesterovas_21_8 = %s", 
                [record_id]
            )
        elif table_name == 'training_slots':
            record = DatabaseService.execute_query(
                f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE class_start_time_nesterovas_21_8 = %s", 
                [record_id]
            )
        elif table_name == 'administrators':
            record = DatabaseService.execute_query(
                f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE admin_username_nesterovas_21_8 = %s", 
                [record_id]
            )
        elif table_name == 'halls':
            record = DatabaseService.execute_query(
                f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE hall_number_nesterovas_21_8 = %s", 
                [record_id]
            )
        else:
            record = DatabaseService.execute_query(
                f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE {table_name[:-1]}_id = %s", 
                [record_id]
            )
        
        return render(request, 'dance_school/admin_edit.html', {
            'table_name': table_name,
            'record': record[0] if record else None,
            'record_id': record_id
        })
    except Exception as e:
        return HttpResponse(f"Ошибка загрузки данных: {str(e)}")

def admin_delete_record(request, table_name, record_id):
    # Проверяем авторизацию
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    try:
        if table_name == 'clients':
            AdminService.delete_client(record_id)
        elif table_name == 'dance_styles':
            AdminService.delete_dance_style(record_id)
        elif table_name == 'trainers':
            AdminService.delete_trainer(record_id)
        elif table_name == 'halls':
            AdminService.delete_hall(int(record_id))
        elif table_name == 'training_periods':
            AdminService.delete_training_period(record_id)
        elif table_name == 'training_slots':
            AdminService.delete_training_slot(record_id)
        elif table_name == 'administrators':
            AdminService.delete_administrator(record_id)
        elif table_name == 'schedules':
            AdminService.delete_schedule(record_id)
        elif table_name == 'registrations':
            AdminService.delete_registration(record_id)
        
        return redirect('admin_dashboard')
    except Exception as e:
        return HttpResponse(f"Ошибка: {str(e)}")