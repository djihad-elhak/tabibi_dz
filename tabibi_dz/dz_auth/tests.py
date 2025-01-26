# register/tests.py
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from dz_auth.models import PatientManager

@pytest.mark.django_db
def test_register_patient():
    client = APIClient()
    url = reverse('register-patient')  # Replace with your actual URL name
    data = {
        'email': 'newpatient@example.com',
        'phone': '1234567890',
        'password': 'testpassword',
        'name': 'New',
        'last_name': 'Patient',
        'birth_date': '1990-01-01',
        'street': '123 Street',
        'latitude': 36.7,
        'longitude': 3.1
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # Verify the patient was created
    patient = PatientManager.filter_by("email", "newpatient@example.com")
    assert patient is not None
    assert patient['name'] == "New"
    assert patient['last_name'] == "Patient"