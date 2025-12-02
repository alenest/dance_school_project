from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
import traceback
from datetime import datetime, date, time  # Импорт datetime добавлен
from .services.database_service import DatabaseService

def home(request):
    """Главная страница с расписанием и функцией расчета скидки для клиентов"""
    error_message = None
    user_info = None
    discount_result = None
    
    # Проверяем авторизацию
    user_cookie = request.COOKIES.get('user_info')
    if user_cookie:
        try:
            user_info = json.loads(user_cookie)
        except:
            pass
    
    # Форма авторизации
    if request.method == 'POST' and 'login_form' in request.POST:
        role = request.POST.get('role', 'client')
        login_data = request.POST.get('login_data', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = DatabaseService.authenticate_user(login_data, password, role)
        
        if user:
            user_info = user
            response = redirect('home')
            response.set_cookie('user_info', json.dumps(user_info))
            return response
        else:
            error_message = "Неверные данные для входа"
    
    # Форма расчета скидки (для клиентов)
    if request.method == 'POST' and 'discount_form' in request.POST:
        if user_info and user_info.get('role') == 'client':
            try:
                base_price = float(request.POST.get('base_price', 0))
                client_age = int(request.POST.get('client_age', 30))
                registration_count = int(request.POST.get('registration_count', 1))
                
                final_price = DatabaseService.calculate_discount(base_price, client_age, registration_count)
                discount_percent = ((base_price - final_price) / base_price * 100) if base_price > 0 else 0
                
                discount_result = {
                    'base_price': base_price,
                    'final_price': final_price,
                    'discount_percent': round(discount_percent, 2),
                    'client_age': client_age,
                    'registration_count': registration_count
                }
            except Exception as e:
                discount_result = {'error': str(e)}
    
    # Получаем расписание
    try:
        schedule_data = DatabaseService.get_all_active_schedules()
        formatted_schedule = []
        for item in schedule_data:
            formatted_schedule.append({
                'id': item[0],
                'trainer': item[1],
                'style': item[2],
                'day': item[3],
                'start_time': item[4],
                'end_time': item[5],
                'hall': item[6] if item[6] is not None else 'Не указан',
                'capacity': item[7] if item[7] is not None else 0,
                'price': float(item[8]) if item[8] is not None else 0,
                'status': item[9],
                'registered': item[10] if item[10] is not None else 0,
                'available': item[11] if item[11] is not None else 0
            })
    except Exception as e:
        print(f"Ошибка получения расписания: {e}")
        formatted_schedule = []
    
    # Получаем статистику для главной страницы
    try:
        total_classes = len(formatted_schedule)
        total_trainers = len(DatabaseService.get_all_trainers())
        total_styles = len(DatabaseService.get_all_dance_styles())
    except:
        total_classes = 0
        total_trainers = 0
        total_styles = 0
    
    context = {
        'schedule_data': formatted_schedule,
        'total_classes': total_classes,
        'total_trainers': total_trainers,
        'total_styles': total_styles,
        'error_message': error_message,
        'user_info': user_info,
        'discount_result': discount_result
    }
    return render(request, 'dance_school/home.html', context)

def logout(request):
    """Выход из системы"""
    response = redirect('home')
    response.delete_cookie('user_info')
    return response

def public_schedule(request):
    """Публичное расписание (доступно без авторизации)"""
    weekday = request.GET.get('weekday', 'all')
    
    try:
        schedule_data = DatabaseService.get_schedule_by_weekday(weekday if weekday != 'all' else None)
        
        formatted_schedule = []
        for item in schedule_data:
            formatted_schedule.append({
                'id': item[0],
                'trainer': item[1],
                'style': item[2],
                'day': item[3],
                'start_time': item[4],
                'end_time': item[5],
                'hall': item[6] if item[6] is not None else 'Не указан',
                'capacity': item[7] if item[7] is not None else 0,
                'price': float(item[8]) if item[8] is not None else 0,
                'status': item[9],
                'registered': item[10] if item[10] is not None else 0,
                'available': item[11] if item[11] is not None else 0
            })
        
        context = {
            'schedule_data': formatted_schedule,
            'selected_weekday': weekday,
            'total_classes': len(formatted_schedule)
        }
        
        return render(request, 'dance_school/public_schedule.html', context)
    
    except Exception as e:
        print(f"Ошибка загрузки расписания: {e}")
        return HttpResponse(f"Ошибка загрузки расписания: {e}")

def trainer_dashboard(request):
    """Панель тренера"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'trainer':
            return redirect('home')
    except:
        return redirect('home')
    
    trainer_id = user_info.get('trainer_id')
    
    try:
        # Получаем расписания тренера
        schedules = DatabaseService.get_trainer_schedules(trainer_id)
        formatted_schedules = []
        for sched in schedules:
            formatted_schedules.append({
                'id': sched[0],
                'weekday': sched[1],
                'start_time': sched[2],
                'end_time': sched[3],
                'hall': sched[4],
                'style': sched[5],
                'price': float(sched[6]) if sched[6] else 0,
                'status': sched[7],
                'students': sched[8],
                'period_start': sched[9],
                'style_id': sched[10]
            })
        
        # Получаем учеников тренера
        students = DatabaseService.get_trainer_students(trainer_id)
        formatted_students = []
        for student in students:
            formatted_students.append({
                'id': student[0],
                'name': student[1],
                'phone': student[2],
                'email': student[3],
                'birth_date': student[4],
                'status': student[5],
                'style': student[6],
                'day': student[7],
                'time': student[8]
            })
        
        # Статистика
        students_count = DatabaseService.get_trainer_students_count(trainer_id)
        
        context = {
            'user_info': user_info,
            'schedules': formatted_schedules,
            'students': formatted_students,
            'students_count': students_count,
            'total_classes': len(formatted_schedules)
        }
        
        return render(request, 'dance_school/trainer_dashboard.html', context)
    
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return HttpResponse(f"Ошибка загрузки данных: {e}")

def trainer_edit_schedule(request, schedule_id):
    """Редактирование расписания тренера"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'trainer':
            return redirect('home')
    except:
        return redirect('home')
    
    if request.method == 'POST':
        try:
            weekday = request.POST.get('weekday')
            start_time = request.POST.get('start_time')
            hall_number = request.POST.get('hall_number')
            price = request.POST.get('price')
            status = request.POST.get('status')
            
            # Обновляем расписание
            DatabaseService.execute_query(
                """
                UPDATE schedules_nesterovas_21_8 
                SET class_weekday_nesterovas_21_8 = %s,
                    class_start_time_nesterovas_21_8 = %s::time,
                    hall_number_nesterovas_21_8 = %s::integer,
                    subscription_price_nesterovas_21_8 = %s::numeric,
                    schedule_status_nesterovas_21_8 = %s
                WHERE schedule_id = %s
                """,
                [weekday, start_time, hall_number, price, status, schedule_id]
            )
            
            return redirect('trainer_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка обновления: {e}")
    
    # Получаем данные расписания для формы
    try:
        schedule = DatabaseService.execute_query(
            "SELECT * FROM schedules_nesterovas_21_8 WHERE schedule_id = %s",
            [schedule_id]
        )
        
        if not schedule:
            return HttpResponse("Расписание не найдено")
        
        # Проверяем, что тренер редактирует свое расписание
        if schedule[0][1] != user_info.get('trainer_id'):
            return HttpResponse("Нет доступа к этому расписанию")
        
        # Получаем время окончания из таблицы слотов
        time_slot = DatabaseService.execute_query(
            "SELECT class_end_time_nesterovas_21_8 FROM training_slots_nesterovas_21_8 WHERE class_start_time_nesterovas_21_8 = %s",
            [schedule[0][4]]
        )
        
        end_time = time_slot[0][0] if time_slot else None
        
        halls = DatabaseService.get_all_halls()
        
        context = {
            'user_info': user_info,
            'schedule': {
                'id': schedule[0][0],
                'trainer_id': schedule[0][1],
                'weekday': schedule[0][2],
                'period_start': schedule[0][3],
                'start_time': schedule[0][4].strftime('%H:%M') if schedule[0][4] else '',
                'end_time': end_time.strftime('%H:%M') if end_time else '',
                'hall': schedule[0][5],
                'style_id': schedule[0][6],
                'price': float(schedule[0][7]) if schedule[0][7] else 0,
                'status': schedule[0][8]
            },
            'halls': halls
        }
        
        return render(request, 'dance_school/trainer_edit_schedule.html', context)
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return HttpResponse(f"Ошибка: {e}")

def admin_dashboard(request):
    """Админ панель с полным функционалом управления ВСЕМИ таблицами"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    # Обработка удаления записи
    if request.method == 'POST' and 'delete_record' in request.POST:
        try:
            table = request.POST.get('table')
            record_id = request.POST.get('record_id')
            DatabaseService.delete_record(table, record_id)
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка удаления: {e}")
    
    # Получаем ВСЕ данные из ВСЕХ таблиц для админ панели
    try:
        # Получаем данные из всех таблиц
        clients_data = DatabaseService.get_all_clients()
        trainers_data = DatabaseService.get_all_trainers()
        dance_styles_data = DatabaseService.get_all_dance_styles()
        halls_data = DatabaseService.get_all_halls()
        schedules_data = DatabaseService.get_all_schedules()
        registrations_data = DatabaseService.get_all_registrations()
        administrators_data = DatabaseService.get_all_administrators()
        training_periods_data = DatabaseService.get_all_training_periods()
        training_slots_data = DatabaseService.get_all_training_slots()
        
        # Форматируем данные для удобного отображения
        clients = []
        for client in clients_data:
            clients.append({
                'id': client[0],
                'phone': client[1],
                'full_name': client[2],
                'birth_date': client[3],
                'email': client[4],
                'parent_name': client[5],
                'status': client[6]
            })
        
        trainers = []
        for trainer in trainers_data:
            trainers.append({
                'id': trainer[0],
                'phone': trainer[1],
                'full_name': trainer[2],
                'email': trainer[3]
            })
        
        dance_styles = []
        for style in dance_styles_data:
            dance_styles.append({
                'id': style[0],
                'name': style[1],
                'difficulty': style[2],
                'age_group': style[3],
                'status': style[4]
            })
        
        halls = []
        for hall in halls_data:
            halls.append({
                'number': hall[0],
                'capacity': hall[1]
            })
        
        schedules = []
        for schedule in schedules_data:
            schedules.append({
                'id': schedule[0],
                'trainer_id': schedule[1],
                'weekday': schedule[2],
                'period_start': schedule[3],
                'start_time': schedule[4],
                'hall': schedule[5],
                'style_id': schedule[6],
                'price': schedule[7],
                'status': schedule[8],
                'trainer_name': schedule[9],
                'style_name': schedule[10]
            })
        
        registrations = []
        for reg in registrations_data:
            registrations.append({
                'id': reg[0],
                'client_id': reg[1],
                'schedule_id': reg[2],
                'datetime': reg[3],
                'admin_username': reg[4],
                'client_name': reg[5]
            })
        
        administrators = []
        for admin in administrators_data:
            administrators.append({
                'username': admin[0],
                'full_name': admin[1],
                'position': admin[2],
                'phone': admin[3],
                'password': admin[4]
            })
        
        training_periods = []
        for period in training_periods_data:
            training_periods.append({
                'start_date': period[0],
                'end_date': period[1]
            })
        
        training_slots = []
        for slot in training_slots_data:
            training_slots.append({
                'start_time': slot[0],
                'end_time': slot[1]
            })
        
        # Статистика
        total_clients = len(clients)
        total_trainers = len(trainers)
        total_classes = len(schedules)
        active_classes = len([s for s in schedules if s['status'] == 'активно'])
        
        context = {
            'user_info': user_info,
            # Все данные для отображения
            'clients': clients,
            'trainers': trainers,
            'dance_styles': dance_styles,
            'halls': halls,
            'schedules': schedules,
            'registrations': registrations,
            'administrators': administrators,
            'training_periods': training_periods,
            'training_slots': training_slots,
            # Статистика
            'total_clients': total_clients,
            'total_trainers': total_trainers,
            'total_classes': total_classes,
            'active_classes': active_classes,
            # Список всех таблиц для навигации
            'all_tables': [
                {'name': 'clients_nesterovas_21_8', 'display': 'Клиенты', 'data': clients},
                {'name': 'trainers_nesterovas_21_8', 'display': 'Тренеры', 'data': trainers},
                {'name': 'dance_styles_nesterovas_21_8', 'display': 'Направления танцев', 'data': dance_styles},
                {'name': 'halls_nesterovas_21_8', 'display': 'Залы', 'data': halls},
                {'name': 'schedules_nesterovas_21_8', 'display': 'Расписания', 'data': schedules},
                {'name': 'registrations_nesterovas_21_8', 'display': 'Регистрации', 'data': registrations},
                {'name': 'administrators_nesterovas_21_8', 'display': 'Администраторы', 'data': administrators},
                {'name': 'training_periods_nesterovas_21_8', 'display': 'Периоды занятий', 'data': training_periods},
                {'name': 'training_slots_nesterovas_21_8', 'display': 'Временные слоты', 'data': training_slots},
            ]
        }
        
        return render(request, 'dance_school/admin_dashboard.html', context)
    
    except Exception as e:
        print(f"Ошибка загрузки данных: {str(e)}")
        return HttpResponse(f"Ошибка загрузки данных: {str(e)}")

def admin_edit_record(request):
    """Редактирование существующей записи в админ панели (ИСПРАВЛЕННАЯ ВЕРСИЯ)"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    table_name = request.GET.get('table', '')
    record_id = request.GET.get('id', '')
    
    if not table_name:
        return HttpResponse("Не указана таблица")
    
    # Определяем primary key для таблицы
    pk_columns = {
        'clients_nesterovas_21_8': 'client_id',
        'trainers_nesterovas_21_8': 'trainer_id',
        'dance_styles_nesterovas_21_8': 'dance_style_id',
        'halls_nesterovas_21_8': 'hall_number_nesterovas_21_8',
        'schedules_nesterovas_21_8': 'schedule_id',
        'registrations_nesterovas_21_8': 'registration_id',
        'administrators_nesterovas_21_8': 'admin_username_nesterovas_21_8',
        'training_periods_nesterovas_21_8': 'period_start_date_nesterovas_21_8',
        'training_slots_nesterovas_21_8': 'class_start_time_nesterovas_21_8'
    }
    
    pk_column = pk_columns.get(table_name)
    if not pk_column:
        return HttpResponse("Неизвестная таблица")
    
    if request.method == 'POST':
        try:
            # Получаем все данные из формы
            form_data = {}
            for key, value in request.POST.items():
                if key not in ['csrfmiddlewaretoken', 'table', 'id', 'action']:
                    form_data[key] = value
            
            # В зависимости от таблицы вызываем соответствующую процедуру или функцию
            if table_name == 'clients_nesterovas_21_8':
                # Используем процедуру из базы данных для клиентов
                DatabaseService.execute_query(
                    "CALL update_client_nesterovas_21_8(%s, %s, %s, %s, %s, %s, %s)",
                    [
                        record_id,
                        form_data.get('contact_phone_nesterovas_21_8'),
                        form_data.get('client_full_name_nesterovas_21_8'),
                        form_data.get('client_birth_date_nesterovas_21_8'),
                        form_data.get('contact_email_nesterovas_21_8'),
                        form_data.get('parent_guardian_name_nesterovas_21_8'),
                        form_data.get('client_status_nesterovas_21_8')
                    ],
                    fetch=False
                )
                
            elif table_name == 'dance_styles_nesterovas_21_8':
                # Для остальных таблиц используем прямое обновление
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET dance_style_name_nesterovas_21_8 = %s,
                        difficulty_level_nesterovas_21_8 = %s,
                        target_age_group_nesterovas_21_8 = %s,
                        style_status_nesterovas_21_8 = %s
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('dance_style_name_nesterovas_21_8'),
                        form_data.get('difficulty_level_nesterovas_21_8'),
                        form_data.get('target_age_group_nesterovas_21_8'),
                        form_data.get('style_status_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'trainers_nesterovas_21_8':
                # Прямое обновление для тренеров
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET trainer_phone_nesterovas_21_8 = %s,
                        trainer_full_name_nesterovas_21_8 = %s,
                        trainer_email_nesterovas_21_8 = %s
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('trainer_phone_nesterovas_21_8'),
                        form_data.get('trainer_full_name_nesterovas_21_8'),
                        form_data.get('trainer_email_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'halls_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET hall_number_nesterovas_21_8 = %s::integer,
                        hall_capacity_nesterovas_21_8 = %s::integer
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('hall_number_nesterovas_21_8'),
                        form_data.get('hall_capacity_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'schedules_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET trainer_id = %s::integer,
                        class_weekday_nesterovas_21_8 = %s,
                        period_start_date_nesterovas_21_8 = %s::date,
                        class_start_time_nesterovas_21_8 = %s::time,
                        hall_number_nesterovas_21_8 = %s::integer,
                        dance_style_id = %s::integer,
                        subscription_price_nesterovas_21_8 = %s::numeric,
                        schedule_status_nesterovas_21_8 = %s
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('trainer_id'),
                        form_data.get('class_weekday_nesterovas_21_8'),
                        form_data.get('period_start_date_nesterovas_21_8'),
                        form_data.get('class_start_time_nesterovas_21_8'),
                        form_data.get('hall_number_nesterovas_21_8'),
                        form_data.get('dance_style_id'),
                        form_data.get('subscription_price_nesterovas_21_8'),
                        form_data.get('schedule_status_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'registrations_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET client_id = %s::integer,
                        schedule_id = %s::integer,
                        registration_datetime_nesterovas_21_8 = %s::timestamp,
                        admin_username_nesterovas_21_8 = %s
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('client_id'),
                        form_data.get('schedule_id'),
                        form_data.get('registration_datetime_nesterovas_21_8'),
                        form_data.get('admin_username_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'administrators_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET admin_username_nesterovas_21_8 = %s,
                        admin_full_name_nesterovas_21_8 = %s,
                        admin_position_nesterovas_21_8 = %s,
                        admin_phone_nesterovas_21_8 = %s,
                        admin_password_hash_nesterovas_21_8 = %s
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('admin_username_nesterovas_21_8'),
                        form_data.get('admin_full_name_nesterovas_21_8'),
                        form_data.get('admin_position_nesterovas_21_8'),
                        form_data.get('admin_phone_nesterovas_21_8'),
                        form_data.get('admin_password_hash_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'training_periods_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET period_start_date_nesterovas_21_8 = %s::date,
                        period_end_date_nesterovas_21_8 = %s::date
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('period_start_date_nesterovas_21_8'),
                        form_data.get('period_end_date_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
                
            elif table_name == 'training_slots_nesterovas_21_8':
                DatabaseService.execute_query(
                    f"""
                    UPDATE {table_name} 
                    SET class_start_time_nesterovas_21_8 = %s::time,
                        class_end_time_nesterovas_21_8 = %s::time
                    WHERE {pk_column} = %s
                    """,
                    [
                        form_data.get('class_start_time_nesterovas_21_8'),
                        form_data.get('class_end_time_nesterovas_21_8'),
                        record_id
                    ],
                    fetch=False
                )
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка сохранения: {str(e)}")
    
    # GET запрос - отображаем форму редактирования
    try:
        # Получаем структуру таблицы
        table_structure = DatabaseService.get_table_structure(table_name)
        
        # Получаем данные записи
        record_data = None
        if record_id:
            record_result = DatabaseService.get_record_by_id(table_name, record_id)
            if record_result:
                record_data = record_result[0]
        
        # Определяем friendly-имена для таблиц
        table_display_names = {
            'clients_nesterovas_21_8': 'Клиенты',
            'trainers_nesterovas_21_8': 'Тренеры',
            'dance_styles_nesterovas_21_8': 'Направления танцев',
            'halls_nesterovas_21_8': 'Залы',
            'schedules_nesterovas_21_8': 'Расписания',
            'registrations_nesterovas_21_8': 'Регистрации',
            'administrators_nesterovas_21_8': 'Администраторы',
            'training_periods_nesterovas_21_8': 'Периоды занятий',
            'training_slots_nesterovas_21_8': 'Временные слоты'
        }
        
        # Подготавливаем данные для шаблона
        columns_data = []
        for i, column in enumerate(table_structure):
            column_name = column[0]
            data_type = column[1]
            is_nullable = column[2] == 'YES'
            
            # Определяем текущее значение
            current_value = ''
            if record_data and i < len(record_data):
                current_value = record_data[i]
                # Преобразуем даты и время в строки для отображения в форме
                if current_value:
                    try:
                        if isinstance(current_value, (date, datetime)):
                            current_value = current_value.strftime('%Y-%m-%d')
                        elif isinstance(current_value, time):
                            current_value = current_value.strftime('%H:%M')
                    except:
                        pass  # Оставляем как есть, если не удалось преобразовать
            
            columns_data.append({
                'name': column_name,
                'data_type': data_type,
                'is_nullable': is_nullable,
                'current_value': str(current_value) if current_value is not None else ''
            })
        
        context = {
            'user_info': user_info,
            'table_name': table_name,
            'table_display': table_display_names.get(table_name, table_name),
            'record_id': record_id,
            'columns_data': columns_data,
            'action': 'edit' if record_id else 'add'
        }
        
        return render(request, 'dance_school/admin_edit_record.html', context)
    
    except Exception as e:
        print(f"Ошибка загрузки формы: {str(e)}")
        traceback.print_exc()
        return HttpResponse(f"Ошибка загрузки формы: {str(e)}")

def admin_delete_record(request):
    """Удаление записи в админ панели"""
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
            table = request.POST.get('table')
            record_id = request.POST.get('id')
            
            if table and record_id:
                # Для клиентов используем функцию из базы данных
                if table == 'clients_nesterovas_21_8':
                    DatabaseService.execute_query(
                        "SELECT delete_client_void_nesterovas_21_8(%s)",
                        [record_id],
                        fetch=False
                    )
                else:
                    DatabaseService.delete_record(table, record_id)
                return redirect('admin_dashboard')
            else:
                return HttpResponse("Не указана таблица или ID записи")
        except Exception as e:
            return HttpResponse(f"Ошибка удаления: {str(e)}")
    
    # Если GET запрос, показываем форму подтверждения
    table = request.GET.get('table', '')
    record_id = request.GET.get('id', '')
    
    context = {
        'user_info': user_info,
        'table': table,
        'record_id': record_id
    }
    
    return render(request, 'dance_school/admin_delete_record.html', context)