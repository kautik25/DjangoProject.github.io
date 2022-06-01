from app.models import (
    CCAvenueSurchargeModel,
    RazorpaySurchargeModel,
    )

try:
    ccavenue_surcharge_list = [
        ('credit_card_domestic', 2),
        ('debit_card_domestic', 2),
        ('netbanking', 2),
        ('wallet', 2),
        ('upi', 2),
        ('credit_card_commercial', 3),        
        ('credit_card_international', 3),
        ('debit_card_international', 3),
        ('american_express', 4),
    ]
    if not CCAvenueSurchargeModel.objects.all():
        for record in ccavenue_surcharge_list:
            c = CCAvenueSurchargeModel.objects.create(payment_mode = record[0], surcharge = record[1])
            c.save() 
        print("Records inserted in CCAvenueSurchargeModel")   

    else:
        print("Surcharge information for CCAvenue exists")

    razorpay_surcharge_list = [
        ('credit_card_domestic', 2),
        ('debit_card_domestic', 2),
        ('netbanking', 2),
        ('wallet', 2),
        ('upi', 2),
        ('credit_card_commercial', 3),        
        ('credit_card_international', 3),
        ('debit_card_international', 3),
    ]
    if not RazorpaySurchargeModel.objects.all():
        for record in razorpay_surcharge_list:
            r1 = RazorpaySurchargeModel.objects.create(payment_mode = record[0], surcharge = record[1])
            r1.save()  
        print("Records inserted in RazorpaySurchargeModel")

    else:
        print("Surcharge information for Razorpay exists")
        
except Exception as e:
    print("Exception:",str(e))