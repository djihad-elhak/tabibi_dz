from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .models import baseUserManager
from .serializers import ChangePasswordSerializer
from dz_auth.models import PatientManager, DoctorManager
from dz_auth.views import get_authenticated_user

class ChangePasswordDOCAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user=get_authenticated_user(request, DoctorManager)

            current_password = serializer.validated_data['password']
            new_password = serializer.validated_data['new_password']
            email=DoctorManager.get_emai(user)

            # Verify current password
            if not DoctorManager.check__password(email, current_password):
                return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            # Update password
            baseUserManager.change_password('doctor', user, new_password)
            response = Response()
            response.delete_cookie('jwt')
            

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    



class ChangePasswordPatientAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user=get_authenticated_user(request, PatientManager)

            current_password = serializer.validated_data['password']
            new_password = serializer.validated_data['new_password']
            email=DoctorManager.get_emai(user)

            # Verify current password
            if not PatientManager.check__password(email, current_password):
                return Response({"error": "Current password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

            # Update password
            baseUserManager.change_password('patient', user, new_password)
            response = Response()
            response.delete_cookie('jwt')
            

            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)