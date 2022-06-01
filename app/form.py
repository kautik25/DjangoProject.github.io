from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.forms import TextInput
from datetime import date
from django.urls import reverse_lazy
import cities
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from .models import (
    UserModel,
    AudioRecorderModel,
    BillerInfoModel,
    MerchantModel,
    ProductModel,
    PurchaseModel,
    PaymentModel,
    ProductVariationsModel,
    TransactionModel,
    SupplierModel,
    StockAdjustmentsModel,
    ExpenseCategoriesModel,
    StockTransferModel,
    CategoryModel,
    SubcategoryModel,
    SaleModel,
    SellReturnModel,
    ExpenseModel,
    TaxRatesModel,
    BrandModel,
    UnitsModel,
    TaxGroupModel,
)





PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal'),
    ('G', 'Game'),
    ('E', 'EMI'),
    ('C', 'CCAvenue')
)



class CreateAccountForm(forms.ModelForm):
    """
    Model form to create user account 
    """
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = UserModel
        fields = ('first_name', 'last_name', 'email', 'password', 'confirm_password', 'accept_tc')

    def clean_first_name(self):
        #print(self.cleaned_data['first_name'])
        if self.cleaned_data['first_name'] == '' or self.cleaned_data['first_name'] == None:
            print('The field "First Name" is required.')
            self.add_error('first_name', 'The field "First Name" is required.')
        else:
            return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        #print(self.cleaned_data['last_name'])
        if self.cleaned_data['last_name'] == '' or self.cleaned_data['last_name'] == None:
            print('The field "Last Name" is required.')
            self.add_error('last_name', 'The field "Last Name" is required.')
        else:
            return self.cleaned_data['last_name'].strip()

    def clean_email(self):
        #print(self.cleaned_data['email'])
        if self.cleaned_data['email'] == '' or self.cleaned_data['email'] == None:
            print('The field "Email" is required.')
            self.add_error('email', 'The field "Email" is required.')
        else:
            return self.cleaned_data['email'].strip()

    def clean_accept_tc(self):
        #print(self.cleaned_data['accept_tc'])
        if self.cleaned_data['accept_tc'] != True:
            self.add_error('accept_tc', 'Please accept terms and conditions.')
        else:
            return self.cleaned_data['accept_tc']

    def clean(self):
        cleaned_data = super(CreateAccountForm, self).clean()
        #print(self.cleaned_data['password'])
        #print(self.cleaned_data['accept_tc'])
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            print('Password and confirm password does not match.')
            self.add_error('confirm_password', 'Password and confirm password does not match.')
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(CreateAccountForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].error_messages = {'required': 'The field "First Name" is required'}
        self.fields['last_name'].error_messages = {'required': 'The field "Last Name" is required'}
        self.fields['password'].error_messages = {'required': 'The field "Password" is required'}
        self.fields['confirm_password'].error_messages = {'required': 'The field "Confirm Password" is required'}

