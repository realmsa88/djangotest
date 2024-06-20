from . import views
from django.urls import path

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
]