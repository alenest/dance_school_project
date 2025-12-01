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
            if query.strip().upper().startswith('SELECT'):
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
    
    @staticmethod
    def execute_table_function(func_name, params=None):
        """Выполняет табличную функцию"""
        conn = DatabaseService.get_connection()
        cur = conn.cursor()
        try:
            placeholders = ', '.join(['%s'] * len(params)) if params else ''
            call_query = f"SELECT * FROM {func_name}({placeholders})"
            print(f"Выполняем табличную функцию: {call_query}")
            cur.execute(call_query, params or ())
            result = cur.fetchall()
            
            # Получаем описание столбцов
            column_names = [desc[0] for desc in cur.description]
            print(f"Колонки: {column_names}")
            print(f"Найдено записей: {len(result)}")
            
            # Форматируем результат для удобства
            formatted_result = []
            for row in result:
                formatted_result.append(row)
            
            return formatted_result
        except Exception as e:
            print(f"Ошибка выполнения табличной функции {func_name}: {e}")
            print(traceback.format_exc())
            return []
        finally:
            cur.close()
            conn.close()
    
    @staticmethod
    def get_schedule_by_weekday(weekday):
        """Табличная функция: возвращает расписание по дню недели"""
        try:
            print(f"Запрашиваем расписание на день: {weekday}")
            result = DatabaseService.execute_table_function(
                'get_schedule_by_weekday_nesterovas_21_8',
                [weekday]
            )
            
            # Если результат пустой, проверим есть ли данные в таблице
            if not result:
                print(f"Табличная функция вернула пустой результат для {weekday}")
                print("Проверяем данные напрямую...")
                test_query = """
                SELECT 
                    s.schedule_id,
                    t.trainer_full_name_nesterovas_21_8,
                    d.dance_style_name_nesterovas_21_8,
                    s.class_weekday_nesterovas_21_8
                FROM schedules_nesterovas_21_8 s
                JOIN trainers_nesterovas_21_8 t ON s.trainer_id = t.trainer_id
                JOIN dance_styles_nesterovas_21_8 d ON s.dance_style_id = d.dance_style_id
                WHERE s.class_weekday_nesterovas_21_8 = %s
                LIMIT 5
                """
                test_result = DatabaseService.execute_query(test_query, [weekday])
                print(f"Прямой запрос вернул: {len(test_result)} записей")
            
            return result
        except Exception as e:
            print(f"Ошибка в get_schedule_by_weekday: {e}")
            print(traceback.format_exc())
            return []
    
    @staticmethod
    def get_active_clients_by_age(min_age, max_age):
        """Скалярная функция: количество клиентов по возрасту"""
        try:
            query = "SELECT get_active_clients_by_age_nesterovas_21_8(%s, %s)"
            result = DatabaseService.execute_query(query, [min_age, max_age])
            if result and result[0]:
                return int(result[0][0])
            return 0
        except Exception as e:
            print(f"Error in get_active_clients_by_age: {e}")
            return 0
    
    @staticmethod
    def calculate_discount(base_price, client_age, registration_count):
        """Функция расчета скидки"""
        try:
            query = "SELECT calculate_discount_simple_nesterovas_21_8(%s, %s, %s)"
            result = DatabaseService.execute_query(query, [base_price, client_age, registration_count])
            if result and result[0]:
                return float(result[0][0])
            return float(base_price)
        except Exception as e:
            print(f"Error in calculate_discount: {e}")
            return float(base_price)
    
    @staticmethod
    def check_age_validation(client_birth_date, dance_style_age_group):
        """Функция на языке SQL: проверка возраста"""
        try:
            query = "SELECT check_age_validation_nesterovas_21_8(%s, %s)"
            result = DatabaseService.execute_query(query, [client_birth_date, dance_style_age_group])
            if result and result[0]:
                return bool(result[0][0])
            return False
        except Exception as e:
            print(f"Error in check_age_validation: {e}")
            return False
    
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