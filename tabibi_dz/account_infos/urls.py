from django.urls import path
from .views import ChangePasswordDOCAPIView, ChangePasswordPatientAPIView

urlpatterns = [
    path('doc/change-password/', ChangePasswordDOCAPIView.as_view(), name='change_password'),
    path('patient/change-password/', ChangePasswordPatientAPIView.as_view(), name='changep_password'),
]