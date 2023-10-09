from typing import Any, List

from django.core.mail import send_mail
from django.template import Template
from django.template.loader import get_template

from .serializers import NotificationSerializer

from .models import Notification

DEFAULT_FROM_EMAIL = "noreply@email.com"


class EmailNotification:
    """A convenience class to send email notifications"""

    from_email = DEFAULT_FROM_EMAIL  # type: str
    template_path = 'notification-email.html'  # type: str

    @classmethod
    def load_template(cls) -> Template:
        """Load the configured template path"""
        return get_template(cls.template_path)

    @classmethod
    def send_notification(cls, notification: Notification, recipient: str):
        """Send the notification using the given context"""
        serialized_notification = NotificationSerializer(notification)
        context = serialized_notification.data
        subject = notification.get_topic_display()
        template = cls.load_template()
        message_body = template.render(context=context)
        send_mail(
            subject, message_body, cls.from_email, [recipient], fail_silently=False
        )
