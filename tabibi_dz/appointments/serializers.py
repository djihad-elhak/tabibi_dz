from rest_framework import serializers




class SessionsSerializer(serializers.Serializer):
    date = serializers.DateField()
    available_sessions = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=13)
    )

class appointment_serializer(serializers.Serializer):
    appointment_type = serializers.CharField()
    schedule = serializers.IntegerField()
    date = serializers.DateField()
    link = serializers.CharField(required=False)

