from .models import NotifyRequest
from rest_framework import serializers

class NotifyRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotifyRequest
        fields = [
            'request_datetime',
            'notifications'
        ]
