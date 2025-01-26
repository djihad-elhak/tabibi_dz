# Django Imports
from django.conf import settings
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.core.mail import send_mail, EmailMultiAlternatives, BadHeaderError
from django.db import models
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist

from jwt import decode
from jwt.exceptions import DecodeError, ExpiredSignatureError
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes

# Models & Serializers Imports
from .models import PatientManager, DoctorManager, DoctorForm, Adminsrator
from .serializers import RegisterSerializer,OTPSerializer,PersonalInfoSerializer,doc_personal_info,Form_info,PasswordSerializer

# External Libraries
import random
import requests







import json
from django.http import JsonResponse
from django.db import connections

def get_all_patients(request):
    # Connect to the database
    
    patients=PatientManager.fetch_all_patients()

    return JsonResponse({'patients': patients})

from django.shortcuts import render

# Create your views here.
def generate_otp():
    return ''.join(random.choices('0123456789', k=6))


def send_otp(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)

class Forgot_Password(APIView): 
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        patient = PatientManager.filter_by('email', email)
        if not patient:
            doctor=DoctorManager.filter_by('email', email)
            if not doctor:
                return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
            
        otp = generate_otp()
        request.session['email'] = email
        request.session['otp'] = otp
        request.session.save()
        send_otp(email, otp)
        return Response({"message": "OTP sent to email"}, status=status.HTTP_200_OK)
from account_infos.models import baseUserManager

