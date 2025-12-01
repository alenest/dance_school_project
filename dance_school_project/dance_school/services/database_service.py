import psycopg2
from django.conf import settings
from decimal import Decimal

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
            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
            else:
                conn.commit()
                result = None
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def call_procedure(proc_name, params=None):
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            placeholders = ', '.join(['%s'] * len(params)) if params else ''
            call_query = f"CALL {proc_name}({placeholders})"
            cur.execute(call_query, params or ())
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def call_function(func_name, params=None, return_type=None):
        """Вызывает скалярную функцию и возвращает результат"""
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            placeholders = ', '.join(['%s'] * len(params)) if params else ''
            call_query = f"SELECT {func_name}({placeholders})"
            cur.execute(call_query, params or ())
            result = cur.fetchone()
            
            if result and return_type:
                if return_type == 'int':
                    return int(result[0]) if result[0] else 0
                elif return_type == 'float':
                    return float(result[0]) if result[0] else 0.0
                elif return_type == 'decimal':
                    return Decimal(str(result[0])) if result[0] else Decimal('0')
            
            return result[0] if result else None
        except Exception as e:
            raise e
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def execute_table_function(func_name, params=None):
        """Выполняет табличную функцию"""
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            placeholders = ', '.join(['%s'] * len(params)) if params else ''
            call_query = f"SELECT * FROM {func_name}({placeholders})"
            cur.execute(call_query, params or ())
            result = cur.fetchall()
            return result
        except Exception as e:
            print(f"Error executing table function {func_name}: {e}")
            return []
        finally:
            cur.close()
            conn.close()
    
    # Новые методы для работы с функциями и представлениями
    
    @staticmethod
    def get_schedule_by_weekday(weekday):
        """Табличная функция: возвращает расписание по дню недели"""
        try:
            return DatabaseService.execute_table_function(
                'get_schedule_by_weekday_nesterovas_21_8',
                [weekday]
            )
        except Exception as e:
            print(f"Error in get_schedule_by_weekday: {e}")
            return []
    
    @staticmethod
    def get_active_clients_by_age(min_age, max_age):
        """Скалярная функция: количество клиентов по возрасту"""
        try:
            result = DatabaseService.call_function(
                'get_active_clients_by_age_nesterovas_21_8',
                [min_age, max_age],
                'int'
            )
            return result if result is not None else 0
        except Exception as e:
            print(f"Error in get_active_clients_by_age: {e}")
            return 0
    
    @staticmethod
    def calculate_discount(base_price, client_age, registration_count):
        """Функция расчета скидки"""
        try:
            # Преобразуем base_price к строке для корректной передачи в NUMERIC
            base_price_str = str(float(base_price))
            result = DatabaseService.call_function(
                'calculate_discount_simple_nesterovas_21_8',
                [base_price_str, client_age, registration_count],
                'decimal'
            )
            return result if result is not None else Decimal(str(base_price))
        except Exception as e:
            print(f"Error in calculate_discount: {e}")
            return Decimal(str(base_price))
    
    @staticmethod
    def format_phone_number(phone):
        """Функция форматирования телефона (на другом языке)"""
        try:
            return DatabaseService.call_function(
                'format_phone_number_nesterovas_21_8',
                [phone]
            )
        except Exception as e:
            print(f"Error in format_phone_number: {e}")
            return phone
    
    @staticmethod
    def get_admin_view():
        """Представление для администратора"""
        try:
            return DatabaseService.execute_query("SELECT * FROM admin_full_view_nesterovas_21_8 ORDER BY entity_type, id")
        except Exception as e:
            print(f"Error in get_admin_view: {e}")
            return []
    
    @staticmethod
    def get_trainer_view(trainer_id):
        """Представление для тренера"""
        try:
            return DatabaseService.execute_query(
                "SELECT * FROM trainer_view_nesterovas_21_8 WHERE trainer_id = %s ORDER BY class_start_time_nesterovas_21_8",
                [trainer_id]
            )
        except Exception as e:
            print(f"Error in get_trainer_view: {e}")
            return []
    
    @staticmethod
    def get_client_view(client_id):
        """Представление для клиента"""
        try:
            return DatabaseService.execute_query(
                "SELECT * FROM client_view_nesterovas_21_8 WHERE client_id = %s ORDER BY registration_datetime",
                [client_id]
            )
        except Exception as e:
            print(f"Error in get_client_view: {e}")
            return []
    
    @staticmethod
    def get_schedule_data():
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