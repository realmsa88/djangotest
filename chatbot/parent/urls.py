from . import views
from django.urls import path

urlpatterns = [
    path('parent/', views.parent, name='parent'),
    path('parent/student-information/', views.student_info, name='student-information'),
    path('parent/student-modules/', views.student_modules,name='student-modules'),
    path('parent/attendance', views.attendance, name='attendance')

]