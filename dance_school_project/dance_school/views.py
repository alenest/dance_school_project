from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
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
    """Админ панель с функциями ТЗ"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    action = request.GET.get('action', '')
    table = request.GET.get('table', '')
    id_to_edit = request.GET.get('id', '')
    
    # Обработка добавления/редактирования/удаления
    if request.method == 'POST':
        try:
            table_name = request.POST.get('table_name')
            action = request.POST.get('action')
            record_id = request.POST.get('record_id')
            
            if action == 'delete':
                DatabaseService.delete_record(table_name, record_id)
            elif action == 'edit':
                # Сохраняем данные формы в сессии для редактирования
                request.session['edit_data'] = {
                    'table': table_name,
                    'id': record_id,
                    'form_data': request.POST
                }
            elif action == 'save':
                # Сохраняем изменения
                form_data = dict(request.POST)
                DatabaseService.update_record(table_name, record_id, form_data)
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка обработки: {e}")
    
    # Получаем все данные для админ панели
    try:
        clients = DatabaseService.get_all_clients()
        trainers = DatabaseService.get_all_trainers()
        dance_styles = DatabaseService.get_all_dance_styles()
        halls = DatabaseService.get_all_halls()
        schedules = DatabaseService.get_all_schedules()
        registrations = DatabaseService.get_all_registrations()
        administrators = DatabaseService.get_all_administrators()
        training_periods = DatabaseService.get_all_training_periods()
        training_slots = DatabaseService.get_all_training_slots()
        
        # Статистика
        total_clients = len(clients)
        total_trainers = len(trainers)
        total_classes = len(schedules)
        active_classes = len([s for s in schedules if s[8] == 'активно'])
        
        context = {
            'user_info': user_info,
            'clients': clients,
            'trainers': trainers,
            'dance_styles': dance_styles,
            'halls': halls,
            'schedules': schedules,
            'registrations': registrations,
            'administrators': administrators,
            'training_periods': training_periods,
            'training_slots': training_slots,
            'total_clients': total_clients,
            'total_trainers': total_trainers,
            'total_classes': total_classes,
            'active_classes': active_classes,
            'action': action,
            'table': table,
            'id_to_edit': id_to_edit
        }
        
        return render(request, 'dance_school/admin_dashboard.html', context)
    
    except Exception as e:
        print(f"Ошибка загрузки данных: {e}")
        return HttpResponse(f"Ошибка загрузки данных: {e}")

def admin_edit_record(request):
    """Редактирование записи в админ панели"""
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    table = request.GET.get('table', '')
    record_id = request.GET.get('id', '')
    action = request.GET.get('action', 'edit')
    
    if request.method == 'POST':
        try:
            form_data = {k: v for k, v in request.POST.items() if k not in ['csrfmiddlewaretoken', 'table', 'action']}
            
            if action == 'add':
                DatabaseService.insert_record(table, form_data)
            elif action == 'edit':
                DatabaseService.update_record(table, record_id, form_data)
            
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка сохранения: {e}")
    
    # Получаем структуру таблицы и данные записи
    try:
        table_structure = DatabaseService.get_table_structure(table)
        record_data = None
        
        if record_id and action == 'edit':
            record_data = DatabaseService.get_record_by_id(table, record_id)
        
        context = {
            'user_info': user_info,
            'table': table,
            'record_id': record_id,
            'action': action,
            'table_structure': table_structure,
            'record_data': record_data[0] if record_data else None
        }
        
        return render(request, 'dance_school/admin_edit_record.html', context)
    
    except Exception as e:
        return HttpResponse(f"Ошибка загрузки формы: {e}")

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
            
            DatabaseService.delete_record(table, record_id)
            return redirect('admin_dashboard')
        except Exception as e:
            return HttpResponse(f"Ошибка удаления: {e}")
    
    return redirect('admin_dashboard')