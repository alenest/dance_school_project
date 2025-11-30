# dance_school/services/database_service.py
import psycopg2
from django.conf import settings

class DatabaseService:
    @staticmethod
    def get_connection():
        """Создает соединение с базой данных"""
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
    
    @staticmethod
    def execute_query(query, params=None):
        """Выполняет SQL запрос и возвращает результат"""
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
            else:
                conn.commit()
                result = None
            return result
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_schedule_data():
        """Получает данные расписания из БД"""
        query = """
        SELECT 
            class_weekday_nesterovas_21_8 as day,
            class_start_time_nesterovas_21_8 as time,
            ds.dance_style_name_nesterovas_21_8 as style,
            t.trainer_full_name_nesterovas_21_8 as trainer
        FROM schedules_nesterovas_21_8 s
        JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
        JOIN dance_styles_nesterovas_21_8 ds ON s.dance_style_id = ds.dance_style_id
        WHERE s.schedule_status_nesterovas_21_8 = 'активно'
        LIMIT 10
        """
        return DatabaseService.execute_query(query)