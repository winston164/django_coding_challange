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

    def __init__(self, notification: Notification):
        serialized_notification = NotificationSerializer(notification)
        self.context = serialized_notification.data
        self.subject = notification.get_topic_display()

    @classmethod
    def load_template(cls) -> Template:
        """Load the configured template path"""
        return get_template(cls.template_path)

    def send_notification(self, recipient: str):
        """Send the notification using the given context"""
        template = self.load_template()
        message_body = template.render(context=self.context)
        send_mail(
            self.subject, message_body, self.from_email, [recipient], fail_silently=False
        )
