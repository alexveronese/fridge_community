"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from config.views import *
from initcmds import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path("register/", UserCreateView.as_view(), name="register"),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("registerop/",OperatorCreateView.as_view(), name="registerop"),

    path('', include('main.urls')),
]
# Enable if we need to access media
# The following works only if DEBUG==True. We use UNPREFIXED_MEDIA_URL, to make it work from Apache
# when running from a subfolder which provides SCRIPT_NAME to the WSGI application
urlpatterns += static(settings.UNPREFIXED_MEDIA_URL, document_root=settings.MEDIA_ROOT)



#erase_db()
#init_db()
#init_grousp()