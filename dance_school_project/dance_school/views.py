from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from datetime import date, time, datetime
from .services.database_service import DatabaseService
from .services.auth_service import AuthService
from .services.admin_service import AdminService

def home(request):
    error_message = None
    user_info = None
    
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
            response.set_cookie('user_info', json.dumps(user_info))
            return response
        else:
            error_message = "Неверный логин или пароль"
    
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
    
    context = {
        'schedule_data': schedule_data,
        'error_message': error_message,
        'user_info': user_info
    }
    return render(request, 'dance_school/home.html', context)

def logout(request):
    response = redirect('home')
    response.delete_cookie('user_info')
    return response

def admin_dashboard(request):
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
        context = {'error': f"Ошибка загрузки данных: {e}"}
    
    return render(request, 'dance_school/admin_dashboard.html', context)

def admin_add_record(request, table_name):
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
                # Обрабатываем пустые поля как None
                phone = request.POST['phone'].strip() or None
                full_name = request.POST['full_name'].strip() or None
                birth_date = request.POST['birth_date'].strip() or None
                email = request.POST.get('email', '').strip() or None
                parent_name = request.POST.get('parent_name', '').strip() or None
                status = request.POST.get('status', 'активен').strip() or None
                
                AdminService.insert_client(
                    phone, full_name, birth_date, email, parent_name, status
                )
                
            elif table_name == 'dance_styles':
                style_name = request.POST['style_name'].strip() or None
                difficulty_level = request.POST['difficulty_level'].strip() or None
                target_age_group = request.POST['target_age_group'].strip() or None
                status = request.POST.get('status', 'активно').strip() or None
                
                AdminService.insert_dance_style(
                    style_name, difficulty_level, target_age_group, status
                )
                
            elif table_name == 'trainers':
                phone = request.POST['phone'].strip() or None
                full_name = request.POST['full_name'].strip() or None
                email = request.POST.get('email', '').strip() or None
                
                AdminService.insert_trainer(phone, full_name, email)
                
            elif table_name == 'halls':
                hall_number = int(request.POST['hall_number'])
                capacity = int(request.POST['capacity'])
                
                AdminService.insert_hall(hall_number, capacity)
                
            elif table_name == 'training_periods':
                start_date = request.POST['start_date'].strip() or None
                end_date = request.POST['end_date'].strip() or None
                
                AdminService.insert_training_period(start_date, end_date)
                
            elif table_name == 'training_slots':
                start_time = request.POST['start_time'].strip() or None
                end_time = request.POST['end_time'].strip() or None
                
                AdminService.insert_training_slot(start_time, end_time)
                
            elif table_name == 'administrators':
                username = request.POST['username'].strip() or None
                full_name = request.POST['full_name'].strip() or None
                position = request.POST['position'].strip() or None
                phone = request.POST['phone'].strip() or None
                password_hash = request.POST['password_hash'].strip() or None
                
                AdminService.insert_administrator(
                    username, full_name, position, phone, password_hash
                )
                
            elif table_name == 'schedules':
                trainer_id = int(request.POST['trainer_id'])
                weekday = request.POST['weekday'].strip() or None
                period_start_date = request.POST['period_start_date'].strip() or None
                class_start_time = request.POST['class_start_time'].strip() or None
                hall_number = int(request.POST['hall_number'])
                dance_style_id = int(request.POST['dance_style_id'])
                price = float(request.POST['price'])
                status = request.POST.get('status', 'активно').strip() or None
                
                AdminService.insert_schedule(
                    trainer_id, weekday, period_start_date, class_start_time, 
                    hall_number, dance_style_id, price, status
                )
                
            elif table_name == 'registrations':
                client_id = int(request.POST['client_id'])
                schedule_id = int(request.POST['schedule_id'])
                registration_datetime = request.POST['registration_datetime'].strip() or None
                admin_username = request.POST['admin_username'].strip() or None
                
                AdminService.insert_registration(
                    client_id, schedule_id, registration_datetime, admin_username
                )
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {e}")
    
    return render(request, 'dance_school/admin_add.html', {'table_name': table_name})

