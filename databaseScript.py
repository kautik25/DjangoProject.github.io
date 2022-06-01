from app.models import (
    UserModel,
    SampleStringModel,
    )

try:
    if UserModel.objects.all():
        user_queryset = UserModel.objects.filter(email = "admin@gmail.com")
        if not user_queryset:
            UserModel.objects.create_superuser("admin@gmail.com", "admin", "admin", "admin123", True)
            print("Created super user 'admin'")
        else:
            print("Super user 'admin' exists")

    else:
        UserModel.objects.create_superuser("admin@gmail.com", "admin", "admin", "admin123", True)
        print("Created super user 'admin'")

    queryset = SampleStringModel.objects.all()
    if not queryset:
        s1 = SampleStringModel.objects.create(sample_string = "I'm {your name} and this is my voice")
        s1.save()
        print("Sample string 1 saved")
        s2 = SampleStringModel.objects.create(sample_string = "Hey Paybills, pay my bill")
        s2.save()
        print("Sample string 2 saved")
        s3 = SampleStringModel.objects.create(sample_string = "Paybills, what is my balance ?")
        s3.save()
        print("Sample string 3 saved")
    else:
        print("Sample strings already exist")
        
except Exception as e:
    print("Exception:",str(e))