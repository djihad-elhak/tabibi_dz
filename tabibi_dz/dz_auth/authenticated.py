from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import jwt
from django.conf import settings
from .models import PatientManager  # Use the manager you've created for patients

class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = request.cookies.get('Authorization')  # Get token from cookies
        
        if not token:
            raise AuthenticationFailed('Authentication credentials were not provided.')
        
        try:
            # Decode the JWT token with the secret key
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired, please login again.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        # Fetch the patient with the ID from the decoded payload
        patient = PatientManager.fetch_patient_by_id(payload['id'])  # Adjust this to your model's ID field
        
        if patient is None:
            raise AuthenticationFailed('Patient not found.')
        
        return (patient, None)  # Return the authenticated patient instance and None for the authentication backend
