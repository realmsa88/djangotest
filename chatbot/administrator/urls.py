from . import views, student_views
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('administrator/dashboard', views.administrator, name='dashboard'),
    path('administrator/student/delete_account/<str:username>/', views.delete_account, name='delete_account'),
    path('administrator/', views.dashboard, name='administrator'),
    path('administrator/accounts/', views.accounts, name='accounts'),
    path('administrator/student/', views.student, name='student'),
    # path('administrator/student/register-student/', views.registerStudent, name='register-student'),
    path('register-student/', views.registerStudent, name='register-student'),
    path('delete-student/<str:username>/', views.delete_student, name='delete-student'),
    path('administrator/modules/', views.modules, name = 'modules'),
    path('administrator/modules/book_detail/<int:book_id>/<str:instrument_minor>/<str:instrument_major>/', views.book_detail, name='book_detail'),
    path('administrator/modules/delete_module/<int:module_id>/', views.delete_module, name='delete_module'),
    path('add_module/', views.add_module, name='add_module'),
    path('get-teacher-classes/<int:teacher_id>/', views.get_teacher_classes, name='get_teacher_classes'),
    path('students/', views.student_list, name='student_list'),
    path('get-books/<int:instrument_id>/', views.get_books, name='get_books'),
    path('get-teachers/<int:instrument_id>/', views.get_teachers, name='get_teachers'),
    path('administrator/modules/register-modules', views.register_modules, name = 'register-modules'),
    path('administrator/activity/', views.activity, name = 'activity'),
    path('delete-activity/<int:activity_id>/', views.delete_activity, name='delete-activity'),
    path('administrator/activity/register-activity', views.registerActivity, name = 'register-activity'),
    path('administrator/activity/register-activity/<str:success_message>/', views.registerActivity, name='register-activity'),
    path('administrator/media/activity-details/<int:id>/', views.activity_details, name='activity-details-admin'),
    path('administrator/accounts/register', views.register, name='register'),
    path('administrator/media/', views.media, name='media'),
    # path('administrator/accounts/drawer', views.drawer,name='drawer'),
    path('administrator/accounts/navbar', views.navbar,name='navbar'),
    path('administrator/accounts/navbartest', views.navbartest,name='navbartest'),
    path('success/',views.success, name='success'),
    path('administrator/modules/delete_book/<int:book_id>/', views.delete_book, name='delete_book'),
    # path('administrator/get_students_by_instrument/', views.get_students_by_instrument, name='get_students_by_instrument'),
    path('administrator/fetch_students/<int:instrument_id>/', views.fetch_students, name='fetch_students'),
    path('fetch_teachers/', views.fetch_teachers, name='fetch_teachers'),
    path('activity/details/<int:activity_id>/', views.activity_students_list, name='activity-students-list'),
    path('administrator/billing', views.billing, name='billing'),

    # path('stripe-webhook/', views.stripe_webhook, name='stripe_webhook'),
    # path('checkout/', views.checkout_view, name='checkout_view'),
]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)