def admin_edit_record(request, table_name, record_id):
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    # Преобразуем record_id в правильный тип в зависимости от таблицы
    converted_record_id = record_id
    if table_name in ['clients', 'dance_styles', 'trainers', 'schedules', 'registrations']:
        converted_record_id = int(record_id)
    elif table_name == 'halls':
        converted_record_id = int(record_id)
    elif table_name == 'training_periods':
        converted_record_id = record_id  # Оставляем как строку для даты
    elif table_name == 'training_slots':
        converted_record_id = record_id  # Оставляем как строку для времени
    elif table_name == 'administrators':
        converted_record_id = record_id  # Оставляем как строку для username
    
    if request.method == 'POST':
        try:
            if table_name == 'clients':
                # Обрабатываем пустые поля как None
                phone = request.POST.get('phone', '').strip() or None
                full_name = request.POST.get('full_name', '').strip() or None
                birth_date = request.POST.get('birth_date', '').strip() or None
                email = request.POST.get('email', '').strip() or None
                parent_name = request.POST.get('parent_name', '').strip() or None
                status = request.POST.get('status', '').strip() or None
                
                AdminService.update_client(
                    converted_record_id, phone, full_name, birth_date, email, parent_name, status
                )
                
            elif table_name == 'dance_styles':
                style_name = request.POST.get('style_name', '').strip() or None
                difficulty_level = request.POST.get('difficulty_level', '').strip() or None
                target_age_group = request.POST.get('target_age_group', '').strip() or None
                status = request.POST.get('status', '').strip() or None
                
                AdminService.update_dance_style(
                    converted_record_id, style_name, difficulty_level, target_age_group, status
                )
                
            elif table_name == 'trainers':
                phone = request.POST.get('phone', '').strip() or None
                full_name = request.POST.get('full_name', '').strip() or None
                email = request.POST.get('email', '').strip() or None
                
                AdminService.update_trainer(converted_record_id, phone, full_name, email)
                
            elif table_name == 'halls':
                hall_number = int(request.POST.get('hall_number', 0)) or None
                capacity = int(request.POST.get('capacity', 0)) or None
                
                # Для залов используем прямое обновление, так как первичный ключ может меняться
                if hall_number and capacity:
                    DatabaseService.execute_query(
                        "UPDATE halls_nesterovas_21_8 SET hall_number_nesterovas_21_8 = %s, hall_capacity_nesterovas_21_8 = %s WHERE hall_number_nesterovas_21_8 = %s",
                        [hall_number, capacity, converted_record_id]
                    )
                
            elif table_name == 'training_periods':
                start_date = request.POST.get('start_date', '').strip() or None
                end_date = request.POST.get('end_date', '').strip() or None
                
                # Для периодов используем прямое обновление
                if start_date and end_date:
                    DatabaseService.execute_query(
                        "UPDATE training_periods_nesterovas_21_8 SET period_start_date_nesterovas_21_8 = %s, period_end_date_nesterovas_21_8 = %s WHERE period_start_date_nesterovas_21_8 = %s",
                        [start_date, end_date, converted_record_id]
                    )
                
            elif table_name == 'training_slots':
                start_time = request.POST.get('start_time', '').strip() or None
                end_time = request.POST.get('end_time', '').strip() or None
                
                # Для временных слотов используем прямое обновление
                if start_time and end_time:
                    DatabaseService.execute_query(
                        "UPDATE training_slots_nesterovas_21_8 SET class_start_time_nesterovas_21_8 = %s, class_end_time_nesterovas_21_8 = %s WHERE class_start_time_nesterovas_21_8 = %s",
                        [start_time, end_time, converted_record_id]
                    )
                
            elif table_name == 'administrators':
                username = request.POST.get('username', '').strip() or None
                full_name = request.POST.get('full_name', '').strip() or None
                position = request.POST.get('position', '').strip() or None
                phone = request.POST.get('phone', '').strip() or None
                password_hash = request.POST.get('password_hash', '').strip() or None
                
                # Для администраторов используем прямое обновление
                if username and full_name:
                    DatabaseService.execute_query(
                        "UPDATE administrators_nesterovas_21_8 SET admin_username_nesterovas_21_8 = %s, admin_full_name_nesterovas_21_8 = %s, admin_position_nesterovas_21_8 = %s, admin_phone_nesterovas_21_8 = %s, admin_password_hash_nesterovas_21_8 = %s WHERE admin_username_nesterovas_21_8 = %s",
                        [username, full_name, position, phone, password_hash, converted_record_id]
                    )
                
            elif table_name == 'schedules':
                trainer_id = int(request.POST.get('trainer_id', 0)) or None
                weekday = request.POST.get('weekday', '').strip() or None
                period_start_date = request.POST.get('period_start_date', '').strip() or None
                class_start_time = request.POST.get('class_start_time', '').strip() or None
                hall_number = int(request.POST.get('hall_number', 0)) or None
                dance_style_id = int(request.POST.get('dance_style_id', 0)) or None
                price = float(request.POST.get('price', 0)) or None
                status = request.POST.get('status', '').strip() or None
                
                AdminService.update_schedule(
                    converted_record_id, trainer_id, weekday, period_start_date, 
                    class_start_time, hall_number, dance_style_id, price, status
                )
                
            elif table_name == 'registrations':
                client_id = int(request.POST.get('client_id', 0)) or None
                schedule_id = int(request.POST.get('schedule_id', 0)) or None
                registration_datetime = request.POST.get('registration_datetime', '').strip() or None
                admin_username = request.POST.get('admin_username', '').strip() or None
                
                AdminService.update_registration(
                    converted_record_id, client_id, schedule_id, registration_datetime, admin_username
                )
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка: {e}")
    
    try:
        # Формируем правильный SQL запрос в зависимости от типа первичного ключа
        pk_column = get_primary_key_column(table_name)
        record = DatabaseService.execute_query(
            f"SELECT * FROM {table_name}_nesterovas_21_8 WHERE {pk_column} = %s", 
            [converted_record_id]
        )
        
        return render(request, 'dance_school/admin_edit.html', {
            'table_name': table_name,
            'record': record[0] if record else None
        })
    except Exception as e:
        return HttpResponse(f"Ошибка загрузки данных: {e}")