class OTP(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            # Inside your view
            print("hello ",request.session.keys())  # Check if OTP is being stored in session

            otp = serializer.validated_data['otp']
            stored_otp = request.session.get('otp')

            if not stored_otp:
                return Response({"error": "OTP not found or expired"}, status=status.HTTP_400_BAD_REQUEST)

            if otp == stored_otp:
                request.session['otp_verified'] = True
                return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class New_Password1(APIView):
    def post(self, request, *args, **kwargs):
        if not request.session.get('otp_verified'):
            return Response({"error": "OTP verification is required"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = request.session.get('email')
            password = serializer.validated_data['new_password']
            patient = PatientManager.filter_by('email', email)
            if patient:
                baseUserManager.change_password('patient', patient.get('card_id'), password)
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            doctor = DoctorManager.filter_by('email', email)
            if doctor:
                baseUserManager.change_password('doctor', doctor.get('doctor_id'), password)
                return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        
        
        

            

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    
    
# views.py
class RegisterStep1View_doc(APIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        # Initialize the serializer with the request data
        serializer = RegisterSerializer(data=request.data)
        
        # Validate the serializer
        if serializer.is_valid():
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']
            
            # Check if email or phone already exist in the database (using raw SQL)
            if DoctorManager.filter_by('email', email):
                return Response({"error": "Email is already in use"}, status=status.HTTP_400_BAD_REQUEST)
            if DoctorManager.filter_by('phone', phone):
                return Response({"error": "Phone number is already in use"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Store the information in the session
            request.session['step1'] = {'email': email, 'phone': phone, 'password': password}
            
            # Generate an OTP and store it in the session
            otp = generate_otp()
            request.session['otp'] = otp
            request.session.save() 
            print("nihao ",request.session['otp'])
            
            # Send OTP (could be email or SMS)
            send_otp(email, otp)
             
            # Return success response
            return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)
        
        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    







class RegisterStep1View(APIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        # Initialize the serializer with the request data
        serializer = RegisterSerializer(data=request.data)
        
        # Validate the serializer
        if serializer.is_valid():
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            password = serializer.validated_data['password']
            
            # Check if email or phone already exist in the database (using raw SQL)
            if PatientManager.filter_by('email', email):
                return Response({"error": "Email is already in use"}, status=status.HTTP_400_BAD_REQUEST)
            if PatientManager.filter_by('phone', phone):
                return Response({"error": "Phone number is already in use"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Store the information in the session
            request.session['step1'] = {'email': email, 'phone': phone, 'password': password}
            
            # Generate an OTP and store it in the session
            otp = generate_otp()
            request.session['otp'] = otp
            request.session.save() 
            print("nihao ",request.session['otp'])
            
            # Send OTP (could be email or SMS)
            send_otp(email, otp)
             
            # Return success response
            return Response({"message": "OTP sent to email"}, status=status.HTTP_201_CREATED)
        
        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class VerifyOTPView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = OTPSerializer(data=request.data)
        if serializer.is_valid():
            # Inside your view
            print("hello ",request.session.keys())  # Check if OTP is being stored in session

            otp = serializer.validated_data['otp']
            stored_otp = request.session.get('otp')

            if not stored_otp:
                return Response({"error": "OTP not found or expired"}, status=status.HTTP_400_BAD_REQUEST)

            if otp == stored_otp:
                request.session['otp_verified'] = True
                return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegisterStep3View(APIView):
    serializer_class = PersonalInfoSerializer

    def post(self, request, *args, **kwargs):
        if not request.session.get('otp_verified'):
            return Response({"error": "OTP verification is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PersonalInfoSerializer(data=request.data)
        if serializer.is_valid():
            print(serializer)
            personal_info = serializer.validated_data
            # Store personal information in session
            request.session['step3'] = personal_info
            request.session.save()  # Ensure session is saved
            # Store personal information in session
            return Response({"message": personal_info}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

import re

from datetime import datetime

def format_birthdate(birthdate_str):
    """
    Formats a birthdate from YYMMDD to YYYY-MM-DD.
    """
    formatted_date = datetime.strptime(birthdate_str, '%y%m%d').strftime('%Y-%m-%d')

    return formatted_date
def extract_details(parsed_text):
    """
    Extracts the name, last name, birthdate, and ID number from the OCR parsed text.
    """
    name_pattern = r'Prénom\(s\):\s*([\w\s]+)'
    last_name_pattern = r'Nom:\s*(\w+)'
    birthdate_pattern = r'(\d{6})(?=\d{1}[MF])'  # Updated pattern for birthdate

    id_number_pattern = r'IDDZA(\d+)'

    name_match = re.search(name_pattern, parsed_text)
    last_name_match = re.search(last_name_pattern, parsed_text)
    birthdate_match = re.search(birthdate_pattern, parsed_text)
    id_number_match = re.search(id_number_pattern, parsed_text)

    name = name_match.group(1).strip().split('\n')[0] if name_match else ''
    last_name = last_name_match.group(1).strip() if last_name_match else ''
    birthdate = format_birthdate(birthdate_match.group(1) if birthdate_match else '') 
    id_number = id_number_match.group(1) if id_number_match else ''

    return {
        'name': name,
        'last_name': last_name,
        'birth_date': birthdate,
        'id_number': id_number
    }

def ocr_space_api(file_path, overlay=False, api_key='YOUR_API_KEY', language='eng'):
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
        'OCREngine' : 2,
    }
    with open(file_path, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={file_path: f},
                          data=payload,
                          )
    return r.json()


import os
from .forms import UploadFileForm  # Make sure to import your form

class RegisterStep4View(APIView):
    def post(self, request, *args, **kwargs):
        
        
        
        
        # Perform OCR on the uploaded file
        result = request.data.get('result')
        
        # Check for errors in OCR response
        if not result or 'ParsedResults' not in result:
            return Response({"error": "Failed to extract text from the image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        parsed_text = result.get('ParsedResults', [{}])[0].get('ParsedText', '')
        ocr_data = extract_details(parsed_text)

        # Retrieve personal info from session
        personal_info = request.session.get('step3', None)
        if not personal_info:
            return Response({"error": "Personal info is missing from session"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the ID already exists
        if PatientManager.fetch_patient_by_id(ocr_data.get('id_number')):
            return Response({"error": "ID number is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if step1 data is missing from session
        if 'step1' not in request.session:
            return Response({"error": "Step 1 data is missing in session"}, status=status.HTTP_400_BAD_REQUEST)
        
        street = personal_info.get('street')
        
        if not street:
            return Response({"error": " address is missing from session"}, status=status.HTTP_400_BAD_REQUEST)
        from django.db import connection

        card_id=ocr_data.get('id_number')
        name=str(ocr_data.get('name'))
        last_name=str(ocr_data.get('last_name'))
        email=str(request.session['step1']['email'])
        phone=int(request.session['step1']['phone'])
        password=str(request.session['step1']['password'])
        birth_date=str(ocr_data.get('birth_date'))
        street=personal_info.get('street')
        longitude=personal_info.get('longitude')
        latitude=personal_info.get('latitude') 
        try:
            PatientManager.create_patient(
                card_id=card_id,
                name=name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                birth_date=birth_date,
                street=street,
                latitude=latitude,
                longitude=longitude

            )
        except Exception as e:
            return Response({"error": f"Failed to create patient:{ocr_data}, {card_id},{name},{last_name},{email},{phone},{password},{street},{latitude},{longitude},{birth_date},{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Client created successfully"}, status=status.HTTP_201_CREATED)
    

"""class RegisterStep4View(APIView):
    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        
        # Validate form
        if not form.is_valid():
            return Response({"error": "Invalid form submission"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file to the server
        file_name = file.name
        file_path = os.path.join(os.path.dirname(__file__), 'uploads', file_name)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Perform OCR on the uploaded file
        result = ocr_space_api(file_path, api_key='K87236353188957')
        
        # Check for errors in OCR response
        if not result or 'ParsedResults' not in result:
            return Response({"error": "Failed to extract text from the image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        parsed_text = result.get('ParsedResults', [{}])[0].get('ParsedText', '')
        ocr_data = extract_details(parsed_text)

        # Retrieve personal info from session
        personal_info = request.session.get('step3', None)
        if not personal_info:
            return Response({"error": "Personal info is missing from session"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the ID already exists
        if PatientManager.fetch_patient_by_id(ocr_data.get('id_number')):
            return Response({"error": "ID number is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if step1 data is missing from session
        if 'step1' not in request.session:
            return Response({"error": "Step 1 data is missing in session"}, status=status.HTTP_400_BAD_REQUEST)
        
        street = personal_info.get('street')
        
        if not street:
            return Response({"error": " address is missing from session"}, status=status.HTTP_400_BAD_REQUEST)
        from django.db import connection

        card_id=ocr_data.get('id_number')
        name=str(ocr_data.get('name'))
        last_name=str(ocr_data.get('last_name'))
        email=str(request.session['step1']['email'])
        phone=int(request.session['step1']['phone'])
        password=str(request.session['step1']['password'])
        birth_date=str(ocr_data.get('birth_date'))
        street=personal_info.get('street')
        longitude=personal_info.get('longitude')
        latitude=personal_info.get('latitude') 
        try:
            PatientManager.create_patient(
                card_id=card_id,
                name=name,
                last_name=last_name,
                email=email,
                phone=phone,
                password=password,
                birth_date=birth_date,
                street=street,
                latitude=latitude,
                longitude=longitude

            )
        except Exception as e:
            return Response({"error": f"Failed to create patient:{ocr_data}, {card_id},{name},{last_name},{email},{phone},{password},{street},{latitude},{longitude},{birth_date},{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Client created successfully"}, status=status.HTTP_201_CREATED)
    """

class RegisterStep4_doc(APIView):
    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
        
        # Validate form
        if not form.is_valid():
            return Response({"error": "Invalid form submission"}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file to the server
        file_name = file.name
        file_path = os.path.join(os.path.dirname(__file__), 'uploads', file_name)
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Perform OCR on the uploaded file
        result = ocr_space_api(file_path, api_key='K87236353188957')
        
        # Check for errors in OCR response
        if not result or 'ParsedResults' not in result:
            return Response({"error": "Failed to extract text from the image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        parsed_text = result.get('ParsedResults', [{}])[0].get('ParsedText', '')
        ocr_data = extract_details(parsed_text)

        # Retrieve personal info from session
        personal_info = request.session.get('step3', None)
        if not personal_info:
            return Response({"error": "Personal info is missing from session"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the ID already exists
        if DoctorManager.fetch_doctor_by_id(ocr_data.get('id_number')):
            return Response({"error": "ID number is already in use"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if step1 data is missing from session
        if 'step1' not in request.session:
            return Response({"error": "Step 1 data is missing in session"}, status=status.HTTP_400_BAD_REQUEST)
        
        street = personal_info.get('street')
        
        if not street:
            return Response({"error": "address  is missing from session"}, status=status.HTTP_400_BAD_REQUEST)
        from django.db import connection

        card_id=ocr_data.get('id_number')
        name=str(ocr_data.get('name'))
        last_name=str(ocr_data.get('last_name'))
        birth_date=str(ocr_data.get('birth_date')) 

        try:
                request.session['step4'] = {
                    'card_id': card_id,
                    'name': name,
                    'last_name': last_name,
                    'birth_date': birth_date
                }
        except Exception as e:
                # Handle any exception (e.g., session issues, missing data)
                return Response({"error": f"Error saving data to session:{birth_date},{ocr_data}, {card_id},{name},{last_name}, {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
        return Response({"message": "info filled succesfully successfully"}, status=status.HTTP_201_CREATED)
    



class RegisterStep5View(APIView):
    serializer_class = Form_info

    def post(self, request, *args, **kwargs):
        # Ensure 'step4' data is available in session
        if 'step4' not in request.session:
            return Response({"error": "Step 4 data is missing in session"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the data from the request
        serializer = Form_info(data=request.data)
        if serializer.is_valid():
            # Extract form information
            form_info = serializer.validated_data
            speciality = form_info.get('speciality')
            institut = form_info.get('institut')
            experience = form_info.get('experience')

            # Attempt to store the data in the session
            try:
                request.session['step5'] = {
                    'speciality': speciality,
                    'institut': institut,
                    'experience': experience
                }
                request.session.save()  # Persist the session
            except Exception as e:
                return Response({"error": f"Error saving step5 data to session: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Return a success response
            return Response({"message": "Professional info added successfully"}, status=status.HTTP_201_CREATED)

        # If validation fails, return serializer errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UploadDocDocument(APIView):
    def post(self, request, *args, **kwargs):
        form = UploadFileForm(request.POST, request.FILES)
            
            # Validate form
        if not form.is_valid():
            return Response({"error": "Invalid form submission"}, status=status.HTTP_400_BAD_REQUEST)
            
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        email=str(request.session['step1']['email'])
        phone=int(request.session['step1']['phone'])
        password=str(request.session['step1']['password'])
        card_id=request.session['step4']['card_id']
        name=request.session['step4']['name']
        last_name=request.session['step4']['last_name']
        birth_date=request.session['step4']['birth_date']
        speciality=request.session['step5']['speciality']
        institut=request.session['step5']['institut']
        experience=request.session['step5']['experience']
        street=request.session['step3']['street']
        latitude=request.session['step3']['latitude']
        longitude=request.session['step3']['longitude']
        
        DoctorForm.create_form(
            email=email,
            phone=phone,
            password=password,
            card_id=card_id,
            name=name,
            last_name=last_name,
            birth_date=birth_date,
            speciality=speciality,
            institut=institut,
            experience=experience,
            document=file,
            street=street,
            latitude=latitude,
            longitude=longitude

        )
        return Response({"message": "Document uploaded successfully"}, status=status.HTTP_201_CREATED)
                   
            
            # Save the file to the server
            

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

#Login
import jwt 
def get_authenticated_user(request, Manager):
    token=request.COOKIES.get('jwt')
    print("this is the token",token)
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print("This is the payload",payload)
    except InvalidTokenError:
        return None
    id=payload.get('id')
    password=payload.get('password')
    email=payload.get('email')
    if Manager.filter_by("email", email).get('password') == password:
        return id
    return None

    

class BaseLoginAPIView(APIView):
    def authenticate_user(self, user,id_type):
        # Create JWT payload without expiration
        payload = {
            'id': user[id_type],
            'password' : user['password'],
            'email': user['email'],


        }

        # Encode the token
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        # Prepare the response
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {'jwt': token}
        response.status_code = status.HTTP_200_OK

        return response

    def post(self, request, *args, **kwargs):
        # This method should be overridden by subclasses
        raise NotImplementedError("Subclasses should implement this method")


class PatientLoginAPIView(BaseLoginAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Fetch the patient by email
        patient = PatientManager.filter_by('email', email)
        if patient and PatientManager.check__password(email, password):
            return self.authenticate_user(patient,'card_id')
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class DoctorLoginAPIView(BaseLoginAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Fetch the doctor by email
        doctor = DoctorManager.filter_by('email',email)
        if doctor and DoctorManager.check__password(email, password):
            return self.authenticate_user(doctor,'doctor_id')
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)


class ManagerLoginAPIView(BaseLoginAPIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        # Fetch the manager by email
        manager = Adminsrator.filter_by('email', email)
        if manager and Adminsrator.check__password(email, password):
            return self.authenticate_user(manager,'id')
        
        return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)





class ShowDoctorDocumentAPI(APIView):

    def get(self, request, doctor_id, *args, **kwargs):
        document = DoctorForm.fetch_document_by_id(doctor_id)
        if document is None:
            return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)

        response = HttpResponse(document, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="document_{doctor_id}.pdf"'
        return response
    

@api_view(['GET'])

def get_document(request, doctor_id):
    user=get_authenticated_user(request, Adminsrator)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)

    document = DoctorForm.fetch_document_by_id(doctor_id)
    if document is None:
        return Response({"error": "Document not found "}, status=status.HTTP_404_NOT_FOUND)

    response = HttpResponse(document, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="document_{doctor_id}.pdf"'
    return response

@api_view(['GET'])
def get_doctor_forms(request):
    # Connect to the database
    forms=DoctorForm.fetch_all_doctor_forms()
    # Fetch all specialities
    specialities = DoctorForm.fetch_all_specialities()

    # Replace the speciality key with the actual speciality name
    for form in forms:
        
        speciality_key = form['speciality']
        form['speciality'] = specialities
    # Remove the document field from each form as it is not serializable
    for form in forms:
        form.pop('document', None)


    return JsonResponse({'forms': forms})

@api_view(['POST'])
def approve_doctor(request, doctor_id):
    user=get_authenticated_user(request, Adminsrator)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    if not DoctorForm.filter_by_id(doctor_id):
        return Response({"error": "form not found"}, status=status.HTTP_404_NOT_FOUND)
    email = DoctorForm.get_email(doctor_id)

    subject = 'Your OTP Code'
    message = f'your doctor application is approved, welcome to TABIBI DZ'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email]

    send_mail(subject, message, email_from, recipient_list)

    Adminsrator.approve_doctor(doctor_id, True)
    return Response({"message": "Doctor approved successfully"}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reject_doctor(request, doctor_id):
    user=get_authenticated_user(request, Adminsrator)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    if not DoctorForm.filter_by_id(doctor_id):
        return Response({"error": "form not found"}, status=status.HTTP_404_NOT_FOUND)
    Adminsrator.approve_doctor(doctor_id, False)
    return Response({"message": "Doctor rejected successfully"}, status=status.HTTP_200_OK)
   

        
    
@api_view(['POST'])
def LogoutAPIView(request):
    response = Response()
    response.delete_cookie('jwt')
    response.data = {'message': 'Successfully logged out'}
    response.status_code = status.HTTP_200_OK
    return response

class LogoutAPIView1(APIView):
    def post(self, request, *args, **kwargs):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {'message': 'Successfully logged out'}
        response.status_code = status.HTTP_200_OK
        return response
