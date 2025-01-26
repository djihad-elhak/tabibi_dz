from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Filter

class SearchDoctorsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        date = request.data.get('date')
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        specialty = request.data.get('specialty')
        coverage = request.data.get('coverage')
        radius = request.data.get('radius', 10)  # Default radius is 10 km

        # Validate required parameters
        if not date or not latitude or not longitude:
            return Response({"error": "Date, latitude, and longitude are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
            radius = float(radius)
        except ValueError:
            return Response({"error": "Latitude, longitude, and radius must be valid numbers"}, status=status.HTTP_400_BAD_REQUEST)

        # Call the search_doctors function
        doctors = Filter.search_doctors(date, latitude, longitude, specialty, coverage, radius)

        return Response(doctors, status=status.HTTP_200_OK)