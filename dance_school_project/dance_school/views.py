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
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        
        user = DatabaseService.authenticate_user(email=email, phone=phone, password=password)
        
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
                'hall': item[6],
                'capacity': item[7],
                'price': float(item[8]),
                'status': item[9],
                'registered': item[10],
                'available': item[11]
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
                'hall': item[6],
                'capacity': item[7],
                'price': float(item[8]),
                'status': item[9],
                'registered': item[10],
                'available': item[11]
            })
        
        context = {
            'schedule_data': formatted_schedule,
            'selected_weekday': weekday,
            'total_classes': len(formatted_schedule)
        }
        
        return render(request, 'dance_school/public_schedule.html', context)
    
    except Exception as e:
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
                'price': float(sched[6]),
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
    
    # Получаем данные расписания
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
        
        # Получаем все залы
        halls = DatabaseService.get_all_halls()
        
        # Получаем информацию о слоте времени
        time_slot = DatabaseService.execute_query(
            "SELECT * FROM training_slots_nesterovas_21_8 WHERE class_start_time_nesterovas_21_8 = %s",
            [schedule[0][4]]
        )
        
        if request.method == 'POST':
            try:
                data = {
                    'weekday': request.POST.get('weekday'),
                    'hall_number': int(request.POST.get('hall_number', 0)),
                    'price': float(request.POST.get('price', 0)),
                    'status': request.POST.get('status', 'активно')
                }
                
                # Обновляем расписание
                DatabaseService.execute_query(
                    """
                    UPDATE schedules_nesterovas_21_8 
                    SET class_weekday_nesterovas_21_8 = %s, 
                        hall_number_nesterovas_21_8 = %s, 
                        subscription_price_nesterovas_21_8 = %s,
                        schedule_status_nesterovas_21_8 = %s
                    WHERE schedule_id = %s
                    """,
                    [data['weekday'], data['hall_number'], data['price'], data['status'], schedule_id]
                )
                
                return redirect('trainer_dashboard')
            except Exception as e:
                return HttpResponse(f"Ошибка обновления: {e}")
        
        # Формируем контекст для отображения формы
        context = {
            'user_info': user_info,
            'schedule': {
                'id': schedule[0][0],
                'trainer_id': schedule[0][1],
                'weekday': schedule[0][2],
                'period_start': schedule[0][3],
                'start_time': schedule[0][4].strftime('%H:%M') if hasattr(schedule[0][4], 'strftime') else schedule[0][4],
                'end_time': time_slot[0][1].strftime('%H:%M') if time_slot and hasattr(time_slot[0][1], 'strftime') else '',
                'hall': schedule[0][5],
                'style_id': schedule[0][6],
                'price': float(schedule[0][7]),
                'status': schedule[0][8]
            },
            'halls': halls
        }
        
        return render(request, 'dance_school/trainer_edit_schedule.html', context)
    
    except Exception as e:
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
    
    # Обработка функции подсчета клиентов по возрасту
    age_count_result = None
    if request.method == 'POST' and 'age_count_form' in request.POST:
        try:
            min_age = int(request.POST.get('min_age', 18))
            max_age = int(request.POST.get('max_age', 40))
            count = DatabaseService.get_active_clients_by_age(min_age, max_age)
            age_count_result = {
                'min_age': min_age,
                'max_age': max_age,
                'count': count
            }
        except Exception as e:
            age_count_result = {'error': str(e)}
    
    # Получаем все данные для админ панели
    try:
        clients = DatabaseService.get_all_clients()
        trainers = DatabaseService.get_all_trainers()
        dance_styles = DatabaseService.get_all_dance_styles()
        halls = DatabaseService.get_all_halls()
        schedules = DatabaseService.get_all_schedules()
        registrations = DatabaseService.get_all_registrations()
        
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
            'age_count_result': age_count_result,
            'total_clients': total_clients,
            'total_trainers': total_trainers,
            'total_classes': total_classes,
            'active_classes': active_classes
        }
        
        return render(request, 'dance_school/admin_dashboard.html', context)
    
    except Exception as e:
        return HttpResponse(f"Ошибка загрузки данных: {e}")