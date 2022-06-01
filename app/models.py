from email.policy import default
from unittest.mock import DEFAULT
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.conf import settings
import cities.models as city_models
from numpy import product
from timezone_field import TimeZoneField
import calendar
from datetime import datetime
from django.shortcuts import reverse
from django_countries.fields import CountryField


ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping'),
)

class CustomManager(BaseUserManager):
    """
    Custom user manager for custom user model creation
    """
    def create_user(self, email, first_name, last_name, password, accept_tc):
        """
        Function to create user.
        Parameters:
            email (EmailField) : User's email
            first_name (CharField): User's first name
            last_name (CharField): User's last name
            password (CharField): User's password
            accept_tc (BooleanField): Checkbox to accept T&C
        Returns:
            user : UserModel instance
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not first_name:
	        raise ValueError('Users must have a first name')
        if not password:
	        raise ValueError('Users must have a password')
        if not accept_tc:
            raise ValueError('Users must accept T&C')
        if accept_tc!=True:
            raise ValueError('Please accept T&C to create user')

        user = self.model(
		    email=self.normalize_email(email),
		    first_name=first_name,
            last_name=last_name,
        )
        #Added to login to admin panel with staff user account
        user.is_staff = True
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, password, accept_tc):
        """
        Function to create super user.
        Parameters:
            email (EmailField) : User's email
            first_name (CharField): User's first name
            last_name (CharField): User's name name
            password (CharField): User's password
            accept_tc (BooleanField): Checkbox to accept T&C
        Returns:
            user : UserModel instance
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not first_name:
        	raise ValueError('Users must have a first name')
        if not password:
        	raise ValueError('Users must have a password')

        user = self.model(
		    email=self.normalize_email(email),
		    first_name=first_name,
            last_name=last_name,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()
        return user

class UserModel(AbstractBaseUser, PermissionsMixin):
    """
    Model to store users to the system.

    Attributes:
        email (EmailField) : User's email address
        first_name (CharField) : User's first name
        last_name (CharField) : User's last name
        password (CharField) : password field
        accept_tc (BooleanField) : Checkbox to accept T&C
        is_active (BooleanField) : Field depicts if user account is active
        is_admin (BooleanField) : Field depicts if user is in admin category
        is_staff (BooleanField) : Field depicts if user is in staff category
        is_superuser (BooleanField) : Field depicts if user is superuser
        last_login (DateTimeField) : To store last login time of the user
        phone_number (CharField) : To store user's phone number
        upi_id (CharField) : User's UPI ID
    """
    email    = models.EmailField(max_length=60, unique=True, db_index=True)
    first_name = models.CharField(max_length=30, blank = True, null = True)
    last_name = models.CharField(max_length=30, blank = True, null = True)
    #Consider Hashed password length
    password = models.CharField(max_length=128, verbose_name='password')
    accept_tc = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    upi_id = models.CharField(max_length=45, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = CustomManager()

    def __str__(self):
        return self.email

class SampleStringModel(models.Model):   
    """
    Model to store voice sample strings.

    Attributes:
        sample_string (CharField) : sample string to record when user registers
    """
    sample_string = models.CharField(max_length = 50)

def audio_file_path(instance, filename):
    # audio file will be uploaded to MEDIA_ROOT/registration/user_<id>_<sample_string_id><ext>
    #ext = ".webm"
    ext = ".wav"
    return 'registration/user_{0}_{1}{2}'.format(instance.user.id, instance.sample_string.id, ext)

class AudioRecorderModel(models.Model):
    """
    Model to store audio recordings of user

    Attributes:
        audio_file(FileField) : Field to store audio blob data 
        user : Reference to UserModel instance
    """
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    sample_string = models.ForeignKey(SampleStringModel, on_delete=models.PROTECT)
    audio_file = models.FileField(upload_to=audio_file_path)

class OTPVerificationModel(models.Model):
    """
    Model for OTP verification 

    Attributes:
        email(EmailField) : Field to store user's email address
        isVerified(BooleanField) : Field depicts if user is verified or not for login
        counter(IntegerField) : Field to store login OTP counter for HOTP algorithm
        isVerified_payment(BooleanField) : Field depicts if user is verified or not when trying for bill payment
        counter_payment(IntegerField) : Field to store payment OTP counter for HOTP algorithm
    """
    email    = models.EmailField(max_length=60, blank=False)
    isVerified = models.BooleanField(blank=False, default=False)
    counter = models.IntegerField(default=0, blank=False)
    isVerified_payment = models.BooleanField(blank=False, default=False)
    counter_payment = models.IntegerField(default=0, blank=False)
    
    def __str__(self):
        return str(self.email)

class BillerInfoModel(models.Model):
    """
    Model to store available biller information.

    Attributes:
        biller_id (CharField) : string to store Biller ID
        biller_name (CharField) : string to store Biller name
    """
    biller_id = models.CharField(max_length = 20)
    biller_name = models.CharField(max_length = 20)

class MobileRechargeBillModel(models.Model):
    """
    Model to store mobile recharge bill details

    Attributes:
        biller (ForeignKey) : foreign key to biller instance
        phone_number (CharField) : string to store mobile number
        bill_amount (FloatField) : float to store bill amount
        payer_name (CharField) : string to store payer's name
        transaction_date (DateTimeField) : Date and time of the bill creation
    """
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    biller = models.ForeignKey(BillerInfoModel, on_delete=models.PROTECT)
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True) # validators should be a list
    bill_amount = models.FloatField()
    payer_name = models.CharField(max_length=60)
    transaction_date = models.DateTimeField(default=now, editable=False)

class UrlShortnerModel(models.Model):
    """
    Model to store shortlinks
    """
    long_url = models.URLField()
    short_id = models.SlugField()

class RazorpayTransactionModel(models.Model):
    """
    Model to store transaction using razorpay
    """
    amount = models.FloatField()
    description = models.CharField(max_length = 50)
    order_id = models.CharField(max_length = 50)
    payment_id = models.CharField(max_length = 50, blank = True)
    is_completed = models.BooleanField(default = False)
    payer = models.ForeignKey(UserModel, on_delete = models.PROTECT)

class CCAvenueSurchargeModel(models.Model):
    """
    Model to store surcharge in pct.(%) to different payment mode with CCAvenue
    """
    payment_mode = models.CharField(max_length = 30)
    surcharge = models.FloatField()

class RazorpaySurchargeModel(models.Model):
    """
    Model to store surcharge in pct.(%) to different payment mode with Razorpay
    """
    payment_mode = models.CharField(max_length = 30)
    surcharge = models.FloatField()

class MerchantModel(models.Model):   
    """
    Model to store merchant details.

    Attributes:
        business_name (CharField) : Business name
        subdomain_name (CharField) : Sub domain name
        merchant (OneToOneField) : One to one relationship with UserModel
        merchant_category (CharField) : Merchant profession category
        merchant_country (ForeignKey) : Foreign key of Country model
        merchant_state (ForeignKey) : Foreign key of Region model
        merchant_city (ForeignKey) : Foreign key of City model
        timezone (TimeZoneField): time zone field
        tax_1_name (CharField) : Tax 1 name
        tax_1_no (CharField) : Tax 1 number
        tax_2_name (CharField) : Tax 2 name
        tax_2_no (CharField) : Tax 2 number
        finanicial_year_start_month (CharField) : Financial year start month
    """
    business_name = models.CharField(max_length=30)
    subdomain_name_regex = RegexValidator(regex=r'^[a-zA-Z]+[a-zA-Z\d\-]*$', message="Sub-domain name start with letter and can include only letters, digits, and hyphen(-) in it.")
    merchant = models.OneToOneField(UserModel, on_delete=models.CASCADE)
    subdomain_name = models.CharField(validators=[subdomain_name_regex], max_length=63, unique=True)

    CATEGORY_CHOICE = (
        ('fashion', 'Fashion'),
        ('books', 'Books'),
        ('movie_tickets', 'Movie Tickets'),
        ('electronics', 'Electronics'),
        ('groceries', 'Groceries'),
        ('food', 'Food Takeaway/Delivery'),
        ('baby_products', 'Baby Products'),
    )
    merchant_category = models.CharField(max_length=30, choices=CATEGORY_CHOICE, default='1') 

    #logo = models.ImageField(upload_to=settings.MERCHANT_LOGO)  
    merchant_country = models.ForeignKey(city_models.Country, on_delete=models.PROTECT)
    merchant_state = models.ForeignKey(city_models.Region, on_delete=models.PROTECT)
    merchant_city = models.ForeignKey(city_models.City, on_delete=models.PROTECT)
    timezone = TimeZoneField(default='Asia/Kolkata') 
    tax_1_name = models.CharField(max_length=50, blank=True)
    tax_1_no = models.CharField(max_length=50, blank=True)
    tax_2_name = models.CharField(max_length=50, blank=True)
    tax_2_no = models.CharField(max_length=50, blank=True)

    MONTH_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1,13)]
    finanicial_year_start_month = models.CharField(max_length=9, choices=MONTH_CHOICES, default='1')

    def __str__(self):
        return self.business_name

