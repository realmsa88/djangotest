# views.py
import datetime
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SupportTicket, TicketMessage, Notification
from .forms import SupportTicketForm,  TicketReplyForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone  # Import timezone module


@login_required
def create_support_ticket(request):
    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            
            # Send email notification
            send_ticket_notification(ticket)
            
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = SupportTicketForm()
    return render(request, 'create_support_ticket.html', {'form': form})


@login_required
def support_ticket_detail(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    # Fetch all messages related to the ticket, both from users and admins
    ticket_messages = TicketMessage.objects.filter(ticket=ticket).order_by('sent_at')
    user_messages = TicketMessage.objects.filter(ticket=ticket, sender=request.user).order_by('sent_at')
    
    # Combine both types of messages
    all_messages = ticket_messages | user_messages
    
    return render(request, 'support_ticket_detail.html', {'ticket': ticket, 'messages': all_messages})
@login_required
def reply_to_ticket(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    
    if request.method == 'POST':
        form = TicketReplyForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.ticket = ticket
            message.sender = request.user
            message.save()
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketReplyForm()

    return render(request, 'reply_to_ticket.html', {'form': form, 'ticket': ticket})

@login_required
def view_ticket_conversation(request, ticket_id):
    ticket = get_object_or_404(SupportTicket, id=ticket_id)
    messages = TicketMessage.objects.filter(ticket=ticket).order_by('sent_at')
    return render(request, 'view_ticket_conversation.html', {'ticket': ticket, 'messages': messages})

def fetch_new_messages(request):
    # Retrieve last_seen_timestamp from the request GET parameters
    last_seen_timestamp_str = request.GET.get('last_seen_timestamp')

    # Convert last_seen_timestamp to a datetime object if it exists
    if last_seen_timestamp_str:
        last_seen_timestamp = timezone.make_aware(datetime.fromisoformat(last_seen_timestamp_str))
    else:
        # If last_seen_timestamp is not provided, set it to the earliest possible timestamp in the database
        last_seen_timestamp = TicketMessage.objects.earliest('sent_at').sent_at

    # Retrieve new messages from the database based on last_seen_timestamp
    new_messages = TicketMessage.objects.filter(sent_at__gt=last_seen_timestamp)

    # Serialize the new messages into JSON format
    messages_data = [{'message': message.message, 'sender': message.sender.username, 'sent_at': message.sent_at} for message in new_messages]

    # Return the new messages as JSON response
    return JsonResponse({'messages': messages_data})


def fetch_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user, status='unread')
    # Serialize notifications and return them as JSON response
    return JsonResponse({'notifications': notifications})


def send_ticket_notification(ticket):
    subject = 'New Support Ticket Created: {}'.format(ticket.title)
    message = render_to_string('email/new_ticket_notification.html', {'ticket': ticket})
    sender_email = 'tickets@example.com'  # Update with your sender email address
    recipient_email = ticket.created_by.email  # Assuming the ticket creator's email is used for notifications
    send_mail(subject, message, sender_email, [recipient_email])