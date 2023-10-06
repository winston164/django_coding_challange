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
            if exp_delta < ONE_WEEK:
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
