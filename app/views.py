from pyexpat import model
from re import template
from urllib import request
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import FormView
from django.views.generic import CreateView, ListView, DeleteView, TemplateView, UpdateView, ListView, DetailView, View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from formtools.wizard.views import SessionWizardView 
from multi_form_view import MultiFormView

import stripe

from datetime import datetime
# from django.app.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from mysqlx import PoolError
from numpy import product
import pyotp
import base64
import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import redirect
from django.db import models
from django.db.models import Q
from requests import get

#Module for Send email
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

#Speech recognition
import speech_recognition as sr

#Timezone
import pytz

from .form import(
    CreateAccountForm,
    RegisterAccountForm,
    AudioRecorderForm,
    LoginForm,
    OTPForm,
    DrawNumberForm,
    MobileRechargeForm,
    SearchUserForm,
    RequestMoneyForm,
    CCAvenueCheckoutForm,
    MerchantRegistrationForm,
    ProductForm,
    PurchaseForm,
    PaymentForm,
    MerchantDetailsForm,
    ProductVariationForm,
    SaleForm,
    SellReturnForm,
    StockTransferForm,
    StockAdjustmentsForm,
    ExpenseForm,
    ExpenseCategoryForm,
    TaxRatesForm,
    BrandsForm,
    UnitsForm,
    TaxGroupForm,
    CheckoutForm,
    CouponForm,
    RefundForm,
)

from .models import(
    UserModel,
    AudioRecorderModel,
    SampleStringModel,
    OTPVerificationModel,
    BillerInfoModel,
    MobileRechargeBillModel,
    UrlShortnerModel,
    RazorpayTransactionModel,
    MerchantModel,
    ProductModel,
    PurchaseModel,
    PaymentModel,
    ProductVariationsModel,
    TaxRatesModel,
    BrandModel,
    CategoryModel,
    SubcategoryModel,
    SupplierModel,
    SaleModel,
    LocationModel,
    SellReturnModel,
    StockTransferModel,
    StockAdjustmentsModel,
    ExpenseModel,
    ExpenseCategoriesModel,
    BrandModel,
    UnitsModel,
    TaxGroupModel,

    Orderproduct,
    Order,
    BillingAddress,
    Coupon,
    Refund,

)
from . import utils, ccavutil
from datetime import datetime, timedelta
from .number_prediction_API import number_prediction
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice
from django.http import FileResponse
from django.contrib import messages
import cities


import random

class IndexView(View):
    """
    Index View
    """
    def get(self, request):
        merchant = utils.get_subdomain(request)
        print(merchant)
        try:
            m = MerchantModel.objects.get(subdomain_name = merchant)
            self.request.session['email'] = m.merchant.email
            self.request.session['first_name'] = m.merchant.first_name
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))   
        except MerchantModel.DoesNotExist:
            return render(request, 'common/index.html')

class CreateAccountView(CreateView):
    """
    View for create account request
    get:
        Renders create-account.html template
    post:
        This will validate user information and stores it in database
    """
    form_class = CreateAccountForm
    template_name = 'common/create-account.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        try:
            print("Form valid")   
            user = form.save()        
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            self.request.session['email'] = user.email
            self.request.session['user_id'] = user.id            
            return HttpResponseRedirect(reverse('app:setup_voice'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)

class RegisterView(CreateView):
    """
    View for create account request
    get:
        Renders create-account.html template
    post:
        This will validate user information and stores it in database
    """
    form_class = RegisterAccountForm
    template_name = 'common/register.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        try:
            print("Form valid")   
            user_email = self.request.session.get('email')
            print(user_email)

            phone_number = form.cleaned_data['phone_number']
            print(phone_number)
            upi_id = form.cleaned_data['upi_id']
            print(upi_id)
            
            user = UserModel.objects.get(email=self.request.session.get('email'), id=self.request.session.get('user_id'))
            user.phone_number = phone_number
            user.upi_id = upi_id
            user.save()
            return HttpResponseRedirect(reverse('app:paybill_login'))

        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)           

def send_email(request):
    """
    API to send email to specified user using SendGrid WebAPI
    """
    try:
        send_email_status = False
        response_string = str()
        #sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        subject = request["subject"]
        content = Content(request["content_type"], request["content"])
        from_email = Email(request["from_email"]) 
        to_email = To(request["to_email"]) 
        cc_email = Email(request["cc_email"])
    
        if subject and content and to_email and from_email and sg and cc_email:
            mail = Mail(from_email, to_email, subject, content)
            if request["cc_email"] != "":
                p = sendgrid.Personalization()
                p.add_to(to_email)
                p.add_cc(cc_email)
                mail.add_personalization(p)
            response = sg.client.mail.send.post(request_body=mail.get())
            response_string = "Email sent successfully. sendgrid status code :", response.status_code
            send_email_status = True
            return send_email_status, response_string
            
        else:
            response_string = "Please validate the input json"
        return send_email_status, response_string

    except Exception as e:
        print("errMsg:",str(e))
        send_email_status = False
        return send_email_status, str(e)

def generateKey(email):
    """
    API to generate key for OTP generation and verification
    """
    return str(email) + str(datetime.date(datetime.now())) + "Some Random Secret Key"

class GenerateOTPView(View):
    """
    View to generate OTP token
    get:
        Generates OTP token using HOTP algorithm from pyotp library and send it over an email
    """
    def get(self, request):
        try:
            print("path:",request.path)
            try:
                receiver_email = self.request.session.get('email')            
                print("email",receiver_email)
                verification_obj = OTPVerificationModel.objects.get(email=receiver_email)  
            except ObjectDoesNotExist:
                OTPVerificationModel.objects.create(
                    email=receiver_email,
                )
                verification_obj = OTPVerificationModel.objects.get(email=receiver_email) 

            if request.path == "/otp/":
                verification_obj.counter += 1  # Update counter At every call
            elif request.path == "/otp/payment/": 
                verification_obj.counter_payment += 1

            verification_obj.save() 

            #Send OTP to user's registered email address  
            first_name = (UserModel.objects.get(email=receiver_email)).first_name  
            key = base64.b32encode(generateKey(receiver_email).encode())
            OTP = pyotp.HOTP(key)
            
            if request.path == "/otp/":
                print("OTP at", OTP.at(verification_obj.counter))
                send_email_req = {
                    "subject" : "Paybills Login One-Time-Password",
                    "content" : "Hello {0}, \nPlease use OTP for Paybills account login : {1}.\n\nPaybills Team".format(first_name, OTP.at(verification_obj.counter)),
                    "from_email" : settings.EMAIL_SENDER, 
                    "to_email" : receiver_email,
                    "content_type" : "text/plain",
                    "cc_email" : ""
                }    
            elif request.path == "/otp/payment/": 
                print("OTP at", OTP.at(verification_obj.counter_payment))  
                send_email_req = {
                    "subject" : "Paybills Bill-Payment One-Time-Password",
                    "content" : "Hello {0}, \nPlease use OTP to complete bill payment of amount {1} on Paybills : {2}.\n\nPaybills Team".format(first_name, self.request.session['bill_amount'], OTP.at(verification_obj.counter_payment)),
                    "from_email" : settings.EMAIL_SENDER, 
                    "to_email" : receiver_email,
                    "content_type" : "text/plain",
                    "cc_email" : ""
                }   
                print('Hi there', send_email_req)       
            email_response, email_response_string = send_email(send_email_req)
            print("email_response", email_response_string)

            context = {}
            context['form']= OTPForm()
            context['email'] = self.request.session['email']

            if email_response == False: 
                print("Failed to send email") 
                context['email_send_failed'] = "Failed to send email with OTP. Click on 'Resend OTP'"              
                
            print(context)
            if request.path == "/otp/":
                return render(request, 'common/otp.html', context)
            elif request.path == "/otp/payment/":
                return render(request, 'common/otp_payment.html', context)

        except Exception as e:
            print("errMsg:",str(e))
            context = {}
            context['form']= OTPForm()
            context['email_send_failed'] = "Error Occured"
            if request.path == "/otp/":
                return render(request, 'common/otp.html', context)
            elif request.path == "/otp/payment/":
                return render(request, 'common/otp_payment.html', context)
            
