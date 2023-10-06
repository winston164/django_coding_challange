from rest_framework import serializers

from .models import Notification, NotifyRequest


class NotificationSerializer(serializers.ModelSerializer):
    client_info = serializers.SerializerMethodField()
    expiring_licenses = serializers.SerializerMethodField()
    admin_name = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            "topic",
            "send_datetime",
            "message",
            "client_info",
            "expiring_licenses",
            "admin_name",
        ]

    def get_client_info(self, obj):
        return str(obj.client)

    def get_expiring_licenses(self, obj):
        return [
            {
                "type": lic.get_license_type_display(),
                "package": lic.get_package_display(),
                "expiration_date": lic.expiration_datetime.strftime("%Y-%m-%d"),
            }
            for lic in obj.licenses.all()
        ]

    def get_admin_name(self, obj):
        return obj.user.username


class NotifyRequestSerializer(serializers.ModelSerializer):
    notifications = serializers.SerializerMethodField()

    class Meta:
        model = NotifyRequest
        fields = ["request_datetime", "notifications"]

    def get_notifications(self, obj):
        return [
            NotificationSerializer(notification).data
            for notification in obj.notifications.all()
        ]
