from . import views, student_views
from django.urls import path
from .views import delete_book_detail
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('administrator/dashboard', views.administrator, name='dashboard'),
    path('administrator/student/delete_account/<str:username>/', views.delete_account, name='delete_account'),
    path('administrator/', views.dashboard, name='administrator'),
    path('administrator/accounts/', views.accounts, name='accounts'),
    path('administrator/student/', views.student, name='student'),
    path('administrator/student/register-student/', views.registerStudent, name='register-student'),
    path('administrator/modules/', views.modules, name = 'modules'),
    path('administrator/modules/book_detail/<int:book_id>/<str:instrument_minor>/<str:instrument_major>/', views.book_detail, name='book_detail'),
    path('administrator/modules/delete_module/<int:module_id>/', views.delete_book_detail, name='delete_book_detail'),
    path('add_module/', views.add_module, name='add_module'),
    path('get-books/<int:instrument_id>/', views.get_books, name='get_books'),
    path('administrator/activity/', views.activity, name = 'activity'),
    path('administrator/activity/register-activity', views.registerActivity, name = 'register-activity'),
    path('administrator/activity/register-activity/<str:success_message>/', views.registerActivity, name='register-activity'),
    path('administrator/media/activity-details/<int:id>/', views.activity_details, name='activity-details'),
    path('administrator/accounts/register', views.register, name='register'),
    path('administrator/media/', views.media, name='media'),
    # path('administrator/accounts/drawer', views.drawer,name='drawer'),
    path('administrator/accounts/navbar', views.navbar,name='navbar'),
    path('administrator/accounts/navbartest', views.navbartest,name='navbartest'),
    path('success/',views.success, name='success'),
  

]+ static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])