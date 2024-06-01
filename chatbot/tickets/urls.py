# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-support-ticket/', views.create_support_ticket, name='create_support_ticket'),
    path('support-ticket/<int:ticket_id>/', views.support_ticket_detail, name='ticket_detail'),
    path('create-support-ticket/', views.create_support_ticket, name='create_support_ticket'),
    path('support-ticket/<int:ticket_id>/reply/', views.reply_to_ticket, name='reply_to_ticket'),
    path('support-ticket/<int:ticket_id>/conversation/', views.view_ticket_conversation, name='view_ticket_conversation'),
    path('reply-ticket/<int:ticket_id>/', views.reply_to_ticket, name='reply_to_ticket'),
    path('fetch-new-messages/', views.fetch_new_messages, name='fetch_new_messages'),
    path('fetch-notifications/', views.fetch_notifications, name='fetch_notifications'),  # New URL for fetching notifications
]