class RegisterAccountForm(forms.ModelForm):
    """
    Model form to enter user details to complete registration
    """
    class Meta:
        model = UserModel
        fields = ('phone_number', 'upi_id')

    def clean_phone_number(self):
        print(self.cleaned_data['phone_number'])
        if self.cleaned_data['phone_number'] == '' or self.cleaned_data['phone_number'] == None:
            print('The field "phone number" is required.')
            self.add_error('phone_number', 'The field "Phone Number" is required.')
        else:
            return self.cleaned_data['phone_number'].strip()

    def clean_upi_id(self):
        print(self.cleaned_data['upi_id'])
        if self.cleaned_data['upi_id'] == '' or self.cleaned_data['upi_id'] == None:
            print('The field "UPI ID" is required.')
            self.add_error('upi_id', 'The field "UPI ID" is required.')
        else:
            return self.cleaned_data['upi_id'].strip()

    def clean(self):
        cleaned_data = super(RegisterAccountForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(RegisterAccountForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].error_messages = {'required': 'The field "Phone Number" is required'}
        self.fields['upi_id'].error_messages = {'required': 'The field "UPI ID" is required'}

class AudioRecorderForm(forms.ModelForm):
    """
    Model form to store audio recording data  
    """
    button_id = forms.CharField()
    class Meta:
        model = AudioRecorderModel
        fields = ["audio_file"]

class LoginForm(forms.Form):
    """
    Login form
    """
    email = forms.EmailField(max_length=60)
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_email(self):
        if self.cleaned_data['email'] == '' or self.cleaned_data['email'] == None:
            print('The field "email" is required.')
            self.add_error('email', 'The field "Email" is required.')
        else:
            return self.cleaned_data['email'].strip()

    def clean_password(self):
        if self.cleaned_data['password'] == '' or self.cleaned_data['password'] == None:
            print('The field "password" is required.')
            self.add_error('password', 'The field "password" is required.')
        else:
            return self.cleaned_data['password'].strip()

    def clean(self):
        cleaned_data = super(LoginForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].error_messages = {'required': 'The field "email" is required'}
        self.fields['password'].error_messages = {'required': 'The field "password" is required'}

class OTPForm(forms.Form):
    """
    Form to get OTP token from user for login
    """    
    otp_token = forms.CharField()

    def clean_otp_token(self):
        print(self.cleaned_data['otp_token'])
        if self.cleaned_data['otp_token'] == '' or self.cleaned_data['otp_token'] == None:
            print('The field "otp token" is required.')
            self.add_error('otp_token', 'The field "otp token" is required.')
        if not self.cleaned_data['otp_token'].isnumeric():
            print("OTP can only have numbers")
            self.add_error('otp_token', 'The field "otp token" can only have numbers.')
        else:
            return self.cleaned_data['otp_token'].strip()
    
    def clean(self):
        cleaned_data = super(OTPForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(OTPForm, self).__init__(*args, **kwargs)
        self.fields['otp_token'].error_messages = {'required': 'The field "OTP token" is required'}

class DrawNumberForm(forms.Form):
    """
    Form to get selected number from user
    """    
    selected_number = forms.IntegerField()

    def clean_selected_number(self):
        if self.cleaned_data['selected_number'] == '' or self.cleaned_data['selected_number'] == None:
            print('The field "selected_number" is required.')
            self.add_error('selected_number', 'The field "selected_number" is required.')
        else:
            return self.cleaned_data['selected_number']
    
    def clean(self):
        cleaned_data = super(DrawNumberForm, self).clean()
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(DrawNumberForm, self).__init__(*args, **kwargs)
        self.fields['selected_number'].error_messages = {'required': 'The field "selected_number" is required'}

class MobileRechargeForm(forms.Form):
    """
    Form for mobile recharge
    """
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17) # validators should be a list
    bill_amount = forms.FloatField()

    OPERATOR_CHOICES = list()
    operator = forms.ChoiceField(choices=OPERATOR_CHOICES, required=True)

    def clean_phone_number(self):
        print("phone number", self.cleaned_data['phone_number'])
        if self.cleaned_data['phone_number'] == '' or self.cleaned_data['phone_number'] == None:
            print('The field "phone number" is required.')
            self.add_error('phone_number', 'The field "Phone Number" is required.')
        else:
            return self.cleaned_data['phone_number']

    def clean_bill_amount(self):
        print("Bill amount", self.cleaned_data['bill_amount'])        
        if self.cleaned_data['bill_amount'] == '' or self.cleaned_data['bill_amount'] == None:
            print('The field "bill_amount" is required.')
            self.add_error('bill_amount', 'The field "Bill amount" is required.')
        else:
            return self.cleaned_data['bill_amount']

    def clean(self):
        cleaned_data = super(MobileRechargeForm, self).clean()
        print("cleaned_data", cleaned_data)
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super(MobileRechargeForm, self).__init__(*args, **kwargs)
        self.fields['phone_number'].error_messages = {'required': 'The field "Phone Number" is required'}
        self.fields['bill_amount'].error_messages = {'required': 'The field "Bill amount" is required'}
        self.fields['operator'].error_messages = {'required': 'The field "Operator" is required'}
        queryset = BillerInfoModel.objects.all()
        if queryset:
            for obj in queryset:
                (biller_id, biller_name) = (obj.biller_id, obj.biller_name)
                self.OPERATOR_CHOICES.append((biller_id, biller_name))

class SearchUserForm(forms.ModelForm):
    """
    Form to check if the target user exists or not
    """
    class Meta:
        model = UserModel
        fields = ('email',)

    def clean_email(self):
        print(self.cleaned_data['email'])
        if self.cleaned_data['email'] == '' or self.cleaned_data['email'] == None:
            print('The field "Email" is required.')
            self.add_error('email', 'The field "Email" is required.')
        else:
            return self.cleaned_data['email'].strip()

class RequestMoneyForm(forms.Form):
    """
    Form to receive amount and description for send or receive payment
    """
    amount = forms.CharField()
    description = forms.CharField(max_length=200)

    def clean_amount(self):
        if self.cleaned_data['amount'] == '' or self.cleaned_data['amount'] == None:
            print('The field "amount" is required.')
            self.add_error('amount', 'The field "amount" is required.')
        else:
            try:
                float(self.cleaned_data['amount'])
                return self.cleaned_data['amount'].strip()
            except Exception as e:
                print("errMsg:", str(e))
                self.add_error('amount', 'The field "amount" can only have numbers.')            

    def clean_description(self):
        return self.cleaned_data['description'].strip()

    def __init__(self, *args, **kwargs):
        super(RequestMoneyForm, self).__init__(*args, **kwargs)
        self.fields['amount'].error_messages = {'required': 'The field "Amount" is required'}
        self.fields['description'].error_messages = {'required': 'The field "Description" is required'}

class CCAvenueCheckoutForm(forms.Form):
    amount = forms.CharField()
    billing_name = forms.CharField()
    billing_address = forms.CharField()
    billing_city = forms.CharField()
    billing_state = forms.CharField()
    billing_zip = forms.CharField()
    billing_country = forms.CharField()
    billing_tel = forms.CharField()
    billing_email = forms.CharField()
    delivery_name = forms.CharField()
    delivery_address = forms.CharField()
    delivery_state = forms.CharField()
    delivery_city = forms.CharField()
    delivery_zip = forms.CharField()
    delivery_country = forms.CharField()
    delivery_tel = forms.CharField()
    merchant_param1 = forms.CharField()
    merchant_param2 = forms.CharField()
    merchant_param3 = forms.CharField()
    merchant_param4 = forms.CharField()
    merchant_param5 = forms.CharField()
    promo_code = forms.CharField()
    customer_identifier = forms.CharField()

class MerchantRegistrationForm(forms.ModelForm):
    """
    Model form to create merchant account 
    """
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17) # validators should be a list
    upi_id = forms.CharField()
    subdomain_name_regex = RegexValidator(regex=r'^[a-zA-Z]+[a-zA-Z\d\-]*$', message="Sub-domain name must start with letter and can include letters, digits and hyphen(-) only.")
    subdomain_name = forms.CharField(validators=[subdomain_name_regex], max_length=63)
    country = forms.CharField()
    state = forms.CharField()
    city = forms.CharField()

    class Meta:
        model = MerchantModel
        fields = ('business_name', 'merchant_category', 'subdomain_name', 'timezone')

    def __init__(self, *args, **kwargs):
        super(MerchantRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['business_name'].error_messages = {'required': 'The field "Business name" is required'}
        self.fields['merchant_category'].error_messages = {'required': 'The field "Merchant Category" is required'}
        self.fields['subdomain_name'].error_messages = {'required': 'The field "Sub Domain Name" is required'}
        self.fields['phone_number'].error_messages = {'required': 'The field "Phone Number" is required'}
        self.fields['upi_id'].error_messages = {'required': 'The field "UPI ID" is required'}        
        self.fields['timezone'].error_messages = {'required': 'The field "Timezone" is required'}        
        self.fields['city'].queryset = cities.models.City.objects.none()
        self.fields['state'].queryset = cities.models.Region.objects.none()            
        #self.fields['logo'].error_messages = {'required': 'The field "Logo" is required'}        

class MerchantDetailsForm(forms.ModelForm):
    class Meta:
        model = MerchantModel
        fields = ("tax_1_name", "tax_1_no", "tax_2_name", "tax_2_no", "finanicial_year_start_month" )

    def __init__(self, *args, **kwargs):
        super(MerchantDetailsForm, self).__init__(*args, **kwargs)
        self.fields['tax_1_name'].error_messages = {'required': 'The field "tax 1 name" is required'}
        self.fields['tax_1_no'].error_messages = {'required': 'The field "tax 1 No. " is required'}
        self.fields['tax_2_name'].error_messages = {'required': 'The field "tax 2 name" is required'}
        self.fields['tax_2_no'].error_messages = {'required': 'The field "tax 2 No. " is required'}
        self.fields['finanicial_year_start_month'].error_messages = {'required': 'The field "finanicial year start month" is required'}

class ProductForm(forms.ModelForm):
    """
    Model form to create/update product 
    """
    class Meta:
        model = ProductModel
        exclude = ('merchant', 'supplier','created_at', 'updated_at',)

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key), 
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class PurchaseForm(forms.ModelForm):
    """
    Model form to create/update purchase 
    """
    class Meta:
        model = PurchaseModel
        exclude = ('merchant', 'buyer', 'payment_id', 'pp_without_discount','discount_percent','created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super(PurchaseForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key), 
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key), 
            }

