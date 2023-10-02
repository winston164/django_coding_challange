from rest_framework import routers
from .views import NotifyRequestViewSet

notification_router = routers.SimpleRouter()
notification_router.register(r'notify', NotifyRequestViewSet)
