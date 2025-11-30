import psycopg2
from django.conf import settings
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
    
    # Training Periods
    @staticmethod
    def insert_training_period(start_date, end_date):
        DatabaseService.call_procedure('insert_training_period_nesterovas_21_8', [start_date, end_date])
    
    @staticmethod
    def update_training_period(start_date, end_date):
        DatabaseService.call_procedure('update_training_period_nesterovas_21_8', [start_date, end_date])
    
    @staticmethod
    def delete_training_period(start_date):
        DatabaseService.call_procedure('delete_training_period_nesterovas_21_8', [start_date])
    
    # Training Slots
    @staticmethod
    def insert_training_slot(start_time, end_time):
        DatabaseService.call_procedure('insert_training_slot_nesterovas_21_8', [start_time, end_time])
    
    @staticmethod
    def update_training_slot(start_time, end_time):
        DatabaseService.call_procedure('update_training_slot_nesterovas_21_8', [start_time, end_time])
    
    @staticmethod
    def delete_training_slot(start_time):
        DatabaseService.call_procedure('delete_training_slot_nesterovas_21_8', [start_time])
    
    # Administrators
    @staticmethod
    def insert_administrator(username, full_name, position, phone, password_hash):
        DatabaseService.call_procedure(
            'insert_administrator_nesterovas_21_8',
            [username, full_name, position, phone, password_hash]
        )
    
    @staticmethod
    def update_administrator(username, full_name=None, position=None, phone=None, password_hash=None):
        DatabaseService.call_procedure(
            'update_administrator_nesterovas_21_8',
            [username, full_name, position, phone, password_hash]
        )
    
    @staticmethod
    def delete_administrator(username):
        DatabaseService.call_procedure('delete_administrator_nesterovas_21_8', [username])
    
    # Schedules
    @staticmethod
    def insert_schedule(trainer_id, weekday, period_start_date, class_start_time, hall_number, dance_style_id, price, status='активно'):
        DatabaseService.call_procedure(
            'insert_schedule_nesterovas_21_8',
            [trainer_id, weekday, period_start_date, class_start_time, hall_number, dance_style_id, price, status]
        )
    
    @staticmethod
    def update_schedule(schedule_id, trainer_id=None, weekday=None, period_start_date=None, class_start_time=None, hall_number=None, dance_style_id=None, price=None, status=None):
        DatabaseService.call_procedure(
            'update_schedule_nesterovas_21_8',
            [schedule_id, trainer_id, weekday, period_start_date, class_start_time, hall_number, dance_style_id, price, status]
        )
    
    @staticmethod
    def delete_schedule(schedule_id):
        DatabaseService.call_procedure('delete_schedule_nesterovas_21_8', [schedule_id])
    
    # Registrations
    @staticmethod
    def insert_registration(client_id, schedule_id, registration_datetime, admin_username):
        DatabaseService.call_procedure(
            'insert_registration_nesterovas_21_8',
            [client_id, schedule_id, registration_datetime, admin_username]
        )
    
    @staticmethod
    def update_registration(registration_id, client_id=None, schedule_id=None, registration_datetime=None, admin_username=None):
        DatabaseService.call_procedure(
            'update_registration_nesterovas_21_8',
            [registration_id, client_id, schedule_id, registration_datetime, admin_username]
        )
    
    @staticmethod
    def delete_registration(registration_id):
        DatabaseService.call_procedure('delete_registration_nesterovas_21_8', [registration_id])
    
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