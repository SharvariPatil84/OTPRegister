from django.urls import path,include,re_path
from .views import *
from . import views
app_name='accounts'

urlpatterns = [
    path('login',Login),
    path('validate_phone',ValidatePhoneSendOTP.as_view()),
    path('validate_otp',ValidateOTP.as_view()),
  
]

