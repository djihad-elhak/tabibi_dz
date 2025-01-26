import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.db import connection

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def setup_database():
    with connection.cursor() as cursor:
        # Create necessary tables
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patient (
                patient_id INT PRIMARY KEY,
                name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(15),
                email VARCHAR(100),
                password VARCHAR(128)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking (
                booking_id INT PRIMARY KEY AUTO_INCREMENT,
                patient_id INT,
                doctor_id INT,
                type VARCHAR(50),
                schedule VARCHAR(50),
                day DATE,
                link VARCHAR(255),
                FOREIGN KEY (patient_id) REFERENCES patient(patient_id),
                FOREIGN KEY (doctor_id) REFERENCES doctor(doctor_id)
            )
        """)
        # Insert a doctor into the table
        cursor.execute("""
            INSERT INTO doctor (doctor_id, name, specialty_id, last_name, phone, email, password)
            VALUES (1, 'John', 'Cardiology', 'Doe', '1234567890', 'john@example.com', 'password')
        """)
        # Insert a patient into the table
        cursor.execute("""
            INSERT INTO patient (patient_id, name, last_name, phone, email, password)
            VALUES (1, 'Jane', 'Doe', '0987654321', 'jane@example.com', 'password')
        """)
        # Insert a booking into the table
        cursor.execute("""
            INSERT INTO booking (patient_id, doctor_id, type, schedule, day, link)
            VALUES (1, 1, 'onsite', 'morning', '2025-01-01', 'http://example.com')
        """)

@pytest.mark.django_db
def test_get_patient_bookings(api_client, setup_database):
    url = reverse('patient_bookings')
    response = api_client.get(url, {'user_id': 1})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0]['type'] == 'onsite'
    assert response.json()[0]['schedule'] == 'morning'