def admin_delete_record(request, table_name, record_id):
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    # Преобразуем record_id в правильный тип
    converted_record_id = record_id
    if table_name in ['clients', 'dance_styles', 'trainers', 'schedules', 'registrations']:
        converted_record_id = int(record_id)
    elif table_name == 'halls':
        converted_record_id = int(record_id)
    
    try:
        if table_name == 'clients':
            AdminService.delete_client(converted_record_id)
        elif table_name == 'dance_styles':
            AdminService.delete_dance_style(converted_record_id)
        elif table_name == 'trainers':
            AdminService.delete_trainer(converted_record_id)
        elif table_name == 'halls':
            AdminService.delete_hall(converted_record_id)
        elif table_name == 'training_periods':
            AdminService.delete_training_period(converted_record_id)
        elif table_name == 'training_slots':
            AdminService.delete_training_slot(converted_record_id)
        elif table_name == 'administrators':
            AdminService.delete_administrator(converted_record_id)
        elif table_name == 'schedules':
            AdminService.delete_schedule(converted_record_id)
        elif table_name == 'registrations':
            AdminService.delete_registration(converted_record_id)
        
        return redirect('admin_dashboard')
    except Exception as e:
        return HttpResponse(f"Ошибка: {e}")

def get_primary_key_column(table_name):
    """Возвращает имя первичного ключа для таблицы"""
    pk_columns = {
        'clients': 'client_id',
        'dance_styles': 'dance_style_id',
        'trainers': 'trainer_id',
        'halls': 'hall_number_nesterovas_21_8',
        'training_periods': 'period_start_date_nesterovas_21_8',
        'training_slots': 'class_start_time_nesterovas_21_8',
        'administrators': 'admin_username_nesterovas_21_8',
        'schedules': 'schedule_id',
        'registrations': 'registration_id'
    }
    return pk_columns.get(table_name, f"{table_name[:-1]}_id")