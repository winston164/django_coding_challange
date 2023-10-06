import json
from datetime import datetime

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.renderers import JSONRenderer
from rest_framework.request import Request
from rest_framework.response import Response

from .models import License, Notification, NotificationTopic, NotifyRequest
from .serializers import NotifyRequestSerializer

ONE_WEEK = timezone.timedelta(days=7)
ONE_MONTH = timezone.timedelta(days=31)

viewsets.ModelViewSet


class NotifyRequestViewSet(viewsets.ViewSet):
    """API endpoint to view notification"""

    queryset = NotifyRequest.objects.all()
    serializer = NotifyRequestSerializer

    def create(self, request: Request):
        notify_req = NotifyRequest.objects.create()
        date_now = timezone.now()

        licenses: [License] = License.objects.all()

        for client_license in licenses:
            exp_date = client_license.expiration_datetime
            exp_delta = exp_date - date_now
            
            expires_in_week = exp_delta < ONE_WEEK

            expires_in_month = exp_delta < ONE_MONTH
            today_is_monday = date_now.weekday() == 0
            is_monday_warning = expires_in_month and today_is_monday

            if expires_in_week or is_monday_warning:
                message = ""
                notification = Notification.objects.create(
                    topic=NotificationTopic.expiration_warning,
                    client=client_license.client,
                    message=message,
                    user=client_license.client.admin_poc,
                )
                notification.licenses.set([client_license])
                notify_req.notifications.add(notification)
                break

        notify_req.save()

        serialized_response = NotifyRequestSerializer(notify_req)
        return Response(serialized_response.data, status=status.HTTP_200_OK)
