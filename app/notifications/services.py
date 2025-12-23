from .models import Notification

def create_notification(recipient, title, message, link='', notification_type='system', sender=None):
    """
    Utility function to create a notification.
    """
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        link=link,
        notification_type=notification_type,
        sender=sender
    )
