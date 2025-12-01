from .database_service import DatabaseService

class AuthService:
    @staticmethod
    def authenticate(username, password):
        # Проверка администратора
        admin_query = """
        SELECT admin_username_nesterovas_21_8, admin_full_name_nesterovas_21_8 
        FROM administrators_nesterovas_21_8 
        WHERE admin_username_nesterovas_21_8 = %s AND admin_password_hash_nesterovas_21_8 = %s
        LIMIT 1
        """
        
        # Проверка тренера
        trainer_query = """
        SELECT trainer_id, trainer_full_name_nesterovas_21_8 
        FROM trainers_nesterovas_21_8 
        WHERE trainer_phone_nesterovas_21_8 = %s LIMIT 1
        """
        
        # Проверка клиента
        client_query = """
        SELECT client_id, client_full_name_nesterovas_21_8 
        FROM clients_nesterovas_21_8 
        WHERE contact_phone_nesterovas_21_8 = %s LIMIT 1
        """
        
        try:
            # Сначала пробуем как администратора
            admin = DatabaseService.execute_query(admin_query, [username, password])
            if admin:
                return {
                    'role': 'admin', 
                    'username': admin[0][0], 
                    'full_name': admin[0][1]
                }
            
            # Пробуем как тренера (по телефону)
            trainer = DatabaseService.execute_query(trainer_query, [username])
            if trainer:
                return {
                    'role': 'trainer', 
                    'trainer_id': trainer[0][0], 
                    'full_name': trainer[0][1],
                    'username': username
                }
            
            # Пробуем как клиента (по телефону)
            client = DatabaseService.execute_query(client_query, [username])
            if client:
                return {
                    'role': 'client', 
                    'client_id': client[0][0], 
                    'full_name': client[0][1],
                    'username': username
                }
                
        except Exception as e:
            print(f"Auth error: {e}")
        
        return None