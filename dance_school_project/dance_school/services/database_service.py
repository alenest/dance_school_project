import psycopg2
from django.conf import settings

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
    
    @staticmethod
    def update_record_directly(table_name, set_values, where_condition, params):
        """Прямое обновление записи в таблице"""
        set_clause = ', '.join([f"{col} = %s" for col in set_values.keys()])
        where_clause = ' AND '.join([f"{col} = %s" for col in where_condition.keys()])
        
        query = f"UPDATE {table_name}_nesterovas_21_8 SET {set_clause} WHERE {where_clause}"
        all_params = list(set_values.values()) + list(where_condition.values())
        
        return DatabaseService.execute_query(query, all_params)