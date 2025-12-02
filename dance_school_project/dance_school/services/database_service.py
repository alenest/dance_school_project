import psycopg2
from django.conf import settings
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
    def execute_query(query, params=None, fetch=True):
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            cur.execute(query, params or ())
            if fetch and (query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('WITH')):
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
            traceback.print_exc()
            raise e
        finally:
            cur.close()
            conn.close()
    
    # ========== МЕТОДЫ ДЛЯ ГЛАВНОЙ СТРАНИЦЫ ==========
    
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
            COALESCE(h.hall_capacity_nesterovas_21_8, 0) - COALESCE(reg.registration_count, 0) as available_spots
        FROM schedules_nesterovas_21_8 s
        JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
        JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
        JOIN training_slots_nesterovas_21_8 ts ON s.class_start_time_nesterovas_21_8 = ts.class_start_time_nesterovas_21_8
        LEFT JOIN halls_nesterovas_21_8 h ON s.hall_number_nesterovas_21_8 = h.hall_number_nesterovas_21_8
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
        """Табличная функция: возвращает расписание по дню недели"""
        try:
            base_query = """
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
                COALESCE(h.hall_capacity_nesterovas_21_8, 0) - COALESCE(reg.registration_count, 0) as available_spots
            FROM schedules_nesterovas_21_8 s
            JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
            JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
            JOIN training_slots_nesterovas_21_8 ts ON s.class_start_time_nesterovas_21_8 = ts.class_start_time_nesterovas_21_8
            LEFT JOIN halls_nesterovas_21_8 h ON s.hall_number_nesterovas_21_8 = h.hall_number_nesterovas_21_8
            LEFT JOIN (
                SELECT r.schedule_id, COUNT(*) as registration_count
                FROM registrations_nesterovas_21_8 r
                GROUP BY r.schedule_id
            ) reg ON s.schedule_id = reg.schedule_id
            WHERE s.schedule_status_nesterovas_21_8 = 'активно'
            """
            
            if weekday and weekday != 'all':
                query = base_query + " AND s.class_weekday_nesterovas_21_8 = %s"
                result = DatabaseService.execute_query(query, [weekday])
            else:
                result = DatabaseService.execute_query(base_query)
            
            return result
                
        except Exception as e:
            print(f"Ошибка в get_schedule_by_weekday: {e}")
            traceback.print_exc()
            return []
    
    @staticmethod
    def authenticate_user(login_data, password, role):
        """Универсальная авторизация"""
        try:
            if role == 'admin':
                # Для админов используем логин как username
                admin_query = """
                SELECT admin_username_nesterovas_21_8, admin_full_name_nesterovas_21_8 
                FROM administrators_nesterovas_21_8 
                WHERE admin_username_nesterovas_21_8 = %s AND admin_password_hash_nesterovas_21_8 = %s
                """
                admin = DatabaseService.execute_query(admin_query, [login_data, password])
                if admin:
                    return {
                        'role': 'admin',
                        'username': admin[0][0],
                        'full_name': admin[0][1]
                    }
            
            elif role == 'trainer':
                # Для тренеров используем email или телефон
                trainer_query = """
                SELECT trainer_id, trainer_full_name_nesterovas_21_8, trainer_email_nesterovas_21_8, trainer_phone_nesterovas_21_8
                FROM trainers_nesterovas_21_8 
                WHERE (trainer_email_nesterovas_21_8 = %s OR trainer_phone_nesterovas_21_8 = %s)
                """
                trainer = DatabaseService.execute_query(trainer_query, [login_data, login_data])
                if trainer:
                    return {
                        'role': 'trainer',
                        'trainer_id': trainer[0][0],
                        'full_name': trainer[0][1],
                        'email': trainer[0][2],
                        'phone': trainer[0][3]
                    }
            
            elif role == 'client':
                # Для клиентов используем email или телефон
                client_query = """
                SELECT client_id, client_full_name_nesterovas_21_8, contact_email_nesterovas_21_8, contact_phone_nesterovas_21_8
                FROM clients_nesterovas_21_8 
                WHERE (contact_email_nesterovas_21_8 = %s OR contact_phone_nesterovas_21_8 = %s)
                AND client_status_nesterovas_21_8 = 'активен'
                """
                client = DatabaseService.execute_query(client_query, [login_data, login_data])
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
            traceback.print_exc()
        
        return None
    
    @staticmethod
    def calculate_discount(base_price, client_age, registration_count):
        """Функция расчета скидки"""
        try:
            discount = 0
            if client_age < 25:
                discount += 5
            elif client_age > 50:
                discount += 10
            
            if registration_count > 5:
                discount += 15
            elif registration_count > 3:
                discount += 10
            
            final_price = base_price * (1 - discount / 100)
            return round(final_price, 2)
        except Exception as e:
            print(f"Error in calculate_discount: {e}")
            return float(base_price)
    
    # ========== МЕТОДЫ ДЛЯ ТРЕНЕРСКОЙ ПАНЕЛИ ==========
    
    @staticmethod
    def get_trainer_schedules(trainer_id):
        """Получить расписания тренера"""
        query = """
        SELECT 
            s.schedule_id,
            s.class_weekday_nesterovas_21_8,
            TO_CHAR(s.class_start_time_nesterovas_21_8, 'HH24:MI') as start_time,
            TO_CHAR(ts.class_end_time_nesterovas_21_8, 'HH24:MI') as end_time,
            s.hall_number_nesterovas_21_8,
            d.dance_style_name_nesterovas_21_8,
            s.subscription_price_nesterovas_21_8,
            s.schedule_status_nesterovas_21_8,
            COALESCE(reg.registration_count, 0) as students_count,
            TO_CHAR(s.period_start_date_nesterovas_21_8, 'YYYY-MM-DD') as period_start,
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
            TO_CHAR(c.client_birth_date_nesterovas_21_8, 'YYYY-MM-DD') as birth_date,
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
            query = """
            SELECT COUNT(DISTINCT r.client_id)
            FROM registrations_nesterovas_21_8 r
            JOIN schedules_nesterovas_21_8 s ON r.schedule_id = s.schedule_id
            WHERE s.trainer_id = %s
            """
            result = DatabaseService.execute_query(query, [trainer_id])
            return int(result[0][0]) if result and result[0] else 0
        except:
            return 0
    
    # ========== МЕТОДЫ ДЛЯ АДМИН-ПАНЕЛИ ==========
    
    @staticmethod
    def get_all_clients():
        """Получить всех клиентов"""
        return DatabaseService.execute_query("""
            SELECT client_id, contact_phone_nesterovas_21_8, client_full_name_nesterovas_21_8, 
                   client_birth_date_nesterovas_21_8, contact_email_nesterovas_21_8, 
                   parent_guardian_name_nesterovas_21_8, client_status_nesterovas_21_8
            FROM clients_nesterovas_21_8 
            ORDER BY client_id
        """)
    
    @staticmethod
    def get_all_trainers():
        """Получить всех тренеров"""
        return DatabaseService.execute_query("""
            SELECT trainer_id, trainer_phone_nesterovas_21_8, trainer_full_name_nesterovas_21_8, trainer_email_nesterovas_21_8
            FROM trainers_nesterovas_21_8 
            ORDER BY trainer_id
        """)
    
    @staticmethod
    def get_all_dance_styles():
        """Получить все направления танцев"""
        return DatabaseService.execute_query("""
            SELECT dance_style_id, dance_style_name_nesterovas_21_8, difficulty_level_nesterovas_21_8, 
                   target_age_group_nesterovas_21_8, style_status_nesterovas_21_8
            FROM dance_styles_nesterovas_21_8 
            ORDER BY dance_style_id
        """)
    
    @staticmethod
    def get_all_halls():
        """Получить все залы"""
        return DatabaseService.execute_query("""
            SELECT hall_number_nesterovas_21_8, hall_capacity_nesterovas_21_8
            FROM halls_nesterovas_21_8 
            ORDER BY hall_number_nesterovas_21_8
        """)
    
    @staticmethod
    def get_all_schedules():
        """Получить все расписания"""
        return DatabaseService.execute_query("""
            SELECT s.schedule_id, s.trainer_id, s.class_weekday_nesterovas_21_8, 
                   s.period_start_date_nesterovas_21_8, s.class_start_time_nesterovas_21_8, 
                   s.hall_number_nesterovas_21_8, s.dance_style_id, s.subscription_price_nesterovas_21_8, 
                   s.schedule_status_nesterovas_21_8,
                   t.trainer_full_name_nesterovas_21_8, 
                   d.dance_style_name_nesterovas_21_8
            FROM schedules_nesterovas_21_8 s
            JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
            JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
            ORDER BY s.schedule_id
        """)
    
    @staticmethod
    def get_all_registrations():
        """Получить все регистрации"""
        return DatabaseService.execute_query("""
            SELECT r.registration_id, r.client_id, r.schedule_id, 
                   r.registration_datetime_nesterovas_21_8, 
                   r.admin_username_nesterovas_21_8,
                   c.client_full_name_nesterovas_21_8
            FROM registrations_nesterovas_21_8 r
            JOIN clients_nesterovas_21_8 c ON r.client_id = c.client_id
            ORDER BY r.registration_id
        """)
    
    @staticmethod
    def get_all_administrators():
        """Получить всех администраторов"""
        return DatabaseService.execute_query("""
            SELECT admin_username_nesterovas_21_8, admin_full_name_nesterovas_21_8, 
                   admin_position_nesterovas_21_8, admin_phone_nesterovas_21_8, 
                   admin_password_hash_nesterovas_21_8
            FROM administrators_nesterovas_21_8 
            ORDER BY admin_username_nesterovas_21_8
        """)
    
    @staticmethod
    def get_all_training_periods():
        """Получить все периоды занятий"""
        return DatabaseService.execute_query("""
            SELECT period_start_date_nesterovas_21_8, period_end_date_nesterovas_21_8
            FROM training_periods_nesterovas_21_8 
            ORDER BY period_start_date_nesterovas_21_8
        """)
    
    @staticmethod
    def get_all_training_slots():
        """Получить все временные слоты"""
        return DatabaseService.execute_query("""
            SELECT class_start_time_nesterovas_21_8, class_end_time_nesterovas_21_8
            FROM training_slots_nesterovas_21_8 
            ORDER BY class_start_time_nesterovas_21_8
        """)
    
    @staticmethod
    def get_table_structure(table_name):
        """Получить структуру таблицы"""
        query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = %s
        ORDER BY ordinal_position
        """
        return DatabaseService.execute_query(query, [table_name])
    
    @staticmethod
    def get_record_by_id(table_name, record_id):
        """Получить запись по ID"""
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
            raise ValueError(f"Неизвестная таблица: {table_name}")
        
        query = f"SELECT * FROM {table_name} WHERE {pk_column} = %s"
        return DatabaseService.execute_query(query, [record_id])
    
    @staticmethod
    def delete_record(table_name, record_id):
        """Удалить запись из таблицы"""
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
            raise ValueError(f"Неизвестная таблица: {table_name}")
        
        query = f"DELETE FROM {table_name} WHERE {pk_column} = %s"
        print(f"Выполняется запрос DELETE: {query}")
        print(f"Параметры: [{record_id}]")
        DatabaseService.execute_query(query, [record_id], fetch=False)