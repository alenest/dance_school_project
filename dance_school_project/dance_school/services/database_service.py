from django.db import connection
from dance_school_project.db_connection import get_db_connection
import psycopg2

class DatabaseService:
    @staticmethod
    def execute_query(query, params=None):
        """Выполняет SQL запрос и возвращает результат"""
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                conn.commit()
                return cursor.rowcount
    
    @staticmethod
    def call_procedure(proc_name, params=None):
        """Вызывает хранимую процедуру"""
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.callproc(proc_name, params or ())
                conn.commit()
    
    @staticmethod
    def get_user_role(username):
        """Определяет роль пользователя по логину"""
        # Логика определения роли пользователя
        pass