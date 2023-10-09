from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from licenses.notifications import EmailNotification

from .models import Client, License, Notification, NotificationTopic, NotifyRequest
from .serializers import NotifyRequestSerializer, NotificationSerializer

ONE_WEEK = timezone.timedelta(days=7)
ONE_MONTH = timezone.timedelta(days=31)
FOUR_MONTS = ONE_MONTH * 4

def should_warn(lic: License):
    date_now = timezone.now()
    exp_date = lic.expiration_datetime
    exp_delta = exp_date - date_now
    exp_delta = timezone.timedelta(days=exp_delta.days)
    
    expires_in_week = exp_delta < ONE_WEEK

    expires_in_month = exp_delta < ONE_MONTH
    today_is_monday = date_now.weekday() == 0
    is_monday_warning = expires_in_month and today_is_monday

    expires_in_4_months = exp_delta == FOUR_MONTS
    return (expires_in_week or is_monday_warning or expires_in_4_months)

class NotifyRequestViewSet(viewsets.ViewSet):

    queryset = NotifyRequest.objects.all()
    serializer = NotifyRequestSerializer

    def create(self, request: Request):
        notify_req = NotifyRequest.objects.create()
        clients: [Client] = Client.objects.all()

        notifications = []

        for client in clients:
            licenses = client.license_set.all()
            expirations = [lic for lic in licenses if should_warn(lic)]

            if len(expirations) > 0:
                notification = Notification.objects.create(
                    topic=NotificationTopic.expiration_warning,
                    client=client,
                    message="",
                    user=client.admin_poc,
                )
                notification.licenses.set(expirations)
                notification.save()

                EmailNotification.send_notification(notification, client.admin_poc.email)
                

                notifications.append(notification)

        notify_req.notifications.set(notifications)
        notify_req.save()

        serialized_response = NotifyRequestSerializer(notify_req)
        return Response(serialized_response.data, status=status.HTTP_200_OK)

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint to view notifications"""

    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


