from . import views
from django.urls import path

urlpatterns = [
    path('teacher/', views.teacher, name='teacher'),
    path('teacher/teaching-modules', views.teaching_modules, name='teaching_modules'),
    path('teacher/student-progress', views.student_progress, name='student_progress'),
    path('teacher/student-attendance-view', views.student_attendance_view, name='student_attendance_view'),
    path('teacher/student-progress/<str:instrument_minor>/<str:instrument_major>/<int:book_id>/', views.student_progress, name='student_progress'),
    path('student_results/<str:student_name>/', views.student_results, name='student_results'),
    path('pass_values/', views.pass_values, name='pass_values'),
    path('teacher/student-attendance/', views.attendance, name='student-attendance'),
    path('teacher/activity-list/', views.activity_list_teacher, name='activity-list' ),
    #  path('teacher/student-attendance/<str:student_name>/', views.attendance, name='student_attendance'),
    path('students-for-date/<str:date>/', views.students_for_date, name='students-for-date'),
    path('teacher/students-by-book/<str:instrument_minor>/<str:instrument_major>/<int:book_id>/', views.student_list_by_book, name='students_by_book'),
    path('update-student-result/<str:student_name>/', views.update_student_result, name='update_student_result'),
    path('teacher/attendance-list/', views.attendance_list, name='attendance-list'),
    path('verify-attendance/', views.verify_attendance, name='verify-attendance'),
    path('get_attendance/<int:student_id>/', views.get_attendance, name='get_attendance'),
    path('attend-student/', views.attend_student, name='attend_student'),
    path('teacher/media-teacher', views.media, name='media-teacher'),
    path('teacher/media/activity-details/<int:id>/', views.activity_details, name='activity-details'),
    # path('performers/', views.performers, name='performers'),
]