class SupplierModel(models.Model):   
    """
    Model to store supplier details.

    Attributes:
        business_name (CharField) : Business name
        supplier (OneToOneField) : One to one relationship with UserModel
        supplier_category (CharField) : Merchant profession category
        supplier_country (ForeignKey) : Foreign key of Country model
        supplier_state (ForeignKey) : Foreign key of Region model
        supplier_city (ForeignKey) : Foreign key of City model
        timezone (TimeZoneField): time zone field
        tax_1_name (CharField) : Tax 1 name
        tax_1_no (CharField) : Tax 1 number
        tax_2_name (CharField) : Tax 2 name
        tax_2_no (CharField) : Tax 2 number
    """
    business_name = models.CharField(max_length=30)
    supplier = models.OneToOneField(UserModel, on_delete=models.CASCADE)

    CATEGORY_CHOICE = (
        ('fashion', 'Fashion'),
        ('books', 'Books'),
        ('movie_tickets', 'Movie Tickets'),
        ('electronics', 'Electronics'),
        ('groceries', 'Groceries'),
        ('food', 'Food Takeaway/Delivery'),
        ('baby_products', 'Baby Products'),
    )
    supplier_category = models.CharField(max_length=30, choices=CATEGORY_CHOICE, default='1')   
    supplier_country = models.ForeignKey(city_models.Country, on_delete=models.PROTECT)
    supplier_state = models.ForeignKey(city_models.Region, on_delete=models.PROTECT)
    supplier_city = models.ForeignKey(city_models.City, on_delete=models.PROTECT)
    timezone = TimeZoneField(default='Asia/Kolkata') 
    tax_1_name = models.CharField(max_length=50, blank=True)
    tax_1_no = models.CharField(max_length=50, blank=True)
    tax_2_name = models.CharField(max_length=50, blank=True)
    tax_2_no = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.business_name

