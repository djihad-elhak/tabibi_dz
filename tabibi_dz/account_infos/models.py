from django.db import connection
from django.contrib.auth.hashers import make_password

class baseUserManager: 
    @staticmethod
    def change_password(user_type,user_id, new_password):
        hashed_password = make_password(new_password)

        with connection.cursor() as cursor:
            if user_type == "doctor" :
                id="doctor_id"
            else :
                id="card_id"
            
            cursor.execute(f"""
                UPDATE {user_type}
                SET password = %s
                WHERE {id} = %s
            """, [hashed_password, user_id])
        return None
    @staticmethod
    def change_phone(user_id, new_phone):
        with connection.cursor() as cursor:
            cursor.execute("""
            UPDATE user
            SET phone = %s
            WHERE user_id = %s
            """, [new_phone, user_id])
        return None
    