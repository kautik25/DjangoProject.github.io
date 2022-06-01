"""paybills URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
"""
from app.views import (
    UserLogin,
    UserLogout,
    UserRegistration,
    UserResetPwd,
)
"""

urlpatterns = [
    #path('', RedirectView.as_view(pattern_name='index')),

    #path('admin/', admin.site.urls),
    path('paybills_admin/', admin.site.urls),
    #path('login/', UserLogin.as_view(template_name='app/login.html'), name='user_login'),
    #path('logout/', UserLogout.as_view(), name='user_logout'),
    #path('registration/', UserRegistration.as_view(), name='registration'),
    #path('reset-password/', UserResetPwd.as_view(), name='reset_password'),
    #path('paypal/', include('paypal.standard.ipn.urls')),    
    # path('', include('app.urls')),
    path('', include(('app.urls', 'app'), namespace='app')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
