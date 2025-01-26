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
from .models import ScheduleManager, BookingManager,Booking ,History_booking, RatingManager
from .serializers import SessionsSerializer,appointment_serializer
# External Libraries
import random
import requests
import json
from django.http import JsonResponse
from django.db import connections
from dz_auth.views import get_authenticated_user
from dz_auth.models import Adminsrator,DoctorManager,PatientManager



class DeclareFreeSessions(APIView):
    def post(self, request):
        user=get_authenticated_user(request, DoctorManager)
        if not user:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = SessionsSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            doctor_id = user
            date = data['date']
            available_sessions = data['available_sessions']

            result = ScheduleManager.declare_free_sessions(doctor_id, date, available_sessions)
            

            return Response({"message": "Free sessions declared successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ChangeSessions(APIView):
    def post(self, request):
        user=get_authenticated_user(request, DoctorManager)
        if not user:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = SessionsSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            doctor_id = user
            date = data['date']
            available_sessions = data['available_sessions']

            result = ScheduleManager.change_sesions(doctor_id, date, available_sessions)
            

            return Response({"message": "Sessions changed successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class book_appointment(APIView):
    def get(self, request, doctor_id):
        user=get_authenticated_user(request, PatientManager)
        if not user:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        result = ScheduleManager.fetch_available_sessions(doctor_id)
        return JsonResponse(result, safe=False)
    def post(self, request,doctor_id):
        user=get_authenticated_user(request, PatientManager)
        if not user:
            return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = appointment_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            patient_id = user
            appointment_type = data['appointment_type']
            schedule = data['schedule']
            date = data['date']
            link = data.get('link', None)

            result = BookingManager.book_appointments(patient_id, doctor_id, appointment_type, schedule, date)
            

            return Response(result, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



@api_view(['GET'])
def get_patient_bookings(request):
    user=get_authenticated_user(request, PatientManager)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    result = Booking.get_patient_bookings(user)
    return JsonResponse(result, safe=False)


@api_view(['GET'])
def get_doctor_bookings(request):
    user=get_authenticated_user(request, DoctorManager)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    result = Booking.get_doctor_bookings(user)
    return JsonResponse(result, safe=False)





@api_view(['GET'])
def get_patient_histroy_bookings(request):
    user=get_authenticated_user(request, PatientManager)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    result = History_booking.get_patient_history(user)
    return JsonResponse(result, safe=False)


@api_view(['GET'])
def get_doctor_history_bookings(request):
    user=get_authenticated_user(request, DoctorManager)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    result = History_booking.get_doctor_history(user)
    return JsonResponse(result, safe=False)






@api_view(['GET'])
def get_doctor_ratings_comments(request,doctor_id):
    ratings = RatingManager.get_ratings(doctor_id)
    return Response(ratings, status=status.HTTP_200_OK)
@api_view(['GET'])

def get_doctor_rating(request,doctor_id):
    rating = RatingManager.get_final_rating(doctor_id)
    return JsonResponse(rating, safe=False)



@api_view(['POST'])
def rate_doctor(request,doctor_id):
    user=get_authenticated_user(request, PatientManager)
    if not user:
        return Response({"error": "Unauthenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    rating = request.data.get('rating')
    comment = request.data.get('comment')
    if not rating:
        return Response({"error": "Rating is required"}, status=status.HTTP_400_BAD_REQUEST)
    RatingManager.add_rating(doctor_id, user, rating, comment)
    return Response({"message": "Rating added successfully"}, status=status.HTTP_201_CREATED)

    

@api_view(['GET'])
def get_patient_bookings(request):
    user_id = request.query_params.get('user_id')
    if not user_id:
        return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    result = Booking.get_patient_bookings(user_id)
    return JsonResponse(result, safe=False)