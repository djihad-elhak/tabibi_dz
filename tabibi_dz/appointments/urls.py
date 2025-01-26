from .views import DeclareFreeSessions, ChangeSessions, book_appointment,get_patient_bookings, get_doctor_bookings, get_doctor_history_bookings, get_patient_histroy_bookings,rate_doctor,get_doctor_rating, get_doctor_ratings_comments
from django.urls import path

urlpatterns = [
    path('doctor/declare_free_sessions/', DeclareFreeSessions.as_view(), name='declare_free_sessions'),
    path('doctor/change_sessions/', ChangeSessions.as_view(), name='change_sessions'),
    path('available_sessions/', DeclareFreeSessions.as_view(), name='available_sessions'),
    path('<int:doctor_id>/book_appointment/', book_appointment.as_view(), name='book_appointment'),

    path('patient/bookings/', get_patient_bookings, name='patient_bookings'),
    path('doctor/bookings/', get_doctor_bookings, name='doctor_bookings'),
    path('doc/history/', get_doctor_history_bookings, name='doctor_history'),
    path('patient/history/', get_patient_histroy_bookings, name='patient_history'),
    #commnets and ratings
    path('doctor/ratings/<int:doctor_id>/', get_doctor_ratings_comments, name='doctor_ratings'),
    path('doctor/final_rating/<int:doctor_id>/', get_doctor_rating, name='doctor_rating'),
    path('rate/<int:doctor_id>/', rate_doctor, name='rating'),

    
]