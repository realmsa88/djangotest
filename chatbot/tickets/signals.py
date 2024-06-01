# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SupportTicket, TicketMessage, Notification

@receiver(post_save, sender=SupportTicket)
def create_ticket_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.created_by,
            message=f"New support ticket created: {instance.title}",
            ticket=instance
        )

@receiver(post_save, sender=TicketMessage)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        # Exclude the sender from receiving the notification
        ticket_users = instance.ticket.users_to_notify.exclude(id=instance.sender.id)
        for user in ticket_users:
            Notification.objects.create(
                user=user,
                message=f"New message in support ticket: {instance.ticket.title}",
                ticket=instance.ticket
            )
