from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=15)
    password = serializers.CharField(max_length=255)

class OTPSerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)


class PersonalInfoSerializer(serializers.Serializer):
    longitude = serializers.IntegerField()
    latitude = serializers.IntegerField()
    street = serializers.CharField(max_length=255)



class doc_personal_info(serializers.Serializer):
    card_id=serializers.CharField(max_length=20)
    name=serializers.CharField(max_length=255)
    last_name=serializers.CharField(max_length=255)
    birth_date=serializers.CharField(max_length=10)


class Form_info(serializers.Serializer):
    speciality=serializers.IntegerField()
    institut=serializers.CharField(max_length=255)
    experience=serializers.IntegerField()

class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(max_length=255)

from rest_framework import serializers