class CategoryModel(models.Model):
    """
    Model to store product categories
    Attributes:
        category_name(CharField) : category name
        short_code(CharField) : category code
    """
    category_name = models.CharField(max_length=25)
    short_code = models.CharField(max_length=191)

    def __str__(self):
        return self.category_name

class SubcategoryModel(models.Model):
    """
    Model to store subcategories
    Attributes:
        category(ForeignKey) : foreign key of CategoryModel
        subcategory_name(CharField) : subcategory name
        short_code(CharField) : subcategory code
    """
    category = models.ForeignKey(CategoryModel, on_delete=models.PROTECT)
    subcategory_name = models.CharField(max_length=25)
    short_code = models.CharField(max_length=191)

    def __str__(self):
        return self.subcategory_name

class BrandModel(models.Model):
    """
    Model to store brands
    Attributes:
        brand_name(CharField) : brand name
        brand_description(CharField) : brand description
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    brand_name = models.CharField(max_length=25)
    brand_description = models.CharField(max_length=255)

    def __str__(self):
        return self.brand_name

class TaxRatesModel(models.Model):
    """
    Model to store tax rates.

    Attributes:
        name (CharField) : Tax name
        amount (FloatField) : Tax amount
        deleted_at (DateTimeField) : Timestamp of tax object deletion
        created_at (DateTimeField) : Timestamp of tax object creation
        updated_at (DateTimeField) : Timestamp of tax object updation
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    name = models.CharField(max_length=191)
    rate = models.FloatField()
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class TaxGroupModel(models.Model):
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    name = models.CharField(max_length=191)
    sub_taxes = models.ManyToManyField(TaxRatesModel)

