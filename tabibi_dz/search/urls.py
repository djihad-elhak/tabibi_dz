from django.urls import path
from .views import SearchDoctorsAPIView

urlpatterns = [
    path('search/doctors/', SearchDoctorsAPIView.as_view(), name='search_doctors'),
]