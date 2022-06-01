from .models import (
    UrlShortnerModel,
    MerchantModel,
)
import pyshorteners
import razorpay
from django.conf import settings

def shorten_url(url):
    try:
        obj = UrlShortnerModel.objects.get(long_url=url)  
        slug = obj.short_id      
        print("slug exists")
    except Exception as e:
        # slug = ''.join(random.choice(string.ascii_letters)
        #             for x in range(10))
        s = pyshorteners.Shortener()
        slug = s.tinyurl.short(url)
        new_url = UrlShortnerModel(long_url=url, short_id=slug)
        new_url.save()
        print("slug added:", slug)
    return slug

def create_razorpay_client():
    # authorize razorpay client with API Keys.
    razorpay_client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
    return razorpay_client 

def get_host_name(request):
    print("host", request.META.get('HTTP_HOST'))
    return request.META.get('HTTP_HOST')

def get_subdomain(request):
    hostname = get_host_name(request)
    subdomain = hostname.split('.')[0]
    print("subdomain", subdomain)
    return subdomain