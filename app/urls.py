from django.urls import path, include
from app.views import (
    IndexView,
    CreateAccountView,
    LoginView,
    GenerateOTPView,
    OTPVerificationView,
    RegisterView,
    RecordPlayView,
    SetupVoiceView,
    TapListenView,
    VerifyProceedView,
    ProvidersView,
    MobileRechargeView,
    BillFoundView,
    DTHRechargeView,
    MobilePostpaidView,
    LandlineView,
    ElectricityView,
    WaterView,
    PipedgasView,
    FASTagView,
    LoanRepaymentView,
    BroadbandView,
    LpgGasView,
    InsurancePaymentView,
    SubscriptionView,
    SendMoneyView,
    SendVoiceMoneyView,
    RequestMoneyView, 
    RequestVoiceMoneyView,
    VoiceAuthenticationView,
    ScanPayView,
    DashboardView,
    SettingView,
    PersonalInformationView,
    NotificationEmailsView,
    PrivacySecurityView,
    AboutView,
    HelpFeedbackView,
    EditMobileNumberView,
    EditLanguageView,
    DataPersonalizationView,
    BlockedPeopleView,
    HowPeopleView,
    TermsServicesView,
    PrivacyPolicyView,
    SoftwareLicenseView,
    UserProfileView,
    DrawNumberGameView,
    GetOTPFromVoiceView,
    LogoutView,
    GetNumberFromVoiceView,
    GetGameResultSuccessView,
    GetGameResultFailureView,
    AskToPlayGameView,
    PaymentSuccessfulView,
    InvoiceGeneratorView,
    DisplayInvoiceView,
    RequestSearchUserView,
    RequestSuccessView,
    RedirectView,
    RazorpayPaymentSuccessfulView,
    RazorpayPaymentUnsuccessfulView,
    RazorpayPaymentHandlerView,
    PayWithCCAvenueView,
    CCAvenueResponseView,
    CreateMerchantAccountView,
    MerchantRegistrationView,
    MerchantLoginView,
    MerchantDashboardView,
    ListProductsView,
    AddProductView,
    UpdateProductView,
    DeleteProductView,
    load_states,
    load_cities,
    ListProductVariationView,
    AddProductVariationView,
    DeleteProductVariationView,
    UpdateProductVariationsView,
    ListPurchaseView,
    AddPurchaseView,
    AddSaleView,
    AddSellReturnView,
    AddStockTransferView,
    AddStockAdjustmentsView,
    DeletePurchaseView,
    DeleteSellReturnView,
    DeleteSaleView,
    DeleteStockTransferView,
    DeleteStockAdjustmentView,
    AddExpenseView,
    DeleteExpenseView,
    AddExpenseCategoryView,
    DeleteExpenseCategoryView,
    AddTaxRatesView,
    UpdateTaxRatesView,
    DeleteTaxRatesView,
    AddBrandsView,
    UpdateBrandsView,
    DeleteBrandsView,
    AddUnitsView,
    UpdateUnitsView,
    DeleteUnitsView,
    AddTaxGroupView,
    DeleteTaxGroupView,
    OrderSummaryView,




    AboutUsView,
    ShopView,
    retrieveData,
    retrieveOneData,
    CheckoutView,
    AddCouponView,
    PaymentView,
    search,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    bycategoryelectronics,
    bycategorybooks,

)
from app import views


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('create_account/', CreateAccountView.as_view(), name='create_account'),
    path('login/', LoginView.as_view(), name='paybill_login'),   
    path('otp/', GenerateOTPView.as_view(), name='otp'),
    path('otp/payment/', GenerateOTPView.as_view(), name='otp_payment'),
    path('otp_verification/', OTPVerificationView.as_view(), name='otp_verification'),   
    path('otp_payment_verification/', OTPVerificationView.as_view(), name='otp_payment_verification'),   
    path('otp_voice_verification/', GetOTPFromVoiceView.as_view(), name='otp_voice_verification'),    
    path('register/', RegisterView.as_view(), name='register'),
    path('record_play/', RecordPlayView.as_view(), name='record_play'),
    path('setup_voice/', SetupVoiceView.as_view(), name='setup_voice'),
    path('tap_listen/', TapListenView.as_view(), name='tap_listen'),
    path('verify_proceed/', VerifyProceedView.as_view(), name='verify_proceed'),
    path('aboutus/', AboutUsView.as_view(), name='aboutus'),
    path('providers/', ProvidersView.as_view(), name='providers'),
    path('providers/mobile_recharge/', MobileRechargeView.as_view(), name='mobile_recharge'),
    path('providers/bill_found/', BillFoundView.as_view(), name='bill_found'),
    path('providers/dth_recharge/', DTHRechargeView.as_view(), name='dth_recharge'),
    path('providers/mobile_postpaid/', MobilePostpaidView.as_view(), name='mobile_postpaid'),  
    path('providers/landline/', LandlineView.as_view(), name='landline'),  
    path('providers/electricity/', ElectricityView.as_view(), name='electricity'),  
    path('providers/water/', WaterView.as_view(), name='water'),  
    path('providers/piped_gas/', PipedgasView.as_view(), name='piped_gas'),  
    path('providers/FASTag/', FASTagView.as_view(), name='fastag'),  
    path('providers/loan_repayment/', LoanRepaymentView.as_view(), name='loan_repayment'),  
    path('providers/broadband/', BroadbandView.as_view(), name='broadband'),  
    path('providers/lpg_gas/', LpgGasView.as_view(), name='lpg_gas'),
    path('providers/insurance_payment/', InsurancePaymentView.as_view(), name='insurance_payment'),
    path('providers/subscription/', SubscriptionView.as_view(), name='subscription'),





    path('shop/', ShopView.as_view(), name='shop'),
    path('shopdetail/', retrieveData.as_view(), name='shop'), 
    path('shopdetail/<slug>/', retrieveOneData.as_view(), name='shopdetail'),
    path('search/', views.search, name='search'),
    path('category/books/', views.bycategorybooks, name='bycategorybooks'),
    path('category/electronics/', views.bycategoryelectronics, name='bycategoryelectronics'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('remove-item-from-cart/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-cart'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('add_coupon/', AddCouponView.as_view(), name='add-coupon'),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),











    path('send_money/', SendMoneyView.as_view(), name='paybills_send_money'),
    path('send_voice_money/', SendVoiceMoneyView.as_view(), name='send_voice_money'),
    path('request_money/<int:user_id>', RequestMoneyView.as_view(), name='request_money'),
    path('request_voice_money/', RequestVoiceMoneyView.as_view(), name='request_voice_money'),
    path('voice_authentication/', VoiceAuthenticationView.as_view(), name='voice_authentication'),
    path('scan_pay/', ScanPayView.as_view(), name='scan_pay'), 
    path('dashboard/', DashboardView.as_view(), name='dashboard'), 
    path('setting/', SettingView.as_view(), name='setting'), 
    path('personal_info/', PersonalInformationView.as_view(), name='personal_info'), 
    path('notification_email/', NotificationEmailsView.as_view(), name='notification_email'), 
    path('privacy_security/', PrivacySecurityView.as_view(), name='privacy_security'), 
    path('about/', AboutView.as_view(), name='about'), 
    path('help_feedback/', HelpFeedbackView.as_view(), name='help_feedback'), 
    path('personal_info/edit_mobile_number/', EditMobileNumberView.as_view(), name='edit_mobile_number'), 
    path('personal_info/edit_language/', EditLanguageView.as_view(), name='edit_language'),      
    path('privacy_security/data_personalization/', DataPersonalizationView.as_view(), name='data_personalization'),      
    path('privacy_security/blocked_people/', BlockedPeopleView.as_view(), name='blocked_people'),      
    path('privacy_security/how_people_find_you/', HowPeopleView.as_view(), name='how_people_find_you'),      
    path('about/terms_services/', TermsServicesView.as_view(), name='terms_services'),      
    path('about/privacy_policy/', PrivacyPolicyView.as_view(), name='privacy_policy'),      
    path('about/software_license/', SoftwareLicenseView.as_view(), name='software_license'), 
    path('dashboard/user_profile/', UserProfileView.as_view(), name='user_profile'),      
    path('draw_number_game/', DrawNumberGameView.as_view(), name='draw_number_game'),      
    path('get_number_game/', GetNumberFromVoiceView.as_view(), name='get_number_game'),      
    path('logout/', LogoutView.as_view(), name='logout'),
    path('get_game_result_success/', GetGameResultSuccessView.as_view(), name='get_game_result_success'),
    path('get_game_result_failure/', GetGameResultFailureView.as_view(), name='get_game_result_failure'),
    path('ask_to_play_game/', AskToPlayGameView.as_view(), name='ask_to_play_game'),
    path('payment_successful/', PaymentSuccessfulView.as_view(), name='payment_successful'),    
    path('get_invoice/', InvoiceGeneratorView.as_view(), name='get_invoice'),
    path('display_invoice/<int:bill_id>/', DisplayInvoiceView.as_view(), name='display_invoice'),
    path('search_user/', RequestSearchUserView.as_view(), name='search_user'),
    path('request_successful/', RequestSuccessView.as_view(), name='request_successful'),    
    path('send_money/', SendMoneyView.as_view(), name='paybills_send_money'), 
    path('send_money/razorpay_payment_handler/', RazorpayPaymentHandlerView.as_view(), name='razorpay_payment_handler'), 
    path('razorpay_payment_successful/', RazorpayPaymentSuccessfulView.as_view(), name='razorpay_payment_successful'),
    path('razorpay_payment_unsuccessful/', RazorpayPaymentUnsuccessfulView.as_view(), name='razorpay_payment_unsuccessful'),
    #path('razorpay_payment/',PayWithRazorpayView.as_view(), name='razorpay_payment'),
    path('ccavenue_payment/',PayWithCCAvenueView.as_view(), name='ccavenue_payment'),
    path('ccavenue_response/', CCAvenueResponseView.as_view(), name='ccavenue_response'),
    #path('create_merchant_account/', CreateMerchantAccountView.as_view(), name='create_merchant_account'),
    path('create_merchant_account/', MerchantRegistrationView.as_view(), name='create_merchant_account'),
    path('merchant_registration/', MerchantRegistrationView.as_view(), name='merchant_registration'),
    path('merchant_login/', MerchantLoginView.as_view(), name='merchant_login'),
    path('merchant_dashboard/', MerchantDashboardView.as_view(), name='merchant_dashboard'),
    path('merchant_dashboard/products/', ListProductsView.as_view(), name='products'),
    path('merchant_dashboard/add_product/', AddProductView.as_view(), name='add_product'),
    path('merchant_dashboard/products/<int:pk>/edit/', UpdateProductView.as_view(), name='update_product'),
    path('merchant_dashboard/products/<int:pk>/delete/', DeleteProductView.as_view(), name='remove_product'),
    path('load_states/', load_states, name="load_states"),
    path('load_cities/', load_cities, name="load_cities"),
    
    path('merchant_dashboard/list_purchase/', ListPurchaseView.as_view(), name='list_purchase'),
    path('merchant_dashboard/add_purchase/', AddPurchaseView.as_view(), name='add_purchase'),
    path('merchant_dashboard/purchase/<int:pk>/delete/', DeletePurchaseView.as_view(), name='remove_purchase'),    

    path('merchant_dashboard/add_sale/', AddSaleView.as_view(), name='add_sale'),
    path('merchant_dashboard/sale/<int:pk>/delete/', DeleteSaleView.as_view(), name='remove_sale'),

    path('merchant_dashboard/add_sell_return/', AddSellReturnView.as_view(), name='add_sell_return'),
    path('merchant_dashboard/sell_return/<int:pk>/delete/', DeleteSellReturnView.as_view(), name='remove_sell_return'),

    path('merchant_dashboard/add_stock_transfer/', AddStockTransferView.as_view(), name='add_stock_transfer'),
    path('merchant_dashboard/stock_transfer/<int:pk>/delete/', DeleteStockTransferView.as_view(), name='remove_stock_transfer'),

    path('merchant_dashboard/add_stock_adjustment/', AddStockAdjustmentsView.as_view(), name='add_stock_adjustment'),
    path('merchant_dashboard/stock_adjustment/<int:pk>/delete/', DeleteStockAdjustmentView.as_view(), name='remove_stock_adjustment'),
    
    path('merchant_dashboard/product_variations/', ListProductVariationView.as_view(), name='list_product_variation'),    
    path('merchant_dashboard/add_product_variation/', AddProductVariationView.as_view(), name='add_product_variation'),
    path('merchant_dashboard/product_variations/<int:pk>/edit/', UpdateProductVariationsView.as_view(), name='update_product_variation'),
    path('merchant_dashboard/product_variations/<int:pk>/delete/', DeleteProductVariationView.as_view(), name='remove_product_variation'),

    path('merchant_dashboard/add_expense/', AddExpenseView.as_view(), name='add_expense'),
    path('merchant_dashboard/expense/<int:pk>/delete/', DeleteExpenseView.as_view(), name='remove_expense'),

    path('merchant_dashboard/add_expense_category/', AddExpenseCategoryView.as_view(), name='add_expense_category'),
    path('merchant_dashboard/expense_category/<int:pk>/delete/', DeleteExpenseCategoryView.as_view(), name='remove_expense_category'),
    
    path('merchant_dashboard/add_tax_rates/', AddTaxRatesView.as_view(), name='add_tax_rates'),
    path('merchant_dashboard/tax_rates/<int:pk>/delete/', DeleteTaxRatesView.as_view(), name='remove_tax_rates'),
    
    path('merchant_dashboard/add_brands/', AddBrandsView.as_view(), name='add_brands'),
    path('merchant_dashboard/brands/<int:pk>/delete/', DeleteBrandsView.as_view(), name='remove_brands'),
    
    path('merchant_dashboard/add_units/', AddUnitsView.as_view(), name='add_units'),
    path('merchant_dashboard/units/<int:pk>/delete/', DeleteUnitsView.as_view(), name='remove_units'),

    path('merchant_dashboard/add_tax_group/', AddTaxGroupView.as_view(), name='add_tax_group'),
    path('merchant_dashboard/tax_group/<int:pk>/delete/', DeleteTaxGroupView.as_view(), name='remove_tax_group'),
    
    path('<slug:short>/', RedirectView.as_view(), name="url_shortner"),








    
]  