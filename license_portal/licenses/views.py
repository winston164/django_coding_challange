from rest_framework.request import Request
from rest_framework import viewsets
from .models import NotifyRequest
from .serializers import NotifyRequestSerializer

from rest_framework import status
from rest_framework.response import Response

class NotifyRequestViewSet(viewsets.ViewSet):
    """ API endpoint to view notification
    """
    queryset = NotifyRequest.objects.all()
    serializer = NotifyRequestSerializer

    def create(self, request: Request):
        serializer = self.serializer(data=request.data)
        return Response(serializer.initial_data, status=status.HTTP_200_OK)