def verify_OTP(receiver_email, received_otp, action):
    """
    API to verify OTP token using user's email address
    """
    try:
        print("action:", action)
        OTP_verification_status = False
        try:           
            verification_obj = OTPVerificationModel.objects.get(email=receiver_email)
        except ObjectDoesNotExist:
            return OTP_verification_status  # False Call

        key = base64.b32encode(generateKey(receiver_email).encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model

        if action == 0:
            #action : 0 for login OTP
            if OTP.verify(int(received_otp), verification_obj.counter):  # Verifying the OTP
                print("OTP verified successfully")
                verification_obj.isVerified = True
                verification_obj.save()
                OTP_verification_status = True
        elif action == 1:
            #action : 1 for payment OTP
            if OTP.verify(int(received_otp), verification_obj.counter_payment):  # Verifying the OTP
                print("OTP verified successfully")
                verification_obj.isVerified_payment = True
                verification_obj.save()
                OTP_verification_status = True

        return OTP_verification_status

    except Exception as e:
        print("errMsg:", str(e))
        return False
        
class OTPVerificationView(FormView):
    """
    View to verify OTP token
    post:
        Receives OTP and verify it using counter stored in database 
    """
    form_class = OTPForm

    def get_template_names(self):       
        if self.request.path == "/otp_verification/":
            template_name = 'common/otp.html'
        elif self.request.path == "/otp_payment_verification/":
            template_name = 'common/otp_payment.html'
        return template_name

    def form_valid(self, form, **kwargs):
        try:
            print("form valid")
            print("verification path",self.request.path)
            received_otp = form.cleaned_data['otp_token']
            print("received_otp", received_otp) 

            #Pass 0 in verify_OTP for login OTP verification and 1 for payment OTP verification  
            if self.request.path == "/otp_verification/":     
                status = verify_OTP(self.request.session.get('email'), received_otp, 0)
            elif self.request.path == "/otp_payment_verification/":
                status = verify_OTP(self.request.session.get('email'), received_otp, 1)

            print("OTP status", status)
            if status == True:
                print("self.request.path", self.request.path)
                if self.request.path == "/otp_verification/":
                    return HttpResponseRedirect(reverse('app:providers')) 
                elif self.request.path == "/otp_payment_verification/":   
                    return HttpResponseRedirect(reverse('app:payment_successful')) 
            else:
                print("OTP does not match")                
                form.add_error('otp_token', 'OTP does not match. Please try again')
                context = self.get_context_data(**kwargs)
                context['form'] = form                
                return render(self.request, self.get_template_names(), context)
                
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            context = self.get_context_data(**kwargs)
            context['form'] = form                
            return render(self.request, self.get_template_names(), context)

class LoginView(FormView):
    """
    View for user login
    get:
        Renders login.html template
    post:
        Autheticate user with email and password 
    """
    form_class = LoginForm
    template_name = 'common/login.html'

    def form_valid(self, form):
        try:
            print("login form valid")
            email = form.cleaned_data['email']
            print(email)
            password = form.cleaned_data['password']
            user = authenticate(self.request, email=email, password=password)
            if user is not None:         
                try:
                    MerchantModel.objects.get(merchant=(UserModel.objects.get(email=user)))
                    form.add_error('email', 'Please use merchant login from homepage')
                    return super(LoginView, self).form_invalid(form)
                except MerchantModel.DoesNotExist:                  
                    login(self.request, user)
                    print("Login successful")
                    self.request.session['email'] = email
                    return HttpResponseRedirect(reverse('app:otp'))          
            else:
                print("Login failed")
                form.add_error('email', 'Entered email or password is incorrect')
                return super(LoginView, self).form_invalid(form) 
        except Exception as e:
        #     print("errMsg:",str(e))
        #     form.add_error(None, "Internal Server Error")
            return super(LoginView, self).form_invalid(form)
                 
class RecordPlayView(View):
    def get(self, request):
        return render(request, 'common/record-play.html')

"""
class SetupVoiceView(View):
    form_class = AudioRecorderForm
    template_name = 'common/setup-voice.html'
    def get(self, request):
        return render(request, self.template_name)   

    def post(self, request):
        if self.request.method == 'POST':
            form = self.form_class(self.request.POST)
            if form.is_valid():
                print("Form is valid")
                form.save()
                return HttpResponseRedirect(reverse('tap_listen'))
            else:
                print("Form is invalid")
                return HttpResponseRedirect(reverse('setup_voice'))
        return HttpResponseRedirect(reverse('setup_voice'))
        
"""
class SetupVoiceView(CreateView):
    """
    View to setup user's voice information
    get:
        Renders setup-voice.html template
    post:
        Stores user's audio blob data in MEDIA_ROOT directory and an entry
        will be inserted in database.
    """
    form_class = AudioRecorderForm
    template_name = 'common/setup-voice.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            for id in range(1,4):
                sample_string = (SampleStringModel.objects.get(id=id)).sample_string
                context['sample_string_'+str(id)] = sample_string
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("Form is valid")
            user_id = self.request.session.get('user_id')
            print(user_id)

            button_id = form.cleaned_data['button_id']
            if button_id == "recordButton_1":
                step_id = 1
            if button_id == "recordButton_2":
                step_id = 2
            if button_id == "recordButton_3":
                step_id = 3
            print(step_id)

            user = UserModel.objects.get(id=user_id)
            sample_string = SampleStringModel.objects.get(id=step_id)
            ar_object = AudioRecorderModel(user=user, sample_string=sample_string, audio_file=form.cleaned_data['audio_file'])
            ar_object.save()
            return HttpResponseRedirect(reverse('app:tap_listen'))

        except Exception as e:
            print("errMsg:",str(e))
            return JsonResponse({"errMsg" : "Internal Server Error"}, status=500)            

    def form_invalid(self, form):
        print("Form is invalid")
        return HttpResponseRedirect(reverse('app:setup_voice'))

def speech_recognition(wave_file_path, language):
    """
    API for speech recognition using Google Web Speech API
    Returns:
        status(true/false) and generated text
        In case of error, error string along with status will be sent
    """
    try:
        #Speech recognition
        sr_obj = sr.Recognizer()

        #Get AudioData object
        with sr.AudioFile(wave_file_path) as source:
            audio = sr_obj.record(source)

        #Used Google Web Speech API for speech to text conversion
        #Limitation of this Web Speech API is that you can make maximum 50 requests per day. 
        #Also, the default access provided by Google can be revoked at any time.
        text = sr_obj.recognize_google(audio,  language = language)

        #Used Google Cloud Speech API for speech to text conversion
        #Google Cloud Speech API is free up to 60 minutes. For more usage, account will be charged as per their pricing model.
        #text = sr_obj.recognize_google_cloud(audio, language = language)
        print("Text : ",text)
        return True, text
        
    except Exception as e:
        print("error",str(e))
        return False , str(e)

class GetOTPFromVoiceView(FormView):
    """
    View to get OTP from voice and verify OTP token
    post:
        Receives OTP via Voice and perform speech recognition on voice data to get OTP
    """
    form_class = AudioRecorderForm
    template_name = 'common/otp.html'

    def form_valid(self, form):
        try:
            print("GetOTPFromVoiceView: Form is valid")

            button_id = form.cleaned_data['button_id']
            print(button_id)
            audio_blob = form.cleaned_data['audio_file']

            speech_recognition_status, OTP_token = speech_recognition(audio_blob,'en-IN')
            print("OTP_token:", OTP_token)

            #Removed whitespace from OTP token if any
            OTP_token = OTP_token.replace(" ", "")
            print(OTP_token)

            #Check if OTP has only numbers
            if OTP_token.isnumeric():
                return JsonResponse({"OTP_token" : OTP_token}, status=201)
            else:
                return JsonResponse({"errMsg" : "OTP can only have numbers. Please try again"}, status=400)            

        except Exception as e:
            print("errMsg:",str(e))
            return JsonResponse({"errMsg" : str(e)}, status=400)

    def form_invalid(self, form):
        print("Form is invalid")        
        if self.request.path == "/otp":
            return HttpResponseRedirect(reverse('app:otp'))     
        elif self.request.path == "/otp/payment/":
            return HttpResponseRedirect(reverse('app:otp_payment'))     
        #return HttpResponseRedirect(reverse('otp'))

class TapListenView(View):
    def get(self, request):
        return render(request, 'common/tap-listen.html')

class VerifyProceedView(View):
    def get(self, request):
        return render(request, 'common/verify-proceed.html')

class ProvidersView(LoginRequiredMixin, View):
    """
    View for providers page
    """
    login_url = '/login/'
    def get(self, request):
        return render(request, 'common/providers.html')

class MobileRechargeView(LoginRequiredMixin, FormView):
    """
    View for mobile recharge payment
    """
    login_url = '/login/'
    form_class = MobileRechargeForm 
    template_name = 'common/mobile-recharge.html'

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            queryset = BillerInfoModel.objects.all()
            if queryset:
                context = {'biller_list': queryset ,'form':MobileRechargeForm}
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("Form valid")
            print(form.cleaned_data['bill_amount'])
            print(form.cleaned_data['phone_number'])
            print(form.cleaned_data['operator'])
            
            self.request.session['phone_number'] = form.cleaned_data['phone_number']
            self.request.session['bill_amount'] = form.cleaned_data['bill_amount']
            self.request.session['operator'] = form.cleaned_data['operator']
            return HttpResponseRedirect(reverse('app:ask_to_play_game'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, 'common/mobile-recharge.html', context)

class BillFoundView(LoginRequiredMixin, FormView):
    """
    View to display bill with details to user
    """
    login_url = '/login/'
    form_class = MobileRechargeForm 
    template_name = 'common/bill-found.html'
    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            context['phone_numer'] = self.request.session['phone_number']
            context['bill_amount'] = self.request.session['bill_amount']
            context['operator'] = self.request.session['operator']
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class DTHRechargeView(View):
    def get(self, request):
        return render(request, 'common/dth-recharge.html')

class MobilePostpaidView(View):
    def get(self, request):
        return render(request, 'common/mobile-postpaid.html')

class LandlineView(View):
    def get(self, request):
        return render(request, 'common/landline.html')

class ElectricityView(View):
    def get(self, request):
        return render(request, 'common/electricity.html')

class WaterView(View):
    def get(self, request):
        return render(request, 'common/water.html')

class PipedgasView(View):
    def get(self, request):
        return render(request, 'common/piped-gas.html')
        
class FASTagView(View):
    def get(self, request):
        return render(request, 'common/fastag.html')

class LoanRepaymentView(View):
    def get(self, request):
        return render(request, 'common/loan-repayment.html')

class BroadbandView(View):
    def get(self, request):
        return render(request, 'common/broadband.html')

class LpgGasView(View):
    def get(self, request):
        return render(request, 'common/lpg-gas.html')

class InsurancePaymentView(View):
    def get(self, request):
        return render(request, 'common/insurance-payment.html')
        
class SubscriptionView(View):
    def get(self, request):
        return render(request, 'common/subscription.html')

class SendVoiceMoneyView(View):
    def get(self, request):
        return render(request, 'common/send-voice-money.html')

class RequestVoiceMoneyView(View):
    def get(self, request):
        return render(request, 'common/request-voice-money.html')

class VoiceAuthenticationView(View):
    def get(self, request):
        return render(request, 'common/voice-authentication.html')

class ScanPayView(View):
    def get(self, request):
        return render(request, 'common/scan-pay.html')

class DashboardView(View):
    def get(self, request):
        return render(request, 'common/dashboard.html')

class SettingView(View):
    def get(self, request):
        return render(request, 'common/setting.html')

class PersonalInformationView(View):
    def get(self, request):
        return render(request, 'common/personal-info.html')

class NotificationEmailsView(View):
    def get(self, request):
        return render(request, 'common/notifications_emails.html')

class PrivacySecurityView(View):
    def get(self, request):
        return render(request, 'common/privacy_security.html')

class AboutView(View):
    def get(self, request):
        return render(request, 'common/about.html')

class HelpFeedbackView(View):
    def get(self, request):
        return render(request, 'common/help-feedback.html')

class EditMobileNumberView(View):
    def get(self, request):
        return render(request, 'common/edit-mobile-number.html')

class EditLanguageView(View):
    def get(self, request):
        return render(request, 'common/edit-language.html')

class DataPersonalizationView(View):
    def get(self, request):
        return render(request, 'common/data_personalization.html')

class BlockedPeopleView(View):
    def get(self, request):
        return render(request, 'common/blocked-people.html')

class HowPeopleView(View):
    def get(self, request):
        return render(request, 'common/how-people.html')

class TermsServicesView(View):
    def get(self, request):
        return render(request, 'common/terms-service.html')

class PrivacyPolicyView(View):
    def get(self, request):
        return render(request, 'common/privacy-policy.html')

class SoftwareLicenseView(View):
    def get(self, request):
        return render(request, 'common/software-licenses.html')

class UserProfileView(View):
    def get(self, request):
        return render(request, 'common/profile.html')

class GetNumberFromVoiceView(FormView):
    """
    View to get selected number for game from voice
    post:
        Receives selected number via Voice and perform speech recognition on voice data to get number
    """
    form_class = AudioRecorderForm
    template_name = 'common/number.html'

    def form_valid(self, form):
        try:
            print("GetNumberFromVoiceView: Form is valid")

            button_id = form.cleaned_data['button_id']
            print(button_id)
            audio_blob = form.cleaned_data['audio_file']

            speech_recognition_status, selected_number = speech_recognition(audio_blob,'en-IN')
            print("selected_number:", selected_number)

            #Removed whitespace from OTP token if any
            selected_number = selected_number.replace(" ", "")
            print(selected_number)

            #Check if selected number has only numerics
            if selected_number.isnumeric():
                return JsonResponse({"selected_number" : selected_number}, status=201)
            else:
                return JsonResponse({"errMsg" : "Selected number should be numeric. Please try again"}, status=400)            

        except Exception as e:
            print("errMsg:",str(e))
            return JsonResponse({"errMsg" : str(e)}, status=400)

    def form_invalid(self, form):
        print("Form is invalid")
        return HttpResponseRedirect(reverse('app:draw_game_number'))     

class DrawNumberGameView(LoginRequiredMixin, FormView):
    """
    View for draw number game
    get:
        Renders number.html template
    post:
        Take user input and check if user has won the game or not 
    """
    login_url = '/login/'
    form_class = DrawNumberForm
    template_name = 'common/number.html'

    def form_valid(self, form):
        try:
            print("DrawNumberGameView : selected_number", form.cleaned_data['selected_number'])
            #Calculate start date and end date of the current week and find magic number 
# -------------------------------------------------------------------------------------------------------------------

            # now = datetime.now()
            # monday = now - timedelta(days = now.weekday())
            # saturday = now - timedelta(days = (now.weekday() -5))
            # start_date = monday.strftime("%Y-%m-%d")
            # end_date = saturday.strftime("%Y-%m-%d")  
            # print(monday)
            # print(saturday)
            # print(start_date)
            # print(end_date)

            # result_dict = number_prediction(start_date, end_date, 1)      
            # print(result_dict)
            # print( (result_dict['Predicted-Magic Numbers'])[now.weekday()] )

            # #If magic number equals to user's selected number, user wins otherwise lose.
            # if ((result_dict['Predicted-Magic Numbers'])[now.weekday()])[0] == form.cleaned_data['selected_number']:
            #     print("Congratulations! You have won the game.")
            #     return HttpResponseRedirect(reverse('get_game_result_success'))                 
            # else:
            #     print("Sorry! You have lost the game.")
            #     return HttpResponseRedirect(reverse('get_game_result_failure'))           
# ------------------------------------------------------------------------------------------------------------------

            luckynum = random.randint(0,10)
            print(luckynum)
            selectednum = form.cleaned_data['selected_number']
            if(luckynum==selectednum):
                print("Congratulations! You have won the game.")
                return HttpResponseRedirect(reverse('app:get_game_result_success'))      
            else:
                print("Sorry! You have lost the game.")
                return HttpResponseRedirect(reverse('app:get_game_result_failure'))           







# ------------------------------------------------------------------------------------------------------------------
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)

class LogoutView(View):
    """
    View for user logout
    """
    def get(self, request):
        try:
            logout(request)
            print("logout successful")
            return redirect('app:index')
        except Exception as e:
            print("errMsg:",str(e))
            print("logout unsuccessful")
            return redirect('app:providers')
        
class GetGameResultSuccessView(LoginRequiredMixin, View):
    """
    View to render template in case of user wins a game
    """
    login_url = '/login/'
    # def get(self, request):
    #     amount = 0
    #     return render(request, 'shop/checkout.html', {'amount': amount} )


    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "shop/game_checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("app:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # add redirect to the selected payment option
                if payment_option == 'S':
                    return redirect('app:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('app:payment', payment_option='paypal')
                elif payment_option == 'G':
                    return redirect('app:ask_to_play_game')
                elif payment_option == 'E':
                    return redirect('app:payment', payment_option='emi')
                elif payment_option == 'C':
                    return redirect('app:ccavenue_payment', payment_option='ccavenue')
                else:
                    messages.warning(
                        self.request, "Invalid payment option select")
                    return redirect('app:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("app:order-summary")



class GetGameResultFailureView(LoginRequiredMixin, View):
    """
    View to render template in case of user loses a game
    """
    login_url = '/login/'
    def get(self, request):
        return render(request, 'common/game-result-failure.html')

class AskToPlayGameView(LoginRequiredMixin, View):
    """
    View to render template to check if user wants to play a game or not
    """
    login_url = '/login/'
    # model = ProductModel
    # template_name = 'common/playgame.html'

    # def get(self, *args, **kwargs):
    #     return render(request, 'common/playgame.html')
    
    def get(self, request):
        return render(request, 'common/playgame.html')

    # def get(self, *args, **kwargs):
    #     try:
    #         slug = slug
    #         order = ProductModel.objects.get(user=self.request.user, ordered=False)
    #         context = {
    #             'object': order
    #         }
    #         return render(self.request, 'order_summary.html', context)
    #     except ObjectDoesNotExist:
    #         messages.error(self.request, "You do not have an active order")
    #         return redirect("/")

class PaymentSuccessfulView(LoginRequiredMixin, View):
    """
    View to render template when bill payment is successful
    """
    login_url = '/login/'
    def get(self, request):
        try:
            bill_obj = MobileRechargeBillModel.objects.create(
                payer_name = " ".join([self.request.user.first_name, self.request.user.last_name]),
                phone_number = self.request.session['phone_number'],
                bill_amount = self.request.session['bill_amount'],
                biller = BillerInfoModel.objects.get(biller_id = self.request.session['operator']),
            )
            self.request.session['bill_id'] = bill_obj.id
            del self.request.session['phone_number']
            del self.request.session['bill_amount']
            return render(request, 'common/payment-successful.html')
        except Exception as e:
            print("errMsg:",str(e))
            return redirect('app:providers')

class RazorpayPaymentSuccessfulView(LoginRequiredMixin, View):
    """
    View to render template when bill payment is successful using razorpay
    """
    login_url = '/login/'
    def get(self, request):
        try:
            return render(request, 'common/razorpay-payment-successful.html')
        except Exception as e:
            print("errMsg:",str(e))
            return redirect('app:providers')

class RazorpayPaymentUnsuccessfulView(LoginRequiredMixin, View):
    """
    View to render template when payment is unsuccessful using razorpay
    """
    login_url = '/login/'
    def get(self, request):
        try:
            return render(request, 'common/razorpay-payment-unsuccessful.html')
        except Exception as e:
            print("errMsg:",str(e))
            return redirect('app:providers')

class InvoiceGeneratorView(LoginRequiredMixin, View):
    """
    View to generate PDF invoice
    """
    login_url = '/login/'
    def get(self, request):
        try:
            # choose english as language
            os.environ["INVOICE_LANG"] = "en"

            print("Bill ID:", self.request.session['bill_id'])
            bill_obj = MobileRechargeBillModel.objects.get(id = self.request.session['bill_id'])

            client = Client(bill_obj.payer_name)
            provider = Provider(bill_obj.biller.biller_name, bank_account='2600420569', bank_code='2010')
            creator = Creator('Rushikesh Patel')

            invoice = Invoice(client, provider, creator)
            invoice.title = "Mobile Recharge Invoice"
            invoice.number = bill_obj.id
            invoice.currency = u'₹'
            invoice.date = bill_obj.transaction_date.date()
            invoice.currency_locale = 'en_US.UTF-8'
            invoice.add_item(Item(
                count = 1, 
                price = bill_obj.bill_amount, 
                description = "Mobile Recharge : phone number "+bill_obj.phone_number,
                tax = 0,
                ))

            pdf = SimpleInvoice(invoice)
            pdf.gen(os.path.join(settings.MEDIA_ROOT, "invoice_dir", "invoice_"+ str(bill_obj.id) +".pdf"), generate_qr_code=True)

            context = {}
            context['bill_id'] = bill_obj.id
            return render(request, 'common/get-invoice.html', context)
        
        except Exception as e:
            print("errMsg:",str(e))
            return render(request, 'common/failed-to-get-invoice.html')

class DisplayInvoiceView(LoginRequiredMixin, View):
    """
    View to display PDF invoice
    """
    login_url = '/login/'
    def get(self, request, bill_id):
        try:
            filename = "invoice_"+ str(bill_id) +".pdf"
            filepath = os.path.join(settings.MEDIA_ROOT, "invoice_dir", filename)
            print(filepath)
            return FileResponse(open(filepath, 'rb'), content_type='application/pdf')

        except Exception as e:
            print("errMsg:",str(e))
            context = {}
            context['bill_id'] = self.request.session['bill_id']
            return render(request, "common/failed-to-display-invoice.html", context)

class SendSearchUser(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = UserModel
    form_class = SearchUserForm
    template_name = 'app/send_search_user_form.html'

    def get_queryset(self):
        try:
            first_name = self.kwargs['search_user']
        except:
            first_name = ''

        if first_name != '':
            object_list = self.model.objects.filter(first_name=first_name)
        else:
            object_list = self.model.objects.all()        
        return object_list

    def get_context_data(self, **kwargs):
        context = super(SendSearchUser, self).get_context_data(**kwargs)
        query = self.request.GET.get("search_user")
        context['user'] = self.request.user

        if query:
            queryset = (Q(first_name=query))
            search_user = UserModel.objects.filter(queryset).distinct()
            if not search_user:
                messages.error(self.request, 'No user found.')
        else:
            search_user = []

        context['search_user'] = search_user
        context['nbar'] = 'send'        
        return context

class RequestSearchUserView(LoginRequiredMixin, ListView):
    """
    View to search user for request money
    """
    login_url = '/login/'
    model = UserModel
    form_class = SearchUserForm
    template_name = 'common/request_search_user_form.html'

    def get_context_data(self, **kwargs):
        try:
            context = super(RequestSearchUserView, self).get_context_data(**kwargs)
            query = self.request.GET.get("search_user")
            context['user'] = self.request.user

            if query:            
                queryset = (Q(email=query))
                search_user = UserModel.objects.filter(queryset).distinct()
                if not search_user:
                    #messages.error(self.request, 'Entered email not found.')
                    context['external_user_email'] = query
                    self.request.session['external_user_email'] = query
            else:
                search_user = []

            context['search_user'] = search_user
            print("context", context)
            return context

        except Exception as e:
            print("error:", str(e))
            return dict()

class RequestMoneyView(LoginRequiredMixin, FormView):
    """
    View for Request Money
    """
    login_url = '/login/'
    form_class = RequestMoneyForm
    template_name = 'common/request-money.html'
    
    def get_context_data(self, **kwargs):
        try:
            context = super(RequestMoneyView, self).get_context_data(**kwargs)
            user_id = self.kwargs.get('user_id')
            print("user_id", user_id)
            if user_id == 0:
                context['receiver_id'] = 0
                context['receiver_email'] = self.request.session['external_user_email']
                context['receiver_first_name'] = str()
            else:
                context['receiver_id'] = user_id
                context['receiver_email'] = UserModel.objects.get(id=user_id).email
                context['receiver_first_name'] = UserModel.objects.get(id=user_id).first_name

            print("context", context)
            return context
        except Exception as e:
            print("errMsg:",str(e))
            return dict()

    def form_valid(self, form):
        print("amount", form.cleaned_data['amount'])
        print(form.clean_description())
        context = self.get_context_data()

        short_link = utils.shorten_url(settings.SIGNUP_URL)
        print("short_link", short_link)

        send_email_req = {
            "subject" : "Paybills Money Request",
            "content" : "Hello {0}, <br><br>This is money request from {1} on Paybills.<br><br>Amount:{2}<br>Description:{3}<br><br><a href='{4}'> Join paybills now and win great cashback if you haven't yet! </a><br><br>Paybills Team".format(context['receiver_first_name'], self.request.user, str(form.cleaned_data['amount']), form.cleaned_data['description'], short_link),
            "from_email" : settings.EMAIL_SENDER, 
            "to_email" : context['receiver_email'],
            "content_type" : "text/html",
            "cc_email" : self.request.user.email 
        }          
        email_response, email_response_string = send_email(send_email_req)
        print("Email", email_response)

        return HttpResponseRedirect(reverse('app:request_successful'))

class RequestSuccessView(LoginRequiredMixin, View):
    """
    View to render template when request money is successful
    """
    login_url = '/login/'
    def get(self, request):
        return render(request, 'common/request-successful.html')

class RedirectView(View):
    """
    View to redirect to actual url from shortlink
    """
    def get(self, request, short):
        url = get_object_or_404(UrlShortnerModel, short_id=short)
        print(url.long_url)
        return redirect(url.long_url)

class SendMoneyView(LoginRequiredMixin, FormView):
    """
    View for Send Money
    """
    login_url = '/login/'
    form_class = RequestMoneyForm
    template_name = 'common/send-money.html'

    def form_valid(self, form):
        try:
            amount = form.cleaned_data['amount']
            description = form.cleaned_data['description']
            currency = 'INR'
            razorpay_client = utils.create_razorpay_client()

            #Amount from session will be used in payment handler
            self.request.session['amount'] = amount
            # Create a Razorpay Order
            # Razorpay takes amount in paisa unit. That's why we need to multiply it by 100
            razorpay_order = razorpay_client.order.create(dict(amount=float(amount)*100,
                                                            currency=currency,
                                                            payment_capture='0',
                                                            ))
        
            # order id and status of newly created order.
            razorpay_order_id = razorpay_order['id']
            callback_url = 'razorpay_payment_handler/'
            order_status =  razorpay_order['status']
            if order_status == 'created':
                print("Order created successfully")
                transaction = RazorpayTransactionModel(
                    amount = float(amount),
                    description = description,
                    order_id = razorpay_order_id,
                    payer = self.request.user,
                )
                transaction.save()
        
            # we need to pass these details to frontend.
            context = {}
            context['razorpay_order_id'] = razorpay_order_id
            context['razorpay_merchant_key'] = settings.RAZORPAY_KEY_ID
            context['razorpay_amount'] = amount
            context['currency'] = currency
            context['callback_url'] = callback_url
            context['description'] = description
            print("amount", amount)
            print(context)
        
            return render(self.request, 'common/razorpay_payment.html', context=context)

        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)

class RazorpayPaymentHandlerView(View): 
    """
    View to receive payment details from razorpay
    Details will be stored to database after signature verification
    """
    def post(self, request):
        print("received", request.POST)
        try:           
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            print("params_dict", params_dict)
            # verify the payment signature.
            razorpay_client = utils.create_razorpay_client()

            status = razorpay_client.utility.verify_payment_signature(
                params_dict)
            print("verify_payment_signature", status)
            transaction = RazorpayTransactionModel.objects.get(order_id=razorpay_order_id)
            transaction.payment_id = payment_id
            transaction.is_completed = True
            transaction.save()

            if status is None:
                #amount = 20000  # Rs. 200
                amount = request.session['amount']

                # capture the payemt
                print(razorpay_client.payment.capture(payment_id, float(amount)*100))
                print("captured")
                # render success page on successful caputre of payment
                return HttpResponseRedirect(reverse('app:razorpay_payment_successful'))
            else: 
                # if signature verification fails.
                print("Signature varification failed")
                return HttpResponseRedirect(reverse('app:razorpay_payment_unsuccessful'))

        except Exception as e:
            print("errMsg:", str(e))
            return HttpResponseRedirect(reverse('app:razorpay_payment_unsuccessful'))

class PayWithRazorpayView(View):
    def get(self, request):
        pass

from string import Template
class PayWithCCAvenueView(FormView):
    template_name = 'common/ccavenue_checkout_form.html'
    form_class = CCAvenueCheckoutForm

    def get_context_data(self, **kwargs):
        print("Getting context data")
        try:
            context = super().get_context_data(**kwargs)
            context['merchant_id'] = settings.CCAVENUE_MERCHANT_ID
            context['order_id'] = 1
            context['redirect_url'] = "http://127.0.0.1:8000/ccavenue_response/"
            context['cancel_url'] = "http://127.0.0.1:8000/ccavenue_response/"
            
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("Form valid")
            p_merchant_id = settings.CCAVENUE_MERCHANT_ID
            p_order_id = 1
            p_redirect_url = "http://127.0.0.1:8000/ccavenue_response/"
            p_cancel_url = "http://127.0.0.1:8000/ccavenue_response/"

            #p_merchant_id = form.cleaned_data['merchant_id']
            #p_order_id = form.cleaned_data['order_id']
            # p_currency = form.cleaned_data['currency']
            p_currency = 'INR'
            p_amount = form.cleaned_data['amount']
            #p_redirect_url = form.cleaned_data['redirect_url']
            #p_cancel_url = form.cleaned_data['cancel_url']
            #p_language = form.cleaned_data['language']
            p_language = 'EN'
            p_billing_name = form.cleaned_data['billing_name']
            p_billing_address = form.cleaned_data['billing_address']
            p_billing_city = form.cleaned_data['billing_city']
            p_billing_state = form.cleaned_data['billing_state']
            p_billing_zip = form.cleaned_data['billing_zip']
            p_billing_country = form.cleaned_data['billing_country']
            p_billing_tel = form.cleaned_data['billing_tel']
            p_billing_email = form.cleaned_data['billing_email']
            p_delivery_name = form.cleaned_data['delivery_name']
            p_delivery_address = form.cleaned_data['delivery_address']
            p_delivery_city = form.cleaned_data['delivery_city']
            p_delivery_state = form.cleaned_data['delivery_state']
            p_delivery_zip = form.cleaned_data['delivery_zip']
            p_delivery_country = form.cleaned_data['delivery_country']
            p_delivery_tel = form.cleaned_data['delivery_tel']
            p_merchant_param1 = form.cleaned_data['merchant_param1']
            p_merchant_param2 = form.cleaned_data['merchant_param2']
            p_merchant_param3 = form.cleaned_data['merchant_param3']
            p_merchant_param4 = form.cleaned_data['merchant_param4']
            p_merchant_param5 = form.cleaned_data['merchant_param5']
            p_promo_code = form.cleaned_data['promo_code']
            p_customer_identifier = form.cleaned_data['customer_identifier']           
            
            merchant_data = 'merchant_id='+str(p_merchant_id)+ '&'+'order_id='+str(p_order_id) + '&' + "currency=" + p_currency + '&' + 'amount=' + str(p_amount)+'&'+'redirect_url='+p_redirect_url+'&'+'cancel_url='+p_cancel_url+'&'+'language='+p_language+'&'+'billing_name='+p_billing_name+'&'+'billing_address='+p_billing_address+'&'+'billing_city='+p_billing_city+'&'+'billing_state='+p_billing_state+'&'+'billing_zip='+p_billing_zip+'&'+'billing_country='+p_billing_country+'&'+'billing_tel='+p_billing_tel+'&'+'billing_email='+p_billing_email+'&'+'delivery_name='+p_delivery_name+'&'+'delivery_address='+p_delivery_address+'&'+'delivery_city='+p_delivery_city+'&'+'delivery_state='+p_delivery_state+'&'+'delivery_zip='+p_delivery_zip+'&'+'delivery_country='+p_delivery_country+'&'+'delivery_tel='+p_delivery_tel+'&'+'merchant_param1='+p_merchant_param1+'&'+'merchant_param2='+p_merchant_param2+'&'+'merchant_param3='+p_merchant_param3+'&'+'merchant_param4='+p_merchant_param4+'&'+'merchant_param5='+p_merchant_param5+'&'+'promo_code='+p_promo_code+'&'+'customer_identifier='+p_customer_identifier+'&'
            print("merchant_data", merchant_data)
            
            workingKey = b"FC98690B8615B5A1D1C461E4091B9A3D"
            encryption = ccavutil.encrypt(merchant_data,workingKey)
            print("encryption", encryption)

            accessCode = "AVQW44CY59KI48PVMS"            
            context = {}
            context['encReq'] = encryption
            context['xscode'] = accessCode
            return render(self.request, 'common/ccavenue_merchant_checkout.html', context)
            
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, 'common/ccavenue_checkout_form.html', context)

class CCAvenueResponseView(View):
    '''
	Please put in the 32 bit alphanumeric key in quotes provided by CCAvenues.
	'''	 
    def post(self, request):
        print("received", request.POST)
        try:
            print("encResp:", request.POST.get[encResp])
            workingKey = b"FC98690B8615B5A1D1C461E4091B9A3D"
            decResp = ccavutil.decrypt(encResp,workingKey)
            data = '<table border=1 cellspacing=2 cellpadding=2><tr><td>'	
            data = data + decResp.replace('=','</td><td>')
            data = data.replace('&','</td></tr><tr><td>')
            data = data + '</td></tr></table>'
            
            html = '''\
            <html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
                    <title>Response Handler</title>
                </head>
                <body>
                    <center>
                        <font size="4" color="blue"><b>Response Page</b></font>
                        <br>
                        $response
                    </center>
                    <br>
                </body>
            </html>
            '''
            print("html", html)
            fin = Template(html).safe_substitute(response=data)
            print("data", data)
            print("fin", fin)
            return fin
        except Exception as e:
            print("errMsg:", str(e))
            return HttpResponseRedirect(reverse('app:razorpay_payment_unsuccessful'))

class CreateMerchantAccountView(CreateView):
    """
    View for create merchant account request
    get:
        Renders create-merchant-account.html template
    post:
        This will validate user information and stores it in database
    """
    form_class = CreateAccountForm
    template_name = 'common/create-merchant-account.html'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        try:
            print("Form valid")   
            user = form.save()        
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            self.request.session['email'] = user.email
            self.request.session['user_id'] = user.id            
            return HttpResponseRedirect(reverse('app:merchant_registration'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super().form_invalid(form)
   
class MerchantRegistrationView(SessionWizardView):
    """
    View for merchat account registration
    get:
        Renders merchant-registration.html template
    post:
        This will validate merchant information and stores it in database
    """
    form_list = [CreateAccountForm, MerchantRegistrationForm, MerchantDetailsForm]
    template_name = 'common/merchant-registration.html'

    def get_context_data(self, **kwargs):
        try:
            print("get context")
            context = super().get_context_data(**kwargs)       
            context['country_queryset'] = cities.models.Country.objects.all()
            context['city_queryset'] = cities.models.City.objects.none()
            context['state_queryset'] = cities.models.Region.objects.none()
            context['timezones'] = pytz.common_timezones
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def done(self, form_list, **kwargs):       
        for form in form_list:
            if form_list.index(form) == 0:
                # CreateAccountForm : Store UserModel                
                user = form.save()        
                password = form.cleaned_data['password']
                user.set_password(password)
                user.save()
                self.request.session['email'] = user.email
                self.request.session['user_id'] = user.id 
            elif form_list.index(form) == 1:
                # MerchantRegistrationForm : Store MerchantModel
                merchant_obj = MerchantModel(
                business_name = form.cleaned_data['business_name'],
                subdomain_name = form.cleaned_data['subdomain_name'],
                merchant_category = form.cleaned_data['merchant_category'],
                merchant_country = cities.models.Country.objects.get(id=int(form.cleaned_data['country'])),
                merchant_state = cities.models.Region.objects.get(id=int(form.cleaned_data['state'])),
                merchant_city = cities.models.City.objects.get(id=int(form.cleaned_data['city'])),
                )    

                merchant_obj.merchant = UserModel.objects.get(email = self.request.session['email'])
                merchant_obj.merchant.phone_number = form.cleaned_data['phone_number']
                merchant_obj.merchant.upi_id = form.cleaned_data['upi_id']
                merchant_obj.merchant.save()
                merchant_obj.save() 

            elif form_list.index(form) == 2:
                # MerchantDetailsForm : Store merchant details
                merchant_obj = MerchantModel.objects.get(merchant=UserModel.objects.get(email = self.request.session['email']))
                merchant_obj.tax_1_name = form.cleaned_data['tax_1_name']
                merchant_obj.tax_1_no = form.cleaned_data['tax_1_no']
                merchant_obj.tax_2_name = form.cleaned_data['tax_2_name']
                merchant_obj.tax_2_no = form.cleaned_data['tax_2_no']
                merchant_obj.finanicial_year_start_month = form.cleaned_data['finanicial_year_start_month']
                merchant_obj.save() 
    
        return HttpResponseRedirect(reverse('app:merchant_login'))

def load_states(request):
    """
    View to get states depending upon selected country
    """
    country_id = request.GET.get('country_id')
    print("country_id", country_id)
    state_queryset = cities.models.Region.objects.filter(country_id=country_id).all()
    return JsonResponse(list(state_queryset.values('id','name')), safe=False)            

def load_cities(request):
    """
    View to get cities depending upon selected country
    """
    country_id = request.GET.get('state_id')
    print("state_id", country_id)
    city_queryset = cities.models.City.objects.filter(country_id=country_id).all()
    return JsonResponse(list(city_queryset.values('id','name')), safe=False)            

class MerchantLoginView(FormView):
    """
    View for user login
    get:
        Renders login.html template
    post:
        Autheticate user with email and password 
    """
    form_class = LoginForm
    template_name = 'common/merchant-login.html'

    def form_valid(self, form):
        try:
            print("login form valid")
            email = form.cleaned_data['email']
            print(email)
            password = form.cleaned_data['password']
            user = authenticate(self.request, email=email, password=password)
            if user is not None:
                try:
                    m = MerchantModel.objects.get(merchant=(UserModel.objects.get(email=user)))
                except MerchantModel.DoesNotExist:
                    print("Login failed")
                    form.add_error('email', 'Merchant with this email is not registered')
                    return super(MerchantLoginView, self).form_invalid(form)

                login(self.request, user)
                print("Login successful")
                self.request.session['email'] = email
                self.request.session['first_name'] = m.merchant.first_name
                redirect_path = "{0}://{1}.{2}".format(settings.HTTP_PROTOCOL, m.subdomain_name, settings.DEFAULT_SITE_DOMAIN)
                print(redirect_path)
                return redirect(redirect_path)         
            else:
                print("Login failed")
                form.add_error('email', 'Entered email or password is incorrect')
                return super(MerchantLoginView, self).form_invalid(form) 
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(MerchantLoginView, self).form_invalid(form)

class MerchantDashboardView(LoginRequiredMixin, View):
    login_url = '/merchant_login/'
    def get(self, request):
        context = {}
        context['merchant_email'] = self.request.session['email']
        context['merchant_first_name'] = self.request.session['first_name']
        print(context)
        return render(request, 'ecommerce/merchant-dashboard.html', context)

class ListProductsView(LoginRequiredMixin, TemplateView):
    """
    View to list products
    """
    login_url = '/merchant_login/'
    template_name = 'ecommerce/list-products.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddProductView(LoginRequiredMixin, FormView):
    """
    View to add products
    """
    login_url = '/merchant_login/'
    form_class = ProductForm
    template_name = 'ecommerce/add-product.html'

    def get_context_data(self, **kwargs):
        print("get_context_data")
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['brand_queryset'] = BrandModel.objects.all()
            context['tax_queryset'] = TaxRatesModel.objects.all()
            context['category_queryset'] = CategoryModel.objects.all()
            context['subcategory_queryset'] = SubcategoryModel.objects.all()
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("AddProductView form valid")
            print("form", form)            
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            print("merchant", merchant)
            product = form.save(commit=False)
            print("commit false done")
            product.merchant = merchant
            product.merchant.merchant_id = merchant.merchant_id
            product.save()           
            print("Product added")
            return HttpResponseRedirect(reverse('app:products'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddProductView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid", form)
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class UpdateProductView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = ProductForm
    template_name = 'ecommerce/update-product.html'
    model = ProductModel
    success_url = reverse_lazy('products')

    def get_context_data(self, **kwargs):
        print("get_context_data")
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            #context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['brand_queryset'] = BrandModel.objects.all()
            context['tax_queryset'] = TaxRatesModel.objects.all()
            context['category_queryset'] = CategoryModel.objects.all()
            context['subcategory_queryset'] = SubcategoryModel.objects.all()
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class DeleteProductView(DeleteView):
    model = ProductModel 
    template_name = 'ecommerce/remove-product.html'    
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('products')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteProductView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-product.html')

class ListProductVariationView(LoginRequiredMixin, TemplateView):
    """
    View to list products
    """
    login_url = '/merchant_login/'
    template_name = 'ecommerce/list-product-variation.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))           
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))
            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant=merchant)
            context['product_variation_queryset'] = ProductVariationsModel.objects.filter(product_id__in=[item.id for item in context['product_queryset']])
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddProductVariationView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = ProductVariationForm
    template_name = 'ecommerce/add-product-variation.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))           
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))
            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant=merchant)
            context['product_variation_queryset'] = ProductVariationsModel.objects.filter(product_id__in=[item.id for item in context['product_queryset']])
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("ProductVariationsView form valid")
            print("form", form)            
            form.save()
            print("Product variation added")
            return HttpResponseRedirect(reverse('app:list_product_variation'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(ProductVariationsView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class UpdateProductVariationsView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    template_name = 'ecommerce/update-product-variation.html'
    model = ProductVariationsModel
    fields = ('name', 'value', )
    success_url = reverse_lazy('list_product_variation')

class DeleteProductVariationView(DeleteView):
    model = ProductVariationsModel  
    template_name = 'ecommerce/remove-product-variation.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('list_product_variation')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteProductVariationView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-product-variation.html')

class ListPurchaseView(LoginRequiredMixin, TemplateView):
    login_url = '/merchant_login/'
    template_name = 'ecommerce/list-purchase.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['purchase_queryset'] = PurchaseModel.objects.filter(merchant = merchant)
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddPurchaseView(LoginRequiredMixin, MultiFormView):
    login_url = '/merchant_login/'
    form_classes = {
        'purchase_form' : PurchaseForm,
        'payment_form' : PaymentForm,
    }
    template_name = 'ecommerce/add-purchase.html'   

    def get_success_url(self):
        return reverse('app:merchant_dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['supplier_queryset'] = SupplierModel.objects.all()
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['user_queryset'] = UserModel.objects.all()           
            
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()   

    def forms_valid(self, forms):
        payment = forms['payment_form']
        purchase = forms['purchase_form']  
        payment_object = forms['payment_form'].save()
        print("Added payment successfully")   

        purchase_obj = forms['purchase_form'].save(commit=False)
        subdomain_name = utils.get_subdomain(self.request)
        merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
        purchase_obj.merchant = merchant
        purchase_obj.payment_id = payment_object
        purchase_obj.save()  
        print("Added purchase successfully")   
        return super(AddPurchaseView, self).forms_valid(forms)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeletePurchaseView(DeleteView):
    model = PurchaseModel    
    template_name = 'ecommerce/remove-purchase.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('app:merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeletePurchaseView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-purchase.html') 

class AddSaleView(LoginRequiredMixin, MultiFormView):
    login_url = '/merchant_login/'
    form_classes = {
        'sale_form' : SaleForm,
        'payment_form' : PaymentForm,
    }
    template_name = 'ecommerce/add-sales.html'   

    def get_success_url(self):
        return reverse('app:merchant_dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['supplier_queryset'] = SupplierModel.objects.all()
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['user_queryset'] = UserModel.objects.all()           
            
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()   

    def forms_valid(self, forms):
        payment = forms['payment_form']
        purchase = forms['sale_form']  

        payment_object = forms['payment_form'].save()
        print("Added payment successfully")   

        sale_obj = forms['sale_form'].save(commit=False)
        subdomain_name = utils.get_subdomain(self.request)
        merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
        sale_obj.merchant = merchant
        sale_obj.payment_id = payment_object
        sale_obj.save()  
        print("Added sale successfully")   
        return super(AddSaleView, self).forms_valid(forms)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteSaleView(DeleteView):
    model = SaleModel  
    template_name = 'ecommerce/remove-sale.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteSaleView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-sale.html')

class AddSellReturnView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = SellReturnForm
    template_name = 'ecommerce/add-sell-return.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['user_queryset'] = UserModel.objects.all()
            context['location_queryset'] = LocationModel.objects.all()
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("sell return form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            sell_return = form.save(commit=False)
            sell_return.merchant = merchant
            sell_return.save()
            print("Sell return added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddSellReturnView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteSellReturnView(DeleteView):
    model = SellReturnModel 
    template_name = 'ecommerce/remove-sell-return.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteSellReturnView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-sell-return.html')

class AddStockTransferView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = StockTransferForm
    template_name = 'ecommerce/add-stock-transfer.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['location_queryset'] = LocationModel.objects.all()
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("stock transfer form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            stock_transfer = form.save(commit=False)
            stock_transfer.merchant = merchant
            stock_transfer.save()
            print("Stock transfer added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddStockTransferView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteStockTransferView(DeleteView):
    model = StockTransferModel  
    template_name = 'ecommerce/remove-stock-transfer.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('app:merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteStockTransferView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-stock-transfer.html')

class AddStockAdjustmentsView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = StockAdjustmentsForm
    template_name = 'ecommerce/add-stock-adjustment.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['location_queryset'] = LocationModel.objects.all()
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("stock transfer form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            stock_adjustment = form.save(commit=False)
            stock_adjustment.merchant = merchant
            stock_adjustment.save()
            print("Stock adjustment added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddStockAdjustmentsView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteStockAdjustmentView(DeleteView):
    model = StockAdjustmentsModel  
    template_name = 'ecommerce/remove-stock-adjustment.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteStockAdjustmentView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-stock-adjustment.html')

class AddExpenseView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = ExpenseForm
    template_name = 'ecommerce/add-expense.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['location_queryset'] = LocationModel.objects.all()
            context['expense_category_queryset'] = ExpenseCategoriesModel.objects.all()
            context['user_queryset'] = UserModel.objects.all()
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("stock transfer form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            expense = form.save(commit=False)
            expense.merchant = merchant
            expense.save()
            print("Expense added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddExpenseView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteExpenseView(DeleteView):
    model = ExpenseModel  
    template_name = 'ecommerce/remove-expense.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteExpenseView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-expense.html')

class UpdateExpenseView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = ExpenseForm
    template_name = 'ecommerce/update-expense.html'
    model = ExpenseModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['location_queryset'] = LocationModel.objects.all()
            context['expense_category_queryset'] = ExpenseCategoriesModel.objects.all()
            context['user_queryset'] = UserModel.objects.all()
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddExpenseCategoryView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = ExpenseCategoryForm
    template_name = 'ecommerce/add-expense-category.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['location_queryset'] = LocationModel.objects.all()
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("stock transfer form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            expense_category = form.save(commit=False)
            expense_category.merchant = merchant
            expense_category.save()
            print("Expense category added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddExpenseCategoryView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteExpenseCategoryView(DeleteView):
    model = ExpenseCategoriesModel
    template_name = 'ecommerce/remove-expense-category.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteExpenseCategoryView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-expense-category.html')

class UpdateExpenseCategoryView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = ExpenseCategoryForm
    template_name = 'ecommerce/update-expense-category.html'
    model = ExpenseCategoriesModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['product_queryset'] = ProductModel.objects.filter(merchant = merchant)
            context['location_queryset'] = LocationModel.objects.all()
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddTaxRatesView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = TaxRatesForm
    template_name = 'ecommerce/add-tax-rates.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("tax rates form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            tax_rate = form.save(commit=False)
            tax_rate.merchant = merchant
            tax_rate.save()
            print("Tax rate added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddTaxRatesView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteTaxRatesView(DeleteView):
    model = TaxRatesModel
    template_name = 'ecommerce/remove-tax-rates.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteTaxRatesView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-tax-rates.html')

class UpdateTaxRatesView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = TaxRatesForm
    template_name = 'ecommerce/update-tax-rates.html'
    model = TaxRatesModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddBrandsView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = BrandsForm
    template_name = 'ecommerce/add-brands.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("Brand form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            brand = form.save(commit=False)
            brand.merchant = merchant
            brand.save()
            print("Brand added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddBrandsView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteBrandsView(DeleteView):
    model = BrandModel
    template_name = 'ecommerce/remove-brands.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteBrandsView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-brands.html')

class UpdateBrandsView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = BrandsForm
    template_name = 'ecommerce/update-brands.html'
    model = BrandModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddUnitsView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = UnitsForm
    template_name = 'ecommerce/add-units.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("Brand form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            unit = form.save(commit=False)
            unit.merchant = merchant
            unit.save()
            print("Unit added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddUnitsView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteUnitsView(DeleteView):
    model = UnitsModel
    template_name = 'ecommerce/remove-units.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteUnitsView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-units.html')

class UpdateUnitsView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = UnitsForm
    template_name = 'ecommerce/update-units.html'
    model = UnitsModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

class AddTaxGroupView(LoginRequiredMixin, FormView):
    login_url = '/merchant_login/'
    form_class = TaxGroupForm
    template_name = 'ecommerce/add-tax-group.html'

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            context['tax_rates_queryset'] = TaxRatesModel.objects.filter(merchant=merchant)
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()

    def form_valid(self, form):
        try:
            print("tax rates form valid")
            subdomain_name = utils.get_subdomain(self.request)
            merchant = MerchantModel.objects.get(subdomain_name = subdomain_name)
            print("subtaxes form:", form.cleaned_data['sub_taxes'])
            tax_group = form.save(commit=False)
            tax_group.merchant = merchant           
            tax_group.save()
            for obj in form.cleaned_data['sub_taxes']:
                tax_group.sub_taxes.add(obj)
                # Don't need to save model afterwards as add has immediate effect on DB
            print("Tax group added")
            return HttpResponseRedirect(reverse('app:merchant_dashboard'))
        except Exception as e:
            print("errMsg:",str(e))
            form.add_error(None, "Internal Server Error")
            return super(AddTaxGroupView, self).form_invalid(form)

    def form_invalid(self, form, **kwargs):
        print("form invalid")
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return render(self.request, self.template_name, context)

class DeleteTaxGroupView(DeleteView):
    model = TaxGroupModel
    template_name = 'ecommerce/remove-tax-group.html'   
    # url to redirect after successfully deleting object
    success_url = reverse_lazy('merchant_dashboard')

    def delete(self, request, *args, **kwargs):
        try:
            return super(DeleteTaxGroupView, self).delete(
                request, *args, **kwargs
            )
        except models.ProtectedError as e:           
            return render(request, 'ecommerce/failed-remove-tax-group.html')

class UpdateTaxGroupView(LoginRequiredMixin, UpdateView):
    login_url = '/merchant_login/'
    form_class = TaxGroupForm
    template_name = 'ecommerce/update-tax-group.html'
    model = TaxGroupModel
    success_url = reverse_lazy('merchant-dashboard')

    def get_context_data(self, **kwargs):
        try:
            print("merchant subdomain", utils.get_subdomain(self.request))
            merchant = MerchantModel.objects.get(subdomain_name = utils.get_subdomain(self.request))

            context = super().get_context_data(**kwargs)
            context['merchant_email'] = self.request.session['email']
            context['merchant_first_name'] = self.request.session['first_name']  
            
            print("context", context)
            return context
        except Exception as e:
            print("error:", str(e))
            return dict()


########################################################################################################################



class AboutUsView(View):
    def get(self, request):
        return render(request, 'common/aboutus.html')
        # return HttpResponse('HELLO about us')



class ShopView(View):
    login_url = '/login/'

    def get(self, *args, **kwargs):
        # xyz = ProductModel.objects.filter(pk=1)
        # xyz = get_object_or_404(ProductModel)
        # # xyz = ProductModel.objects.filter(id=merchant)
        # print (xyz)
        img = ProductModel.objects.all()

        return render(self.request, 'shop/index.html', {'img':img})
        # return HttpResponse('This is Shop Page')

class retrieveData(LoginRequiredMixin, ListView):
    login_url = '/login/'
    model = ProductModel
    paginate_by = 9
    template_name = "shop/product.html"


# class retrieveOneData(View):
#     # def oneData(request, slug1):
#     #     print (slug1)
#     #     abc = ProductModel.objects.filter(slug = '01')

#     # def getOne(request, slug):
#     #     xyz = ProductModel.objects.filter(slug=01)
#     #     return render(request, 'shop/one.html' )


#     def get(self, *args, **kwargs):
#         abc = ProductModel.objects.get(slug=self.kwargs['slug'])
#         print(abc)
#         return render(self.request, 'shop/one.html', {'abc': abc, 'media_url':settings.MEDIA_URL})

class retrieveOneData(LoginRequiredMixin, DetailView):
    login_url = '/login/'
    model = ProductModel
    # template_name = 'shop/one.html'
    template_name = 'shop/product4.html'


def search(request):
    login_url = '/login/'

    query = request.GET['query']
    sproducts = ProductModel.objects.filter(product_name__icontains=query)
    print(sproducts)
    return render(request,'shop/search.html', {'sproducts': sproducts})

def bycategorybooks(request):
    login_url = '/login/'

    sproducts = ProductModel.objects.filter(product_category = '1')
    print(sproducts)
    return render(request,'shop/category.html', {'sproducts': sproducts})

def bycategoryelectronics(request):
    login_url = '/login/'

    sproducts = ProductModel.objects.filter(product_category = '5')
    print(sproducts)
    return render(request,'shop/category.html', {'sproducts': sproducts})


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            print(context)
            return render(self.request, 'shop/ordersummery.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")

def add_to_cart(request, slug):
    product = get_object_or_404(ProductModel, slug=slug)
    print(request.user)
    
    order_item, created = ProductModel.objects.get_or_create(
        product_name=product,
        User=request.user,
    )
    print('HIIIIIIIIIIIII')
    order_qs = Order.objects.filter(user=request.user)
    if order_qs.exists():
        order = order_qs[0]
        if order.products.filter(item__slug=product.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "Item qty was updated.")
            return redirect("app:order-summary")
        else:
            order.products.add(order_item)
            messages.info(request, "Item was added to your cart.")
            return redirect("app:order-summary")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "Item was added to your cart.")
    return redirect("app:order-summary")


def remove_from_cart(request, slug):
    product = get_object_or_404(ProductModel, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    print('hello 12345')
    if order_qs.exists():
        order = order_qs[0]
        print('hello 123')
        # check if the order item is in the order
        if order.products.filter(item__slug=product.slug).exists():
            order_item = Orderproduct.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.products.remove(order_item)
            messages.info(request, "Item was removed from your cart.")
            return redirect("app:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("app:shopdetail", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("app:shopdetail", slug=slug)
    # return redirect("app:product", slug=slug)


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(ProductModel, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False)
    print(item)
    print(request.user)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__slug=item.slug).exists():
            order_item = ProductModel.objects.filter(
                product_name=item,
                user=request.user,
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.product.remove(order_item)
            messages.info(request, "This item qty was updated.")
            return redirect("app:order-summary")
        else:
            # add a message saying the user dosent have an order
            messages.info(request, "Item was not in your cart.")
            return redirect("app:product", slug=slug)
    else:
        # add a message saying the user dosent have an order
        messages.info(request, "u don't have an active order.")
        return redirect("app:product", slug=slug)
    # return redirect("app:product", slug=slug)



# class CheckoutView(View):
#     def get(self, request):
#         return render(request, 'shop/checkout.html')
    

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform': CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "shop/checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("app:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # add functionality for these fields
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                    address_type='B'
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                # add redirect to the selected payment option
                if payment_option == 'S':
                    return redirect('app:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('app:payment', payment_option='paypal')
                elif payment_option == 'G':
                    return redirect('app:ask_to_play_game')
                elif payment_option == 'E':
                    return redirect('app:payment', payment_option='emi')
                elif payment_option == 'C':
                    return redirect('app:ccavenue_payment', payment_option='ccavenue')
                else:
                    messages.warning(
                        self.request, "Invalid payment option select")
                    return redirect('app:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("app:order-summary")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("app:checkout")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(
                    user=self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("app:checkout")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an active order")
                return redirect("app:checkout")


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received")
                return redirect("app:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("app:request-refund")


class PaymentView(View):
    def get(self, *args, **kwargs):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "shop/payment.html", context)
        else:
            messages.warning(
                self.request, "u have not added a billing address")
            return redirect("app:checkout")

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="inr",
                source=token
            )
            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order
            order.ordered = True
            order.payment = payment
            # TODO : assign ref code
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Order was successful")
            return redirect("/")

        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "RateLimitError")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not Authentication")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(self.request, "Serious Error occured")
            return redirect("/")

