from django.db import connection

# Create your models here.
class Filter:
    @staticmethod
    def filter_by_availability(date):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM doctor
            join schedule on doctor.doctor_id = schedule.doctor_id
            WHERE date = %s
            """, [date])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None


    @staticmethod
    def filter_by_specialty(specialty):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM doctor
            join specialty on doctor.specialty = specialty.specialty_id
            WHERE specialty = %s
            """, [specialty])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
    @staticmethod
    def filter_by_coverage(coverage):
        with connection.cursor() as cursor:
            cursor.execute("""
            SELECT * FROM doctor
            join insurace on doctor.doctor_id = insurance.doctor_id
            WHERE coverage = %s
            """, [coverage])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                return dict(zip(columns, row))
            return None
    @staticmethod
    
    def search_doctors(date, latitude, longitude, specialty=None, coverage=None, radius=10):
    # Haversine formula to calculate distance
        haversine_formula = """
            (6371 * acos(
                cos(radians(%s)) * cos(radians(dl.latitude)) *
                cos(radians(%s) - radians(dl.longitude)) +
                sin(radians(%s)) * sin(radians(dl.latitude))
            )) AS distance
        """

        # Build the query
        query = f"""
            SELECT doctor.*, {haversine_formula}
            FROM doctor
            JOIN doctor_location dl ON doctor.doctor_id = dl.id
            LEFT JOIN schedules s ON s.doctor_id = doctor.doctor_id
            LEFT JOIN insurance ON doctor.doctor_id = insurance.doctor_id
            WHERE s.day = %s
        """
        params = [latitude, longitude, latitude, date]

        if specialty:
            query += " AND doctor.specialty_id = %s"
            params.append(specialty)
        if coverage:
            query += " AND insurance.coverage = %s"
            params.append(coverage)

        query += " HAVING distance <= %s"
        params.append(radius)

        # Execute the query
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            doctors = [dict(zip(columns, row)) for row in rows]

        return doctors
    



from django.db import connection

class Filter:
    @staticmethod
    def get_all_doctors():
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM doctor")
            rows = cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in rows]