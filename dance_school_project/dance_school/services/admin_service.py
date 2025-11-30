from .database_service import DatabaseService

class AdminService:
    
    # Clients
    @staticmethod
    def insert_client(phone, full_name, birth_date, email=None, parent_name=None, status='активен'):
        DatabaseService.call_procedure(
            'insert_client_nesterovas_21_8',
            [phone, full_name, birth_date, email, parent_name, status]
        )
    
    @staticmethod
    def update_client(client_id, phone=None, full_name=None, birth_date=None, email=None, parent_name=None, status=None):
        DatabaseService.call_procedure(
            'update_client_nesterovas_21_8',
            [client_id, phone, full_name, birth_date, email, parent_name, status]
        )
    
    @staticmethod
    def delete_client(client_id):
        DatabaseService.call_procedure('delete_client_nesterovas_21_8', [client_id])
    
    # Dance Styles
    @staticmethod
    def insert_dance_style(style_name, difficulty_level, target_age_group, status='активно'):
        DatabaseService.call_procedure(
            'insert_dance_style_nesterovas_21_8',
            [style_name, difficulty_level, target_age_group, status]
        )
    
    @staticmethod
    def update_dance_style(style_id, style_name=None, difficulty_level=None, target_age_group=None, status=None):
        DatabaseService.call_procedure(
            'update_dance_style_nesterovas_21_8',
            [style_id, style_name, difficulty_level, target_age_group, status]
        )
    
    @staticmethod
    def delete_dance_style(style_id):
        DatabaseService.call_procedure('delete_dance_style_nesterovas_21_8', [style_id])
    
    # Trainers
    @staticmethod
    def insert_trainer(phone, full_name, email=None):
        DatabaseService.call_procedure(
            'insert_trainer_nesterovas_21_8',
            [phone, full_name, email]
        )
    
    @staticmethod
    def update_trainer(trainer_id, phone=None, full_name=None, email=None):
        DatabaseService.call_procedure(
            'update_trainer_nesterovas_21_8',
            [trainer_id, phone, full_name, email]
        )
    
    @staticmethod
    def delete_trainer(trainer_id):
        DatabaseService.call_procedure('delete_trainer_nesterovas_21_8', [trainer_id])
    
    # Halls
    @staticmethod
    def insert_hall(hall_number, capacity):
        DatabaseService.call_procedure('insert_hall_nesterovas_21_8', [hall_number, capacity])
    
    @staticmethod
    def update_hall(hall_number, capacity):
        DatabaseService.call_procedure('update_hall_nesterovas_21_8', [hall_number, capacity])
    
    @staticmethod
    def delete_hall(hall_number):
        DatabaseService.call_procedure('delete_hall_nesterovas_21_8', [hall_number])
    
    # Получение данных для отображения
    @staticmethod
    def get_all_clients():
        return DatabaseService.execute_query("SELECT * FROM clients_nesterovas_21_8 ORDER BY client_id")
    
    @staticmethod
    def get_all_dance_styles():
        return DatabaseService.execute_query("SELECT * FROM dance_styles_nesterovas_21_8 ORDER BY dance_style_id")
    
    @staticmethod
    def get_all_trainers():
        return DatabaseService.execute_query("SELECT * FROM trainers_nesterovas_21_8 ORDER BY trainer_id")
    
    @staticmethod
    def get_all_halls():
        return DatabaseService.execute_query("SELECT * FROM halls_nesterovas_21_8 ORDER BY hall_number_nesterovas_21_8")
    
    @staticmethod
    def get_all_training_periods():
        return DatabaseService.execute_query("SELECT * FROM training_periods_nesterovas_21_8 ORDER BY period_start_date_nesterovas_21_8")
    
    @staticmethod
    def get_all_training_slots():
        return DatabaseService.execute_query("SELECT * FROM training_slots_nesterovas_21_8 ORDER BY class_start_time_nesterovas_21_8")
    
    @staticmethod
    def get_all_administrators():
        return DatabaseService.execute_query("SELECT * FROM administrators_nesterovas_21_8 ORDER BY admin_username_nesterovas_21_8")
    
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