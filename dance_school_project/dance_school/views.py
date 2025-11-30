from django.shortcuts import render

# Create your views here.

def home(request):
    # Пример данных для таблицы (временные данные)
    schedule_data = [
        {'day': 'Понедельник', 'time': '18:00', 'style': 'Сальса', 'trainer': 'Иванова Мария'},
        {'day': 'Вторник', 'time': '19:00', 'style': 'Бачата', 'trainer': 'Петров Алексей'},
        {'day': 'Среда', 'time': '17:00', 'style': 'Танго', 'trainer': 'Сидорова Анна'},
    ]
    
    context = {
        'schedule_data': schedule_data
    }
    return render(request, 'dance_school/home.html', context)