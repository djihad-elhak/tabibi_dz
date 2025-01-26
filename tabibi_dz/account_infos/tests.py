# change_password/tests.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.hashers import check_password
from dz_auth.models import PatientManager

@pytest.mark.django_db
def test_change_password_patient():
    client = APIClient()
    # Create a test patient
    PatientManager.create_patient(
        card_id="123456789",
        name="Test",
        last_name="Patient",
        email="patient@example.com",
        phone="1234567890",
        password="oldpassword",
        birth_date="1990-01-01",
        street="123 Street",
        latitude=36.7,
        longitude=3.1
    )

    # Log in the patient (simulate JWT token)
    payload = {
        'id': "123456789",
        'password': 'oldpassword',
        'email': 'patient@example.com'
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    client.cookies['jwt'] = token

    # Test password change
    data = {
        'password': 'oldpassword',
        'new_password': 'newpassword'
    }
    url = reverse('change-password-patient')  # Replace with your actual URL name
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {"message": "Password changed successfully"}

    # Verify the password was changed
    patient = PatientManager.filter_by("email", "patient@example.com")
    assert check_password("newpassword", patient['password'])