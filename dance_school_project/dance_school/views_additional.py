from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from .services.database_service import DatabaseService

def function_demo(request):
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    context = {}
    
    # Демонстрация табличной функции
    if request.GET.get('weekday'):
        weekday = request.GET['weekday']
        try:
            schedule_data = DatabaseService.get_schedule_by_weekday(weekday)
            context['schedule_data'] = schedule_data
            context['weekday'] = weekday
        except Exception as e:
            context['error'] = f"Ошибка: {e}"
    
    # Демонстрация скалярной функции
    if request.GET.get('min_age') and request.GET.get('max_age'):
        try:
            min_age = int(request.GET['min_age'])
            max_age = int(request.GET['max_age'])
            client_count = DatabaseService.get_active_clients_by_age(min_age, max_age)
            context['client_count'] = client_count
            context['min_age'] = min_age
            context['max_age'] = max_age
        except Exception as e:
            context['error'] = f"Ошибка: {e}"
    
    # Демонстрация функции расчета скидки
    if request.GET.get('base_price'):
        try:
            base_price = float(request.GET['base_price'])
            client_age = int(request.GET.get('client_age', 30))
            reg_count = int(request.GET.get('reg_count', 1))
            
            final_price = DatabaseService.calculate_discount(base_price, client_age, reg_count)
            discount = ((base_price - final_price) / base_price) * 100
            
            context['discount_data'] = {
                'base_price': base_price,
                'final_price': final_price,
                'discount_percent': round(discount, 1),
                'client_age': client_age,
                'registration_count': reg_count
            }
        except Exception as e:
            context['error'] = f"Ошибка: {e}"
    
    return render(request, 'dance_school/function_demo.html', context)

def views_demo(request):
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        role = user_info.get('role')
    except:
        return redirect('home')
    
    context = {'role': role}
    
    try:
        if role == 'admin':
            admin_data = DatabaseService.get_admin_view()
            context['view_data'] = admin_data
            context['view_name'] = 'Административное представление'
        
        elif role == 'trainer':
            trainer_id = user_info.get('trainer_id', 1)  # По умолчанию
            trainer_data = DatabaseService.get_trainer_view(trainer_id)
            context['view_data'] = trainer_data
            context['view_name'] = 'Представление тренера'
        
        elif role == 'client':
            client_id = user_info.get('client_id', 1)  # По умолчанию
            client_data = DatabaseService.get_client_view(client_id)
            context['view_data'] = client_data
            context['view_name'] = 'Представление клиента'
    
    except Exception as e:
        context['error'] = f"Ошибка загрузки данных: {e}"
    
    return render(request, 'dance_school/views_demo.html', context)

def triggers_demo(request):
    user_cookie = request.COOKIES.get('user_info')
    if not user_cookie:
        return redirect('home')
    
    try:
        user_info = json.loads(user_cookie)
        if user_info.get('role') != 'admin':
            return redirect('home')
    except:
        return redirect('home')
    
    context = {}
    
    # Демонстрация работы триггеров
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'test_age_trigger':
            # Попытка записать несовершеннолетнего на взрослое занятие
            try:
                # Создаем тестового несовершеннолетнего клиента
                DatabaseService.execute_query("""
                    INSERT INTO clients_nesterovas_21_8 
                    (contact_phone_nesterovas_21_8, client_full_name_nesterovas_21_8, 
                     client_birth_date_nesterovas_21_8, client_status_nesterovas_21_8)
                    VALUES ('+79160001111', 'Тестовый Несовершеннолетний', '2010-01-01', 'активен')
                    RETURNING client_id
                """)
                result = DatabaseService.execute_query("SELECT lastval()")
                test_client_id = result[0][0] if result else None
                
                # Пытаемся записать на взрослое занятие (например, Стрип-пластика 21+)
                adult_style_id = DatabaseService.execute_query(
                    "SELECT dance_style_id FROM dance_styles_nesterovas_21_8 WHERE dance_style_name_nesterovas_21_8 LIKE '%Стрип%' LIMIT 1"
                )[0][0]
                
                schedule_id = DatabaseService.execute_query(
                    "SELECT schedule_id FROM schedules_nesterovas_21_8 WHERE dance_style_id = %s LIMIT 1",
                    [adult_style_id]
                )[0][0]
                
                # Эта запись должна вызвать ошибку триггера
                DatabaseService.execute_query(
                    "INSERT INTO registrations_nesterovas_21_8 (client_id, schedule_id, registration_datetime_nesterovas_21_8, admin_username_nesterovas_21_8) VALUES (%s, %s, NOW(), 'admin1')",
                    [test_client_id, schedule_id]
                )
                
                context['trigger_test'] = 'Триггер проверки возраста НЕ сработал (это ошибка!)'
                
            except Exception as e:
                context['trigger_test'] = f'Триггер проверки возраста сработал: {str(e)}'
        
        elif action == 'test_duplicate_trigger':
            # Попытка создать дублирующую запись
            try:
                # Берем существующую запись
                existing = DatabaseService.execute_query(
                    "SELECT client_id, schedule_id FROM registrations_nesterovas_21_8 LIMIT 1"
                )[0]
                
                # Пытаемся создать дубликат
                DatabaseService.execute_query(
                    "INSERT INTO registrations_nesterovas_21_8 (client_id, schedule_id, registration_datetime_nesterovas_21_8, admin_username_nesterovas_21_8) VALUES (%s, %s, NOW(), 'admin1')",
                    [existing[0], existing[1]]
                )
                
                context['trigger_test'] = 'Триггер проверки дубликатов НЕ сработал (это ошибка!)'
                
            except Exception as e:
                context['trigger_test'] = f'Триггер проверки дубликатов сработал: {str(e)}'
    
    return render(request, 'dance_school/triggers_demo.html', context)