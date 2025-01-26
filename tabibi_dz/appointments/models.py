
# Create your models here.
from django.db import connection
from dz_auth.models import DoctorManager, PatientManager
from django.core.mail import send_mail
from django.conf import settings
def list_to_string(list):
    available_sessions_str = ['0'] * 7
    for session in list:
        if 0 <= session < 14:
            available_sessions_str[session] = '1'
    available_sessions_str = ''.join(available_sessions_str)
    return available_sessions_str

def string_to_list(string):
    return [i for i, session in enumerate(string) if session == '1']

    return ''.join(map(str, list))

SCHEDULE_MAPPING = {
    0: "08:00 AM",
    1: "09:00 AM",
    2: "10:00 AM",
    3: "11:00 AM",
    4: "01:00 PM",
    5: "02:00 PM",
    6: "03:00 PM",
}

class ScheduleManager:
    @staticmethod
    def declare_free_sessions(doctor_id, date, available_sessions):
        # Convert available_sessions list to a string of 14 characters
        available_sessions_str = list_to_string(available_sessions)

        with connection.cursor() as cursor:
            cursor.execute("""
                    INSERT INTO schedules (doctor_id, day, available_sessions)
                    VALUES (%s, %s, %s)
                """, [doctor_id, date, available_sessions_str])


    def change_sesions(doctor_id, date, available_sessions):
        available_sessions_str=list_to_string(available_sessions)
        # Ensure available_sessions is a valid list of 14 integers

        with connection.cursor() as cursor:
            cursor.execute("""
                    UPDATE schedules
                    SET available_sessions = %s
                    WHERE doctor_id = %s AND day = %s
                """, [available_sessions_str, doctor_id, date])

    @staticmethod
    def fetch_available_sessions(doctor_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT day, available_sessions FROM schedules
            WHERE doctor_id = %s
            """, [doctor_id])
            rows = cursor.fetchall()

        # Process the results to return a structured format
    
        return [{"date": row[0], "available_sessions": string_to_list(row[1])} for row in rows]
                   
            
   
    @staticmethod
    def fetch_available_sessions_bydate(doctor_id, date):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT available_sessions FROM schedules
                WHERE doctor_id = %s AND day = %s
            """, [doctor_id, date])
            row = cursor.fetchone()
            if row:
                return string_to_list(row[0])
            return None


from tabibi_dz.settings import WHEREBY_API_KEY
import requests
from datetime import datetime, timedelta


