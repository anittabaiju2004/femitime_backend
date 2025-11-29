from django.urls import path
from . import views
from .views import *
urlpatterns = [
    path("", admin_login, name="admin_login"),
    path("index/", index, name="index"),
    path('view_users/', views.view_users, name='view_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('view_pending_doctors/', views.view_pending_doctors, name='view_pending_doctors'),

    # Hospital Doctor Actions
    path('approve_hospital_doctor/<int:doctor_id>/', views.approve_hospital_doctor, name='approve_hospital_doctor'),
    path('reject_hospital_doctor/<int:doctor_id>/', views.reject_hospital_doctor, name='reject_hospital_doctor'),

    path('view_approved_doctors/', views.view_approved_doctors, name='view_approved_doctors'),

    path('view_rejected_doctors/', views.view_rejected_doctors, name='view_rejected_doctors'),
]