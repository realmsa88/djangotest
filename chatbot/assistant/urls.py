from django.urls import path
from . import views, pipeline, zendesk


urlpatterns = [
    # path('', views.index, name='index'),
    path('', views.chat, name='chat'),
    path('test/', pipeline.check, name='check'),
    path('zendesk/', zendesk.zendesk, name='zendesk')
    # path('pass_to_admin/', views.pass_to_admin, name='pass_to_admin'),
    # path('check/', views.test, name='test'),
]