class ProductModel(models.Model): 
    """
    Model to store product details.

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with merchant instance
        supplier (ForeignKey) : Foreign key field relationship with supplier instance
        product_name (CharField) : Product name
        product_description (CharField) : Product description
        product_price (CharField) : Product price
        product_stock (IntegerField) : Product available stock
        product_category (CharField) : Product category
        product_subcategory (CharField) : Product subcategory
        product_type (CharField) : Product type
        product_units (CharField) : Product units
        product_brand (ForeignKey) : Foreign key field of BrandModel
        product_SKU (CharField) : Product SKU
        product_image (ImageField) : Product image
        tax (PositiveIntegerField) : Tax on product    
        tax_type (CharField) : Tax type on product
        enable_stock (BooleanField) : Enable stock of product
        alert_quantity (IntegerField) : Alert product quantity
        expiry_period (DecimalField) : Expiry period   
        expiry_period_type (CharField) : Expiry period type in days/months
        enable_sr_no (BooleanField) : Enable Sr No.
        weight (CharField) : Weight of the product
        product_custom_field1 (CharField) : Custom field
        product_custom_field2 (CharField) : Custom field
        product_custom_field3 (CharField) : Custom field
        product_custom_field4 (CharField) : Custom field 
        mfg_date (DateField) : Manufacturing date
        exp_date (DateField) : Expiry date
        lot_number (CharField) : Lot number
        created_at (DateTimeField) : Product creation timestamp
        updated_at (DateTimeField) : Product updation timestamp
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.CASCADE)
    supplier = models.ForeignKey(SupplierModel, on_delete=models.CASCADE, blank=True, null=True)
    product_name = models.CharField(max_length=191, unique=True)
    product_description = models.CharField(max_length=1000)
    product_price = models.FloatField()
    product_stock = models.IntegerField()

    discount_price = models.FloatField(blank=True, null=True)



    slug = models.SlugField()

    

    # PRODUCT_CATEGORY_CHOICE = (
    #     ('fashion', 'Fashion'),
    #     ('books', 'Books'),
    #     ('electronics', 'Electronics'),
    #     ('groceries', 'Groceries'),
    #     ('food', 'Food'),
    #     ('baby_products', 'Baby Products'),
    # )
    
    product_category = models.ForeignKey(CategoryModel, on_delete=models.PROTECT, blank=True, null=True)
    product_subcategory = models.ForeignKey(SubcategoryModel, on_delete=models.PROTECT, blank=True, null=True)

    PRODUCT_TYPE_CHOICE = (
        ('single', 'Single'),
        ('variable', 'Variable'),
    )
    product_type = models.CharField(max_length=30, choices=PRODUCT_TYPE_CHOICE)

    PRODUCT_UNITS_CHOICE = (
        ('Pc(s)', 'Pieces'),
        ('gm', 'gm'),
    )
    product_units = models.CharField(max_length=10, choices=PRODUCT_UNITS_CHOICE)
    product_brand = models.ForeignKey(BrandModel, on_delete=models.PROTECT, blank=True, null=True)
    product_SKU = models.CharField(max_length=191)
    product_image = models.ImageField()


    product_image2 = models.ImageField()
    product_image3 = models.ImageField()
    product_image4 = models.ImageField()


    tax = models.ForeignKey(TaxRatesModel, on_delete=models.PROTECT, blank=True, null=True)

    TAX_TYPE_CHOICE = (
        ('inclusive', 'Inclusive'),
        ('exclusive', 'Exclusive'), 
    )
    tax_type = models.CharField(max_length=9, choices=TAX_TYPE_CHOICE, blank=True, null=True)
    enable_stock = models.BooleanField(default=False)
    alert_quantity = models.IntegerField(blank=True, null=True)    
    expiry_period = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)

    EXPIRY_PERIOD_TYPE = (
        ('days', 'Days'),
        ('months', 'Months'),
        ('not applicable', 'Not Applicable'),
    )
    expiry_period_type = models.CharField(max_length=15, choices=EXPIRY_PERIOD_TYPE, blank=True, null=True)
    enable_sr_no = models.BooleanField(default=False)    
    weight = models.CharField(max_length=191, blank=True, null=True)
    product_custom_field1 = models.CharField(max_length=191, blank=True, null=True)
    product_custom_field2 = models.CharField(max_length=191, blank=True, null=True)
    product_custom_field3 = models.CharField(max_length=191, blank=True, null=True)
    product_custom_field4 = models.CharField(max_length=191, blank=True, null=True)
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    lot_number = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True, auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)




    OFFER_TYPES = (
        ('prediction_game', 'Prediction Game'),
        ('discount', 'Discount'),
        ('with_emi', 'With EMI')
    )



    def __str__(self):
        return self.product_name

    def get_absolute_url(self):
        return reverse("app:shopdetail", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("app:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("app:remove-from-cart", kwargs={
            'slug': self.slug
        })


class ExpenseCategoriesModel(models.Model):
    """
    Model to store expense categories

    Attributes:
        name (CharField) : Expense category name
        code (CharField) : Expense category code
        deleted_at (DateTimeField) : Timestamp of expense category object deletion
        created_at (DateTimeField) : Timestamp of expense category object creation
        updated_at (DateTimeField) : Timestamp of expense category object updation
    """
    name = models.CharField(max_length=191)
    code = models.CharField(max_length=191, blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

class TransactionModel(models.Model):
    """
    Model to store transaction details.

    Attributes:
        transaction_type (CharField) : Type of transaction
        adjustment_type (CharField): Adjustment type      
        transaction_status (CharField) : Transaction status
        payment_status (CharField) : Payment status        
        is_quotation (IntegerField) : Quotation variable
        invoice_no (CharField) : Invoice number
        ref_no (CharField) : Reference number
        transaction_date (DateTimeField) : Transaction date
        total_before_tax (DecimalField) : Total amount without including tax
        tax_id (ForeignKey) : Forign key field of TaxRatesModel
        tax_amount (DecimalField) : Calculated tax amount    
        discount_type (CharField) : Discount type
        discount_amount (CharField) : Discount amount
        shipping_details (CharField) : Shipping details
        shipping_charges (DecimalField) : Shipping charges
        additional_notes (TextField) : Additional note
        staff_note (TextField) : Staff note
        final_total (DecimalField) : Final amount including tax
        expense_category_id (ForeignKey) : Foreign key relationship with expense category model
        expense_note (TextField) : Expense note
        payer (ForeignKey) : Payer of the transaction
        recipient (ForeignKey) : Recipient of the transaction
        is_direct_sale (IntegerField) : Variable to check if direct or indirect sale
        exchange_rate (DecimalField) : Exchange rate of product
        total_amount_recovered (DecimalField) : Total amount recovered in case of stock adjacements
        created_at (DateTimeField) : Timestamp of object creation
        updated_at (DateTimeField) : Timestamp of object updation
    """
    TRANSACTION_TYPE_CHOICES = (
        ('purchase', 'Purchase'),
        ('sell', 'Sell') ,
        ('expense', 'Expense'),
        ('stock_adjustment', 'Stock adjustment'),
        ('sell_transfer', 'Sell transfer'),
        ('purchase_transfer', 'Purchase transfer'),
        ('opening_stock', 'Opening stock'),
        ('sell_return', 'Sell return'),
        ('opening_balance', 'Opening balance'),
        ('stock_transfer', 'Stock transfer'),
    )
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPE_CHOICES, default=None)     

    ADJUSTMENT_TYPE_CHOICES = (
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal'),
    )
    adjustment_type = models.CharField(max_length=8, choices=ADJUSTMENT_TYPE_CHOICES, blank=True, null=True)

    TRANSACTION_STATUS_CHOICES = (
        ('received', 'received'),
        ('pending', 'pending'),
        ('ordered', 'ordered'),
        ('draft', 'draft'),
        ('final', 'final'),
    )
    transaction_status = models.CharField(max_length=10, choices=TRANSACTION_STATUS_CHOICES, default=1)   

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('due', 'Due'),
        ('partial', 'Partial'),
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=None)     
    
    is_quotation = models.IntegerField(default=0)
    invoice_no = models.CharField(max_length=191, blank=True, null=True)
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    transaction_date = models.DateTimeField()
    total_before_tax = models.DecimalField(max_digits=20, decimal_places=2)
    tax_id = models.ForeignKey(TaxRatesModel, on_delete=models.PROTECT, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)

    DISCOUNT_TYPE_CHOICES = (
        ('fixed', 'Fixed'),
        ('percentage','Percentage'),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    discount_amount = models.CharField(max_length=10, blank=True, null=True)
    shipping_details = models.CharField(max_length=191, blank=True, null=True)
    shipping_charges = models.DecimalField(max_digits=20, decimal_places=2)
    additional_notes = models.TextField(blank=True, null=True)
    staff_note = models.TextField(blank=True, null=True)
    final_total = models.DecimalField(max_digits=20, decimal_places=2)
    expense_category_id = models.ForeignKey(ExpenseCategoriesModel, on_delete=models.PROTECT)
    expense_note = models.TextField(blank=True, null=True)
    payer = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name="transaction_payer") 
    recipient = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name="transaction_recipient")        
    #location_id = models.PositiveIntegerField() 
    #commission_agent = models.IntegerField(blank=True, null=True)
    #document = models.CharField(max_length=191, blank=True, null=True)
    is_direct_sale = models.IntegerField(default=0)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=3, default=1.00)
    total_amount_recovered = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    #transfer_parent_id = models.IntegerField(blank=True, null=True)
    #opening_stock_product_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True)
    
class LocationModel(models.Model):
    """
    Models to store business location
    Attributes:
        name (CharField) : Location name
        country (ForeignKey) : Foreign key of Country model
        state (ForeignKey) : Foreign key of Region model
        city (ForeignKey) : Foreign key of City model
    """
    name = models.CharField(max_length = 191)
    country = models.ForeignKey(city_models.Country, on_delete=models.PROTECT)
    state = models.ForeignKey(city_models.Region, on_delete=models.PROTECT)
    city = models.ForeignKey(city_models.City, on_delete=models.PROTECT)

class PaymentModel(models.Model):
    """
    Model to store payment details.

    Attributes:
        payer (ForeignKey) : Payer of the transaction
        recipient (ForeignKey) : Recipient of the transaction
        transaction_id (ForeignKey) : Foreign key field relationship with TransactionModel instance
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance
        supplier (ForeignKey) : Foreign key field relationship with SupplierModel instance
        payment_method (CharField) : Payment method
        card_transaction_number (CharField) : Card transaction number
        card_number (CharField) : card number
        card_type (CharField) : card type
        card_holder_name (CharField) : card holder name
        card_month (CharField) : Card expiry month 
        card_year (CharField) : Card expiry year
        card_security (CharField) : Card security number
        cheque_number (CharField) : Cheque number
        bank_account_number (CharField) : Bank account number
        paid_on (DateTimeField) : Payment date
        payment_ref_no (CharField) : Payment reference number
        is_return (IntegerField) : Order has been returned or not
        note (CharField) : Payment note 
        created_at (DateTimeField) : Payment creation timestamp
        updated_at (DateTimeField) : Payment updation timestamp   
    """
    payer = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name="payment_payer", default=1) 
    recipient = models.ForeignKey(UserModel, on_delete=models.PROTECT, related_name="payment_recipient", default=1)        
    payment_amount = models.FloatField()
    #transaction_id = models.ForeignKey(TransactionModel, on_delete=models.PROTECT)
    #merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    #supplier = models.ForeignKey(SupplierModel, on_delete=models.PROTECT)

    PAYMENT_METHOD_CHOICES = (
        ('Wallet', 'Paybills Wallet'), 
        ('Card', 'Cards'), 
        ('Bank', 'Bank'),
    )
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default=None)

    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('due', 'Due'),
        ('partial', 'Partial'),
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=None)     
  
    card_transaction_number = models.CharField(max_length=191, blank=True, null=True)
    card_number = models.CharField(max_length=191, blank=True, null=True)

    CARD_TYPE_CHOICE = (
        ('visa', 'Visa'),
        ('master', 'Master'),
    )
    card_type = models.CharField(max_length=6, choices=CARD_TYPE_CHOICE, blank=True, null=True)
    
    card_holder_name = models.CharField(max_length=191, blank=True, null=True)
    card_month = models.CharField(max_length=191, blank=True, null=True)
    card_year = models.CharField(max_length=191, blank=True, null=True)
    card_security = models.CharField(max_length=5, blank=True, null=True)
    cheque_number = models.CharField(max_length=191, blank=True, null=True)
    bank_account_number = models.CharField(max_length=191, blank=True, null=True)
    paid_on = models.DateTimeField(blank=True, null=True)   
    payment_ref_no = models.CharField(max_length=191, blank=True, null=True)
    is_return = models.IntegerField(default=0)
    payment_note = models.CharField(max_length=191, blank=True, null=True)
    created_at = models.DateTimeField(default=now, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)
   
class PurchaseModel(models.Model):
    """
    Model to store purchase details.

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance
        supplier (ForeignKey) : Foreign key field relationship with SupplierModel instance
        product (ForeignKey) : Foreign key field relationship with ProductModel instance
        buyer (ForeignKey) : Foreign key field relationship with UserModel instance
        purchase_amount (FloatField) : Purchase amount
        payment_due (FloatField) : Payment due amount
        discount_amount (FloatField) : Discount amount
        purchase_status (CharField) : Purchase status choice        
        payment (CharField) : Foreign key field relationship with payment instance
        ref_no (CharField) : Reference number
        shipping_details (CharField) : Shipping details
        shipping_charges (DecimalField) : Shipping charges
        additional_notes (TextField) : Additional note
        created_at (DateField) : Timestamp of order creation
        updated_at (DateTimeField) : Payment object updation timestamp        
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.CASCADE)
    supplier = models.ForeignKey(SupplierModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    buyer = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)   
    
    PURCHASE_STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('decline', 'Decline'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
    )
    purchase_status = models.CharField(max_length=10, choices=PURCHASE_STATUS_CHOICE)   
    payment_id = models.ForeignKey(PaymentModel, on_delete=models.PROTECT)
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    purchase_date = models.DateTimeField()    
    quantity = models.IntegerField(default=1)    
    pp_without_discount = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    discount_amount = models.FloatField(default = 0.0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    item_tax = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    tax_id = models.ForeignKey(TaxRatesModel, on_delete=models.PROTECT, blank=True, null=True)
    total_purchase_price = models.DecimalField(max_digits=20, decimal_places=2)
    payment_due = models.FloatField(default = 0.0)   
    quantity_sold = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    quantity_adjusted = models.DecimalField(max_digits=20, decimal_places=4, blank=True, null=True)
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    lot_number = models.CharField(max_length=256, blank=True, null=True)
    DISCOUNT_TYPE_CHOICES = (
        ('fixed', 'Fixed'),
        ('percentage','Percentage'),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    shipping_details = models.CharField(max_length=191, blank=True, null=True)
    shipping_charges = models.DecimalField(max_digits=20, decimal_places=2)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

class SaleModel(models.Model):
    """
    Model to store sale details.

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance
        product (ForeignKey) : Foreign key field relationship with ProductModel instance
        customer (ForeignKey) : Foreign key field relationship with UserModel instance
        payment_due (FloatField) : Payment due amount
        discount_amount (FloatField) : Discount amount
        purchase_status (CharField) : Purchase status choice        
        payment (CharField) : Foreign key field relationship with payment instance
        ref_no (CharField) : Reference number
        shipping_details (CharField) : Shipping details
        shipping_charges (DecimalField) : Shipping charges
        additional_notes (TextField) : Additional note
        created_at (DateField) : Timestamp of order creation
        updated_at (DateTimeField) : Payment object updation timestamp        
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.CASCADE)
    #supplier = models.ForeignKey(SupplierModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    customer = models.ForeignKey(UserModel, on_delete=models.CASCADE, null=True)   
    
    SALE_STATUS_CHOICE = (
        ('final', 'Final'),
        ('draft', 'Draft'),
        ('quatation', 'Quatation'),
    )
    sale_status = models.CharField(max_length=10, choices=SALE_STATUS_CHOICE)   
    payment_id = models.ForeignKey(PaymentModel, on_delete=models.PROTECT)
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    sale_date = models.DateTimeField()  
    quantity = models.IntegerField(default=1)      
    discount_amount = models.FloatField(default = 0.0)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    item_tax = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    tax_id = models.ForeignKey(TaxRatesModel, on_delete=models.PROTECT, blank=True, null=True)
    total_sell_price = models.DecimalField(max_digits=20, decimal_places=2)
    payment_due = models.FloatField(default = 0.0)  
    mfg_date = models.DateField(blank=True, null=True)
    exp_date = models.DateField(blank=True, null=True)
    lot_number = models.CharField(max_length=256, blank=True, null=True)
    DISCOUNT_TYPE_CHOICES = (
        ('fixed', 'Fixed'),
        ('percentage','Percentage'),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    shipping_details = models.CharField(max_length=191, blank=True, null=True)
    shipping_charges = models.DecimalField(max_digits=20, decimal_places=2)
    sell_notes = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

class SellReturnModel(models.Model):
    """
    Model to store sell return details.

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance
        product (ForeignKey) : Foreign key field relationship with ProductModel instance
        customer (ForeignKey) : Foreign key field relationship with UserModel instance
        discount_amount (FloatField) : Discount amount
        payment (CharField) : Foreign key field relationship with payment instance
        ref_no (CharField) : Reference number
        additional_notes (TextField) : Additional note
        created_at (DateField) : Timestamp of order creation
        updated_at (DateTimeField) : Payment object updation timestamp        
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    business_location = models.ForeignKey(LocationModel, on_delete=models.PROTECT)
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    customer = models.ForeignKey(UserModel, on_delete=models.PROTECT, null=True)   
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    purchase_date = models.DateTimeField()  
    discount_amount = models.FloatField(default = 0.0)    
    total_credit_amount = models.DecimalField(max_digits=20, decimal_places=2)   
    DISCOUNT_TYPE_CHOICES = (
        ('fixed', 'Fixed'),
        ('percentage','Percentage'),
    )
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)
    created_at = models.DateField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(blank=True, null=True, auto_now_add=True)

# class ProductVariationsModel(models.Model):
#     """
#     Model to store product variations

#     Attributes:
#         name (CharField) : Product variation name
#         product_id (ForeignKey) : Foreign key field relationship with ProductModel instance
#         created_at (DateTimeField) : Object creation timestamp
#         updated_at (DateTimeField) : Object updation timestamp
#     """
#     name = models.CharField(max_length=191)
#     product_id = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
#     #is_dummy = models.IntegerField()
#     created_at = models.DateTimeField(blank=True, null=True)
#     updated_at = models.DateTimeField(blank=True, null=True)

class ProductVariationsModel(models.Model):
    """
    Model to store variations

    Attributes:
        name (CharField) : Variation name
        value (CharField) : Variation value
        product_id (ForeignKey) : Foreign key field relationship with ProductModel instance
        sub_sku (CharField) : Product sub-SKU
        default_purchase_price (DecimalField) : Default purchase price of product
        dpp_inc_tax (DecimalField) : Default purchase price inclusive of tax
        profit_percent (DecimalField) : Profit percentage
        default_sell_price (DecimalField) : Default sell price
        sell_price_inc_tax (DecimalField) : Sell price inclusive of tax
        created_at (DateTimeField) : Object creation timestamp
        updated_at (DateTimeField) : Object updation timestamp
        deleted_at (DateTimeField) : Object deletion timestamp
    """
    name = models.CharField(max_length=191)
    value = models.CharField(max_length=255, unique=True)
    product_id = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    sub_sku = models.CharField(max_length=191, blank=True, null=True)
    #product_variation_id = models.ForeignKey(ProductVariationsModel, on_delete=models.PROTECT)
    default_purchase_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    dpp_inc_tax = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    profit_percent = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    default_sell_price = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    sell_price_inc_tax = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

class StockAdjustmentsModel(models.Model):
    """
    Models to store stock adjustments

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance
        product_id (ForeignKey) : Foreign key field relationship with ProductModel instance
        variation_id (ForeignKey) : Foreign key field relationship with ProductVariationsModel instance
        business_location (ForeignKey) : Foreign key field relationship with LocationModel instance
        quantity (DecimalField) : Product quantity
        unit_price (DecimalField) : Price per unit
        removed_purchase_line (IntegerField) : 
        created_at (DateTimeField) : Object creation timestamp
        updated_at (DateTimeField) : Object updation timestamp
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.CASCADE)
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    stock_adjustment_date = models.DateTimeField()  
    ADJUSTMENT_TYPE_CHOICES = (
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal'),
    )
    adjustment_type = models.CharField(max_length=8, choices=ADJUSTMENT_TYPE_CHOICES, blank=True, null=True)
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    business_location = models.ForeignKey(LocationModel, on_delete=models.PROTECT)
    total_amount_recovered = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

class StockTransferModel(models.Model):
    """
    Models to store stock transfer

    Attributes:
        merchant (ForeignKey) : Foreign key field relationship with MerchantModel instance    
        ref_no (CharField) : Reference number
        stock_transfer_date(DateTimeField) : Timestamp of stock transfer
        location_from (ForeignKey) : Foreign key field relationship with LocationModel instance
        location_to (ForeignKey) : Foreign key field relationship with LocationModel instance
        product_id (ForeignKey) : Foreign key field relationship with ProductModel instance
        shipping_details (CharField) : Shipping details
        shipping_charges (DecimalField) : Shipping charges
        additional_notes (TextField) : Additional note
        created_at (DateTimeField) : Object creation timestamp
        updated_at (DateTimeField) : Object updation timestamp
    """
    merchant = models.ForeignKey(MerchantModel, on_delete=models.CASCADE)
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    stock_transfer_date = models.DateTimeField()  
    location_from = models.ForeignKey(LocationModel, on_delete=models.PROTECT, related_name='location_from')
    location_to = models.ForeignKey(LocationModel, on_delete=models.PROTECT, related_name='location_to')
    product = models.ForeignKey(ProductModel, on_delete=models.PROTECT)
    shipping_details = models.CharField(max_length=191, blank=True, null=True)
    shipping_charges = models.DecimalField(max_digits=20, decimal_places=2)
    additional_notes = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

class ExpenseModel(models.Model):    
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    business_location = models.ForeignKey(LocationModel, on_delete=models.PROTECT)
    expense_category = models.ForeignKey(ExpenseCategoriesModel, on_delete=models.PROTECT)
    expense_for = models.ForeignKey(UserModel, on_delete=models.PROTECT, null=True)   
    ref_no = models.CharField(max_length=191, blank=True, null=True)
    expense_date = models.DateTimeField()
    
    PAYMENT_STATUS_CHOICES = (
        ('paid', 'Paid'),
        ('due', 'Due'),
    )
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)         
    total_amount = models.DecimalField(max_digits=20, decimal_places=2)
    expense_note = models.TextField(blank=True, null=True)

class UnitsModel(models.Model):
    merchant = models.ForeignKey(MerchantModel, on_delete=models.PROTECT)
    name = models.CharField(max_length=10)
    short_name = models.CharField(max_length=7)

    UNITS_CHOICES = (
        ('yes', 'Yes'),
        ('no', 'No'),
    )
    allow_decimal = models.CharField(max_length=10, choices=UNITS_CHOICES)



#######################################################################################################################################





class Orderproduct(models.Model):
    user = models.ForeignKey(UserModel,
                             on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name}"

    def get_total_product_price(self):
        return self.quantity * self.product.product_price

    def get_total_discount_product_price(self):
        return self.quantity * self.product.discount_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_total_discount_product_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_product_price()
        return self.get_total_product_price()



class Order(models.Model):
    user = models.ForeignKey(UserModel,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20)
    products = models.ManyToManyField(Orderproduct)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    detail = models.CharField(max_length=100)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey(
        'BillingAddress', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'BillingAddress', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'PaymentModel', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. product added to cart
    2. Adding a BillingAddress
    (Failed Checkout)
    3. Payment
    4. Being delivered
    5. Received
    6. Refunds
    '''

    def __str__(self):
        return self.user.email

    def get_total(self):
        total = 0
        for order_product in self.products.all():
            total += order_product.get_final_price()
        if self.coupon:
            total /= self.coupon.amount
        return total


class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name_plural = 'BillingAddresses'

class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"

