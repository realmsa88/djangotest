from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('parent/', views.parent, name='parent'),
    path('parent/student-information/', views.student_info, name='student-information'),
    path('parent/student-modules/', views.student_modules,name='student-modules'),
    path('parent/attendance', views.attendance, name='attendance'),
    path('parent/leave', views.leave, name='leave' ),
    path('parent/activities-list', views.activity_list, name='activities-list'),
    path('parent/<int:student_id>/attendance/<int:attendance_id>/', views.verify_attendance, name='verify_attendance'),
    path('submit_absence/', views.submit_absence, name='submit_absence'),
    path('parent/media-parent', views.media, name='media-parent'),
    path('parent/media/activity-details/<int:id>/', views.activity_details, name='activity-details-parent'),
    path('generate_report/<int:student_id>/', views.generate_report, name='generate_report'),
    path('parent/activity-detail/<int:activity_id>/', views.activity_students_list_parent, name='activity-students-list-parent'),
    path('parent/view_report/<int:student_id>/', views.view_report, name='view_report'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('checkout/', views.checkout_view, name='checkout_view'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)