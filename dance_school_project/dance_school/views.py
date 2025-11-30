# dance_school/views.py
from django.shortcuts import render
from .services.database_service import DatabaseService

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