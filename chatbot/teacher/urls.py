from . import views
from django.urls import path

urlpatterns = [
    path('teacher/', views.teacher, name='teacher'),
    path('teacher/teaching-modules', views.teaching_modules, name='teaching_modules'),
    path('teacher/student-progress', views.student_progress, name='student_progress'),
    path('teacher/student-progress/<str:instrument_minor>/<str:instrument_major>/<int:book_id>/', views.student_progress, name='student_progress'),
    path('student_results/<str:student_name>/', views.student_results, name='student_results'),
    path('pass_values/', views.pass_values, name='pass_values'),
     path('update-student-result/<str:student_name>/', views.update_student_result, name='update_student_result'),
]