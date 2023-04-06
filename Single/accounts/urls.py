from django.urls import path,include,re_path
from .views import *
app_name='accounts'

urlpatterns = [
    
    re_path('validate_phone',ValidatePhoneSendOTP.as_view()),
    re_path('validate_otp',ValidateOTP.as_view()),
    re_path('register',Register.as_view()),
    re_path('login',LoginAPI.as_view()),
    path('test',test)
    
]