class BookingManager:

    @staticmethod
    def create_room_for_doctor(doctor_name, schedule_slot,date):
        # Get the time from the schedule mapping
        if schedule_slot not in SCHEDULE_MAPPING:
            return None, {"error": "Invalid schedule slot"}
        time_slot = SCHEDULE_MAPPING[schedule_slot]
        try:
        # Convert the time to 24-hour format and create datetime object
            date_time_str = f"{date} {time_slot}"
            time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %I:%M %p")
        except ValueError:
            return None, {"error": "Invalid date or time format"}
    
    # Calculate start and end times
        startDate = time_obj.isoformat()  # Start time (ISO 8601 format)
        endDate = (time_obj + timedelta(hours=1)).isoformat()  # End time, one hour 


        # Generate a unique room name
        room_name = f"{doctor_name.replace(' ', '-').lower()}-{time_slot.replace(':', '').replace(' ', '').lower()}"
        url = "https://api.whereby.dev/v1/meetings"
        headers = {
            "Authorization": f"Bearer {WHEREBY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "endDate":endDate ,
            "startDate": startDate,
            "isLocked": "true",
            "roomMode": "group",
            
            
                "endDate": "2026-12-31T23:59:59Z"  # Set a long validity for the room
            }
        

        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        print("nigga",response)
        if response.status_code == 201:
            data = response.json()
            return data.get("roomUrl"), None
        else:
            return None, {"error": "Failed to create room"}
    @staticmethod
    def book_appointment(patient_id, doctor_id, appointment_type, schedule, date, link=None):
        with connection.cursor() as cursor:
            # Check if the session is available
            cursor.execute("""
                SELECT available_sessions FROM schedules
                WHERE doctor_id = %s AND day = %s
            """, [doctor_id, date])
            row = cursor.fetchone()
            if not row:
                return {"error": "No schedule found for the given date"}

            available_sessions = row[0]
            if available_sessions[schedule] != '1':
                return {"error": "Session not available"}

            # Book the appointment
            cursor.execute("""
                INSERT INTO booking (patient_id, doctor_id, type, schedule, day, link)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [patient_id, doctor_id, appointment_type, schedule, date, link])

            # Update the available sessions
            updated_sessions = list(available_sessions)
            updated_sessions[schedule] = '0'
            updated_sessions_str = ''.join(updated_sessions)
            cursor.execute("""
                UPDATE schedules
                SET available_sessions = %s
                WHERE doctor_id = %s AND day = %s
            """, [updated_sessions_str, doctor_id, date])

            return {"message": "Appointment booked successfully"}
        




    @staticmethod
    def book_appointments(patient_id, doctor_id, appointment_type, schedule, date):
        with connection.cursor() as cursor:
            # Fetch doctor name
            cursor.execute("SELECT name FROM doctor WHERE doctor_id = %s", [doctor_id])
            row = cursor.fetchone()
            if not row:
                return {"error": "Doctor not found"}

            doctor_name = row[0]

            # Create a room for the selected time slot
            

            # Check if the session is available
            cursor.execute("""
                SELECT available_sessions FROM schedules
                WHERE doctor_id = %s AND day = %s
            """, [doctor_id, date])
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                DELETE  FROM schedules
                WHERE doctor_id = %s AND day = %s
            """, [doctor_id, date])
                return {"error": "No schedule found for the given date"}


            available_sessions = list(row[0])
            if available_sessions[schedule] != '1':
                return {"error": "Session not available"}
            
            
            # Book the appointment
            

            # Update the available sessions
            available_sessions[schedule] = '0'
            cursor.execute("""
                UPDATE schedules
                SET available_sessions = %s
                WHERE doctor_id = %s AND day = %s
            """, [''.join(available_sessions), doctor_id, date])
            docotr_mail=DoctorManager.fetch_doctor_by_id(doctor_id).get('email')
            patient_mail=PatientManager.fetch_patient_by_id(patient_id).get('email')
            receptients=[docotr_mail,patient_mail]


            if appointment_type =="onsite":
                cursor.execute("""
                INSERT INTO booking (patient_id, doctor_id, type, schedule, day)
                VALUES (%s, %s, %s, %s, %s)
            """, [patient_id, doctor_id, appointment_type, schedule, date])
                send_mail(
                    'Appointment booking',
                    f'Your appointment has been booked successfully at {SCHEDULE_MAPPING[schedule]} {date}', 
                    settings.DEFAULT_FROM_EMAIL,
                    receptients)

                return {
                "message": "Appointment booked successfully"}
                
                
            else :
                room_url, error = BookingManager.create_room_for_doctor(doctor_name, schedule,date)
                if error:
                    return error
                cursor.execute("""
                INSERT INTO booking (patient_id, doctor_id, type, schedule, day, link)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [patient_id, doctor_id, appointment_type, schedule, date, room_url])
                send_mail(
                    'Appointment booking',
                    f'Your appointment has been booked successfully at {SCHEDULE_MAPPING[schedule]} {date}\nheres the link :{room_url}', 
                    settings.DEFAULT_FROM_EMAIL,
                    receptients)


                return {
                "message": "Appointment booked successfully",
                "roomUrl": room_url,
                "timeSlot": SCHEDULE_MAPPING[schedule]
            }
class Booking:
    @staticmethod
    def get_patient_bookings(id) :
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM booking  
            WHERE patient_id = %s AND day >= %s
            """, [id, timezone.now().date()])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        

    @staticmethod    
    def get_doctor_bookings(id):
         with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * from booking  
                WHERE doctor_id = %s AND day >= %s
            """, [id, timezone.now().date()])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
         
from django.utils import timezone

class History_booking :
    @staticmethod
    def get_patient_history(id):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM booking  
            WHERE patient_id = %s AND day < %s
            """, [id, timezone.now().date()])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        

    @staticmethod    
    def get_doctor_history(id):
         with connection.cursor() as cursor:
            cursor.execute("""
                SELECT * from booking  
                WHERE doctor_id = %s AND day < %s
            """, [id, timezone.now().date()])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        
            
        

    
class RatingManager :
    @staticmethod
    def get_ratings(doctor_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM rating
            WHERE doctor_id = %s
            """, [doctor_id])
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
    @staticmethod
    def get_final_rating(doctor_id):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT AVG(rating) FROM rating
            WHERE doctor_id = %s
            """, [doctor_id])
            row = cursor.fetchone()
            return row[0]
    
    @staticmethod
    def add_rating(doctor_id, patient_id, rating, comment):
        with connection.cursor() as cursor:
            # Check if the patient_id and doctor_id are in the booking table and the date is less than now
            cursor.execute("""
                SELECT COUNT(*) FROM booking
                WHERE doctor_id = %s AND patient_id = %s AND day < %s
            """, [doctor_id, patient_id, timezone.now().date()])
            count = cursor.fetchone()[0]

            if count == 0:
                raise ValueError("The patient and doctor must have a past booking")

            # Insert the rating
            cursor.execute("""
                INSERT INTO rating (doctor_id, patient_id, rating, comment)
                VALUES (%s, %s, %s, %s)
            """, [doctor_id, patient_id, rating, comment])
    