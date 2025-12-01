import psycopg2
from django.conf import settings
from decimal import Decimal
import traceback

class DatabaseService:
    @staticmethod
    def get_connection():
        return psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        )
    
    @staticmethod
    def execute_query(query, params=None):
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('WITH'):
                result = cur.fetchall()
            else:
                conn.commit()
                result = None
            return result
        except Exception as e:
            conn.rollback()
            print(f"Ошибка выполнения запроса: {e}")
            print(f"Запрос: {query}")
            print(f"Параметры: {params}")
            raise e
        finally:
            cur.close()
            conn.close()
    
    # Основные методы для главной страницы
    @staticmethod
    def get_all_active_schedules():
        """Получить все активные расписания для главной страницы"""
        query = """
        SELECT 
            s.schedule_id,
            t.trainer_full_name_nesterovas_21_8,
            d.dance_style_name_nesterovas_21_8,
            s.class_weekday_nesterovas_21_8,
            TO_CHAR(s.class_start_time_nesterovas_21_8, 'HH24:MI') as start_time,
            TO_CHAR(ts.class_end_time_nesterovas_21_8, 'HH24:MI') as end_time,
            s.hall_number_nesterovas_21_8,
            h.hall_capacity_nesterovas_21_8,
            s.subscription_price_nesterovas_21_8,
            s.schedule_status_nesterovas_21_8,
            COALESCE(reg.registration_count, 0) as current_registrations,
            h.hall_capacity_nesterovas_21_8 - COALESCE(reg.registration_count, 0) as available_spots
        FROM schedules_nesterovas_21_8 s
        JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
        JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
        JOIN training_slots_nesterovas_21_8 ts ON s.class_start_time_nesterovas_21_8 = ts.class_start_time_nesterovas_21_8
        JOIN halls_nesterovas_21_8 h ON s.hall_number_nesterovas_21_8 = h.hall_number_nesterovas_21_8
        LEFT JOIN (
            SELECT r.schedule_id, COUNT(*) as registration_count
            FROM registrations_nesterovas_21_8 r
            GROUP BY r.schedule_id
        ) reg ON s.schedule_id = reg.schedule_id
        WHERE s.schedule_status_nesterovas_21_8 = 'активно'
        ORDER BY 
            CASE s.class_weekday_nesterovas_21_8
                WHEN 'Понедельник' THEN 1
                WHEN 'Вторник' THEN 2
                WHEN 'Среда' THEN 3
                WHEN 'Четверг' THEN 4
                WHEN 'Пятница' THEN 5
                WHEN 'Суббота' THEN 6
                WHEN 'Воскресенье' THEN 7
                ELSE 8
            END,
            s.class_start_time_nesterovas_21_8
        """
        return DatabaseService.execute_query(query)
    
    @staticmethod
    def get_schedule_by_weekday(weekday=None):
        """Табличная функция: возвращает расписание по дню недели (без авторизации)"""
        try:
            if weekday and weekday != 'all':
                query = "SELECT * FROM get_schedule_by_weekday_nesterovas_21_8(%s)"
                return DatabaseService.execute_query(query, [weekday])
            else:
                # Все активные расписания
                return DatabaseService.get_all_active_schedules()
        except Exception as e:
            print(f"Ошибка в get_schedule_by_weekday: {e}")
            return []
    
    @staticmethod
    def get_active_clients_by_age(min_age, max_age):
        """Скалярная функция: количество клиентов по возрасту (для админов)"""
        try:
            query = "SELECT get_active_clients_by_age_nesterovas_21_8(%s, %s)"
            result = DatabaseService.execute_query(query, [min_age, max_age])
            return int(result[0][0]) if result and result[0] else 0
        except Exception as e:
            print(f"Error in get_active_clients_by_age: {e}")
            return 0
    
    @staticmethod
    def calculate_discount(base_price, client_age, registration_count):
        """Функция расчета скидки (для клиентов)"""
        try:
            query = "SELECT calculate_discount_simple_nesterovas_21_8(%s, %s, %s)"
            result = DatabaseService.execute_query(query, [float(base_price), client_age, registration_count])
            return float(result[0][0]) if result and result[0] else float(base_price)
        except Exception as e:
            print(f"Error in calculate_discount: {e}")
            return float(base_price)
    
    # Методы для авторизации
    @staticmethod
    def authenticate_user(email=None, phone=None, password=None):
        """Универсальная авторизация по email/телефону"""
        if not email and not phone:
            return None
        
        try:
            # Проверяем администратора
            if email and password:
                admin_query = """
                SELECT admin_username_nesterovas_21_8, admin_full_name_nesterovas_21_8 
                FROM administrators_nesterovas_21_8 
                WHERE admin_username_nesterovas_21_8 = %s AND admin_password_hash_nesterovas_21_8 = %s
                """
                admin = DatabaseService.execute_query(admin_query, [email, password])
                if admin:
                    return {
                        'role': 'admin',
                        'username': admin[0][0],
                        'full_name': admin[0][1]
                    }
            
            # Проверяем тренера (по email или телефону)
            trainer_query = """
            SELECT trainer_id, trainer_full_name_nesterovas_21_8, trainer_email_nesterovas_21_8, trainer_phone_nesterovas_21_8
            FROM trainers_nesterovas_21_8 
            WHERE (trainer_email_nesterovas_21_8 = %s OR trainer_phone_nesterovas_21_8 = %s)
            """
            trainer = DatabaseService.execute_query(trainer_query, [email or phone, phone or email])
            if trainer:
                return {
                    'role': 'trainer',
                    'trainer_id': trainer[0][0],
                    'full_name': trainer[0][1],
                    'email': trainer[0][2],
                    'phone': trainer[0][3]
                }
            
            # Проверяем клиента (по email или телефону)
            client_query = """
            SELECT client_id, client_full_name_nesterovas_21_8, contact_email_nesterovas_21_8, contact_phone_nesterovas_21_8
            FROM clients_nesterovas_21_8 
            WHERE (contact_email_nesterovas_21_8 = %s OR contact_phone_nesterovas_21_8 = %s)
            """
            client = DatabaseService.execute_query(client_query, [email or phone, phone or email])
            if client:
                return {
                    'role': 'client',
                    'client_id': client[0][0],
                    'full_name': client[0][1],
                    'email': client[0][2],
                    'phone': client[0][3]
                }
                
        except Exception as e:
            print(f"Auth error: {e}")
        
        return None
    
    # Методы для тренерской панели
    @staticmethod
    def get_trainer_schedules(trainer_id):
        """Получить расписания тренера"""
        query = """
        SELECT 
            s.schedule_id,
            s.class_weekday_nesterovas_21_8,
            s.class_start_time_nesterovas_21_8,
            ts.class_end_time_nesterovas_21_8,
            s.hall_number_nesterovas_21_8,
            d.dance_style_name_nesterovas_21_8,
            s.subscription_price_nesterovas_21_8,
            s.schedule_status_nesterovas_21_8,
            COALESCE(reg.registration_count, 0) as students_count,
            s.period_start_date_nesterovas_21_8,
            s.dance_style_id
        FROM schedules_nesterovas_21_8 s
        JOIN training_slots_nesterovas_21_8 ts ON s.class_start_time_nesterovas_21_8 = ts.class_start_time_nesterovas_21_8
        JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
        LEFT JOIN (
            SELECT schedule_id, COUNT(*) as registration_count
            FROM registrations_nesterovas_21_8
            GROUP BY schedule_id
        ) reg ON s.schedule_id = reg.schedule_id
        WHERE s.trainer_id = %s
        ORDER BY s.class_weekday_nesterovas_21_8, s.class_start_time_nesterovas_21_8
        """
        return DatabaseService.execute_query(query, [trainer_id])
    
    @staticmethod
    def get_trainer_students(trainer_id):
        """Получить всех учеников тренера"""
        query = """
        SELECT DISTINCT
            c.client_id,
            c.client_full_name_nesterovas_21_8,
            c.contact_phone_nesterovas_21_8,
            c.contact_email_nesterovas_21_8,
            c.client_birth_date_nesterovas_21_8,
            c.client_status_nesterovas_21_8,
            d.dance_style_name_nesterovas_21_8,
            s.class_weekday_nesterovas_21_8,
            TO_CHAR(s.class_start_time_nesterovas_21_8, 'HH24:MI') as start_time
        FROM clients_nesterovas_21_8 c
        JOIN registrations_nesterovas_21_8 r ON c.client_id = r.client_id
        JOIN schedules_nesterovas_21_8 s ON r.schedule_id = s.schedule_id
        JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
        WHERE s.trainer_id = %s
        ORDER BY c.client_full_name_nesterovas_21_8
        """
        return DatabaseService.execute_query(query, [trainer_id])
    
    @staticmethod
    def get_trainer_students_count(trainer_id):
        """Количество учеников тренера"""
        try:
            query = "SELECT get_trainer_students_count_nesterovas_21_8(%s)"
            result = DatabaseService.execute_query(query, [trainer_id])
            return int(result[0][0]) if result and result[0] else 0
        except:
            return 0
    
    @staticmethod
    def update_trainer_schedule(schedule_id, data):
        """Обновить расписание тренера"""
        query = """
        UPDATE schedules_nesterovas_21_8
        SET 
            class_weekday_nesterovas_21_8 = %s,
            class_start_time_nesterovas_21_8 = %s,
            hall_number_nesterovas_21_8 = %s,
            subscription_price_nesterovas_21_8 = %s,
            schedule_status_nesterovas_21_8 = %s
        WHERE schedule_id = %s
        """
        params = [
            data.get('weekday'),
            data.get('start_time'),
            data.get('hall_number'),
            data.get('price'),
            data.get('status'),
            schedule_id
        ]
        return DatabaseService.execute_query(query, params)
    
    # Методы для администраторов
    @staticmethod
    def get_all_clients():
        return DatabaseService.execute_query("SELECT * FROM clients_nesterovas_21_8 ORDER BY client_id")
    
    @staticmethod
    def get_all_trainers():
        return DatabaseService.execute_query("SELECT * FROM trainers_nesterovas_21_8 ORDER BY trainer_id")
    
    @staticmethod
    def get_all_dance_styles():
        return DatabaseService.execute_query("SELECT * FROM dance_styles_nesterovas_21_8 ORDER BY dance_style_id")
    
    @staticmethod
    def get_all_halls():
        return DatabaseService.execute_query("SELECT * FROM halls_nesterovas_21_8 ORDER BY hall_number_nesterovas_21_8")
    
    @staticmethod
    def get_all_schedules():
        return DatabaseService.execute_query("""
            SELECT s.*, t.trainer_full_name_nesterovas_21_8, d.dance_style_name_nesterovas_21_8 
            FROM schedules_nesterovas_21_8 s
            JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
            JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
            ORDER BY s.schedule_id
        """)
    
    @staticmethod
    def get_all_registrations():
        return DatabaseService.execute_query("""
            SELECT r.*, c.client_full_name_nesterovas_21_8, s.schedule_id
            FROM registrations_nesterovas_21_8 r
            JOIN clients_nesterovas_21_8 c ON r.client_id = c.client_id
            JOIN schedules_nesterovas_21_8 s ON r.schedule_id = s.schedule_id
            ORDER BY r.registration_id
        """)