from django.shortcuts import render
from django.http import HttpResponse
import http.client
# Create your views here.
import json
import requests
import ast
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, generics
# from forms import UserForm
from .models import User, PhoneOTP
from django.shortcuts import get_object_or_404, redirect
import random
from .serializer import CreateUserSerializer
from knox.auth import TokenAuthentication
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

conn = http.client.HTTPConnection("2factor.in")


class ValidatePhoneSendOTP(APIView):

    def post(self, request, *args, **kwargs):
        phone_number = request.data.get('phone')
        password = request.data.get('password', False)
        username = request.data.get('username', False)
        email = request.data.get('email', False)
        role_i=request.data.get('role', False)
        if phone_number:
            phone = str(phone_number)
            user = User.objects.filter(phone__iexact=phone)
            role=role_i
            if user.exists():
                # return Response({
                #     'status' : False,
                #     'detail' : 'Phone number already exists'
                # })
                
                 messages.info(request,'User Already exists')
                 return redirect('/')               
                 

            else:
                key = send_otp(phone)
                if key:
                    old = PhoneOTP.objects.filter(phone__iexact=phone)
                    if old.exists():
                        old = old.first()
                        count = old.count
                        if count > 10:
                           
                            messages.info(request,'Sending otp error. Limit Exceeded. Please Contact Customer support')
                            return redirect('/') 

                        old.count = count + 1
                        old.save()
                        print('Count Increase', count)

                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=eed99c06-d29d-11ed-addf-0200cd936042&to=" +
                                     phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse()

                        data = res.read()
                        data = data.decode("utf-8")
                        data = ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            old.otp_session_id = data["Details"]
                            old.save()
                            print('In validate phone :'+old.otp_session_id)
                            # return Response({
                            #        'status' : True,
                            #        'detail' : 'OTP sent successfully'
                            #     })
                            context = {
                                'phone': phone_number,
                                'username': username,
                                'password': password,
                                'email': email,
                                'role':role

                            }
                            print(context)
                            return render(request, 'enterOtp.html', context)
                        else:
                            messages.info(request,'OTP sending Failed')
                            return redirect('/') 
                           

                    else:

                        obj = PhoneOTP.objects.create(
                            phone=phone,
                            otp=key,
                            email=email,
                            username=username,
                            password=password,
                            role=role
                            
                        )
                        conn.request("GET", "https://2factor.in/API/R1/?module=SMS_OTP&apikey=eed99c06-d29d-11ed-addf-0200cd936042&to=" +
                                     phone+"&otpvalue="+str(key)+"&templatename=WomenMark1")
                        res = conn.getresponse()
                        data = res.read()
                        print(data.decode("utf-8"))
                        data = data.decode("utf-8")
                        data = ast.literal_eval(data)

                        if data["Status"] == 'Success':
                            obj.otp_session_id = data["Details"]
                            obj.save()
                            print('In validate phone :'+obj.otp_session_id)
                            # return Response({
                            #        'status' : True,
                            #        'detail' : 'OTP sent successfully'
                            #     })
                            context = {
                                'phone': phone_number,
                                 'username': username,
                                 'password': password,
                                 'email': email,
                                 'role':role
                            }
                            print(context)
                            return render(request, 'enterOtp.html', context)
                        else:
                            messages.info(request,'OTP sending Failed')
                            return redirect('/') 
                           

                else:
                     messages.info(request,'OTP sending Error')
                     return redirect('/') 
                           

        else:
             messages.info(request,'Phone number is not given in post request')
             return redirect('/') 
                           
            #  return Response({
            #     'status': False,
            #     'detail': 'Phone number is not given in post request'
            # })


def send_otp(phone):
    if phone:
        key = random.randint(999, 9999)
        print(key)
        return key
    else:
        return False


class ValidateOTP(APIView):

    def post(self, request, *args, **kwargs):

        otp_sent = request.data.get('otp', False)
        phone = request.POST["phone"]
        password = request.POST["password"]
        username = request.POST["username"]
        email = request.POST["email"]
        role=request.POST["role"]
        # print(role)
        if phone and otp_sent:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                otp_session_id = old.otp_session_id
                print("In validate otp"+otp_session_id)
                conn.request(
                    "GET", "https://2factor.in/API/V1/eed99c06-d29d-11ed-addf-0200cd936042/SMS/VERIFY/"+otp_session_id+"/"+otp_sent)
                res = conn.getresponse()
                data = res.read()
                print(data.decode("utf-8"))
                data = data.decode("utf-8")
                data = ast.literal_eval(data)

                if data["Status"] == 'Success':
                    old.validated = True
                    old.save()
                   
                    # return Response({
                    #     'status' : True,
                    #     'detail' : 'OTP MATCHED. Please proceed for registration.'
                    #         })

            else:
                messages.info(request,'First Proceed via sending otp request')
                return redirect('/') 
                # return Response({
                #     'status': False,
                #     'detail': 'First Proceed via sending otp request'
                # })

        else:
            messages.info(request,'Please provide both phone and otp for Validation')
            return redirect('/') 
            # return Response({
            #     'status': False,
            #     'detail': 'Please provide both phone and otp for Validation'
            # })

        if phone and password and username and email:
            old = PhoneOTP.objects.filter(phone__iexact=phone)
            if old.exists():
                old = old.first()
                validated = old.validated

                if validated:
                    temp_data = {
                        'username': old.username,
                        'email': old.email,
                        'phone': old.phone,
                        'password': old.password,
                        'role':old.role
                         
                    }
                    serializer = CreateUserSerializer(data=temp_data)
                    serializer.is_valid(raise_exception=True)
                    user = serializer.save()
                    user.set_password(old.password)
                    user.save()
                    print(user)
                    print(old.password)
                    old.delete()
                # return Response({
                #     'status' : True,
                #     'detail' : 'Account Created Successfully'
                #     })
                    return render(request, 'login.html')

                else:
                    messages.info(request,'OTP havent Verified. First do that Step.')
                    # return redirect('/validate_phone') 
                    return Response({
                        'status': False,
                        'detail': 'OTP havent Verified. First do that Step.'
                    })
            else:
                messages.info(request,'Please verify Phone First')
                return redirect('/') 
                return Response({
                    'status': False,
                    'detail': 'Please verify Phone First'
                })

        else:
            messages.info(request,'OTP INCORRECT')
            # return redirect('/validate_phone')
            return Response({
                'status': False,
                'detail': 'OTP INCORRECT'
            })





def Home(request):
    msg=None
    context = {
             msg:None
         }
    return render(request, 'register.html',context)



def Login(request):
    return render(request,'login.html')
