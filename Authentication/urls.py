from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('signup/otp-verify/', views.otpVerify, name='otpVerify'),
    # Add more paths as needed
]