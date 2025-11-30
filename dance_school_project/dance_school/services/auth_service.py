# dance_school/services/auth_service.py
from .database_service import DatabaseService


class AuthService:
    @staticmethod
    def authenticate(username, password):
        """
        Базовая аутентификация через БД
        В реальном проекте нужно использовать хэширование паролей!
        """
        # Проверяем в администраторах
        admin_query = """
        SELECT admin_username_nesterovas_21_8, admin_full_name_nesterovas_21_8 
        FROM administrators_nesterovas_21_8 
        WHERE admin_username_nesterovas_21_8 = %s AND admin_password_hash_nesterovas_21_8 = %s
        """
        admin = DatabaseService.execute_query(admin_query, [username, password])
        if admin:
            return {'role': 'admin', 'username': admin[0][0], 'full_name': admin[0][1]}
        
        # TODO: Добавить проверку для тренеров и клиентов
        return None
    
    @staticmethod
    def get_user_role(username):
        """Определяет роль пользователя"""
        # Пока просто проверяем в администраторах
        query = "SELECT 1 FROM administrators_nesterovas_21_8 WHERE admin_username_nesterovas_21_8 = %s"
        result = DatabaseService.execute_query(query, [username])
        return 'admin' if result else 'unknown'