class SaleForm(forms.ModelForm):
    """
    Model form to create/update sale 
    """
    class Meta:
        model = SaleModel
        exclude = ('merchant', 'payment_id', 'discount_percent', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key), 
            }

class SellReturnForm(forms.ModelForm):
    """
    Model form to create/update sell return 
    """
    class Meta:
        model = SellReturnModel
        exclude = ('merchant', 'created_at', 'updated_at')

    def __init__(self, *args, **kwargs):
        super(SellReturnForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key), 
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class PaymentForm(forms.ModelForm):
    """
    Model form to create/update payment 
    """
    class Meta:
        model = PaymentModel
        exclude = ('merchant', 'is_return', )

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class ProductVariationForm(forms.ModelForm):
    """
    Model form to create/update product variation 
    """
    class Meta:
        model = ProductVariationsModel
        fields = ('name', 'value', 'product_id')

    def __init__(self, *args, **kwargs):
        super(ProductVariationForm, self).__init__(*args, **kwargs)

        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class SupplierRegistrationForm(forms.ModelForm):
    """
    Model form to create supplier account 
    """
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = forms.CharField(validators=[phone_regex], max_length=17) # validators should be a list
    upi_id = forms.CharField()
    country = forms.CharField()
    state = forms.CharField()
    city = forms.CharField()

    class Meta:
        model = SupplierModel
        fields = ('business_name', 'supplier_category', 'timezone')

    def __init__(self, *args, **kwargs):
        super(SupplierRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['business_name'].error_messages = {'required': 'The field "Business name" is required'}
        self.fields['supplier_category'].error_messages = {'required': 'The field "Supplier Category" is required'}
        self.fields['phone_number'].error_messages = {'required': 'The field "Phone Number" is required'}
        self.fields['upi_id'].error_messages = {'required': 'The field "UPI ID" is required'}        
        self.fields['timezone'].error_messages = {'required': 'The field "Timezone" is required'}        
        self.fields['city'].queryset = cities.models.City.objects.none()
        self.fields['state'].queryset = cities.models.Region.objects.none()            

class SupplierDetailsForm(forms.ModelForm):
    class Meta:
        model = SupplierModel
        fields = ("tax_1_name", "tax_1_no", "tax_2_name", "tax_2_no" )

    def __init__(self, *args, **kwargs):
        super(SupplierDetailsForm, self).__init__(*args, **kwargs)
        self.fields['tax_1_name'].error_messages = {'required': 'The field "tax 1 name" is required'}
        self.fields['tax_1_no'].error_messages = {'required': 'The field "tax 1 No. " is required'}
        self.fields['tax_2_name'].error_messages = {'required': 'The field "tax 2 name" is required'}
        self.fields['tax_2_no'].error_messages = {'required': 'The field "tax 2 No. " is required'}

class StockAdjustmentsForm(forms.ModelForm):
    """
    Modelform to create stock adjustment record
    """
    class Meta:
        model = StockAdjustmentsModel
        exclude = ('merchant', 'created_at', 'updated_at', )

    def __init__(self, *args, **kwargs):
        super(StockAdjustmentsForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }
        
class StockTransferForm(forms.ModelForm):
    """
    Modelform to create stock transfer record
    """
    class Meta:
        model = StockTransferModel
        exclude = ('merchant', 'created_at', 'updated_at', )

    def __init__(self, *args, **kwargs):
        super(StockTransferForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }
       
class ExpenseCategoryForm(forms.ModelForm):
    """
    Modelform to create expense category
    """
    class Meta:
        model = ExpenseCategoriesModel
        fields = ('name', 'code')
    
    def __init__(self, *args, **kwargs):
        super(ExpenseCategoryForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class ExpenseForm(forms.ModelForm):
    """
    Modelform to create expense record
    """
    class Meta:
        model = ExpenseModel
        exclude = ('merchant', )

    def __init__(self, *args, **kwargs):
        super(ExpenseForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class TaxRatesForm(forms.ModelForm):
    """
    Modelform to create tax rates
    """
    class Meta:
        model = TaxRatesModel
        exclude = ('merchant', )

    def __init__(self, *args, **kwargs):
        super(TaxRatesForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class BrandsForm(forms.ModelForm):
    """
    Modelform to create tax rates
    """
    class Meta:
        model = BrandModel
        exclude = ('merchant', )

    def __init__(self, *args, **kwargs):
        super(BrandsForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class UnitsForm(forms.ModelForm):
    """
    Modelform to create tax rates
    """
    class Meta:
        model = UnitsModel
        exclude = ('merchant', )

    def __init__(self, *args, **kwargs):
        super(UnitsForm, self).__init__(*args, **kwargs)
        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

class TaxGroupForm(forms.ModelForm):    
    """
    Modelform to create tax groups
    """
    sub_taxes = forms.ModelMultipleChoiceField(
        widget = forms.CheckboxSelectMultiple(),
        queryset = TaxRatesModel.objects.all()
        )
    class Meta:
        model = TaxGroupModel
        exclude = ('merchant', )

    def __init__(self, *args, **kwargs):
        super(TaxGroupForm, self).__init__(*args, **kwargs)
        #self.fields['sub_taxes'].queryset = TaxRatesModel.objects.filter(merchant=merchant)

        for key,value in self.fields.items():
            value.error_messages = {
                'required':'The field {0} is required'.format(key), 
                'invalid': "Please enter valid data for the field : {0}".format(key),
                'invalid_choice': "Please enter valid choice for the field : {0}".format(key),
            }

# -------------------------------------------------------------------------------------------------------------------

class CheckoutForm(forms.Form):
    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '1234 Main St',
        'class': 'form-control'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Apartment or suite',
        'class': 'form-control'
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class': 'custom-select d-block w-100'

    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control'
    }))
    same_shipping_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Promo code'
    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4
    }))
    email = forms.EmailField()
