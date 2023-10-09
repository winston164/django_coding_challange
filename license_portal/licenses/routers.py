from rest_framework import routers

from .views import NotificationViewSet, NotifyRequestViewSet

notification_router = routers.SimpleRouter()
notification_router.register(r"notify", NotifyRequestViewSet)
notification_router.register(r"notifications", NotificationViewSet)
