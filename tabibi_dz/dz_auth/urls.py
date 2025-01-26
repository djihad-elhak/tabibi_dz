from django.urls import path
from .views import (RegisterStep1View,VerifyOTPView,RegisterStep3View,
 RegisterStep4View,get_all_patients,RegisterStep1View_doc ,
 RegisterStep4_doc,RegisterStep5View,UploadDocDocument,
 DoctorLoginAPIView, ManagerLoginAPIView,PatientLoginAPIView,LogoutAPIView,
 get_document,approve_doctor, reject_doctor,get_doctor_forms,Forgot_Password,OTP,New_Password1

 
 )

urlpatterns = [
    #register for patient
    path('register/step1/', RegisterStep1View.as_view(), name='register_step1'),
    path('register/step2/', VerifyOTPView.as_view(), name='register_step2'),
    path('register/step3/', RegisterStep3View.as_view(), name='register_step3'),
    path('register/step4/', RegisterStep4View.as_view(), name='register_step4'),
    path('patients/', get_all_patients, name="patients"),

#register for doctor
    path('register/doc/step1/', RegisterStep1View_doc.as_view(), name='register_step1_doc'),
    path('register/doc/step4/', RegisterStep4_doc.as_view(), name='register_step4_doc'),
    path('register/doc/step5/', RegisterStep5View.as_view(), name='register_step5'),
    path('register/doc/step6/', UploadDocDocument.as_view(), name='UploadDocDocument'),
#login
    path('login/patient/', PatientLoginAPIView.as_view(), name='patient_login'),
    path('login/doctor/', DoctorLoginAPIView.as_view(),name='docotr_login'),
    path('login/admin/', ManagerLoginAPIView.as_view(),name='admin_login'),

    path('logout/', LogoutAPIView, name='logout'),
    path('admin/doctor_forms/', get_doctor_forms, name='doctor_forms'),

    path('admin/approve/<int:doctor_id>/', approve_doctor,name='approved'),
    path('admin/reject/<int:doctor_id>/', reject_doctor,name='rejected'),

    path('admin/document/<int:doctor_id>/', get_document, name='show_doctor_document'),

    #forgot password
    path('forgot_password/', Forgot_Password.as_view(), name='forgot_password'),
    path('otp/', OTP.as_view(), name='otp'),
    path('new_password/', New_Password1.as_view(), name='new_password'),




    ]











