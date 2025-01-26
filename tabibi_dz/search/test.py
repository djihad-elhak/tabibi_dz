import pytest
from django.db import connection
from .models import Filter

@pytest.fixture
def create_doctor():
    with connection.cursor() as cursor:
        # Create the doctor table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctor (
                doctor_id INT PRIMARY KEY,
                name VARCHAR(100),
                specialty_id VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(15),
                email VARCHAR(100),
                password VARCHAR(128)
            )
        """)
        # Insert a doctor into the table
        cursor.execute("""
            INSERT INTO doctor (doctor_id, name, specialty_id, last_name, phone, email, password)
            VALUES (1, 'John', 'Cardiology', 'Doe', '1234567890', 'john@example.com', 'password')
        """)

@pytest.mark.django_db
def test_get_all_doctors(create_doctor):
    doctors = Filter.get_all_doctors()
    assert len(doctors) > 0
    assert doctors[0]['name'] == 'John'
    assert doctors[0]['specialty_id'] == 'Cardiology'