from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path("", admin_login, name="admin_login"),
    path("index/", index, name="index"),
    path('view_users/', views.view_users, name='view_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
]