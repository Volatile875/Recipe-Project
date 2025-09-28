"""
URL configuration for vege project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))    from myapp.views import lag, first, delete_recepie

"""
from django.contrib import admin
from django.urls import path
from myapp.views import lag
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from django.conf.urls.static import static
from myapp.views import delete_recepie, login_page, register_view,logout_page
from myapp.views import update_recepie


urlpatterns = [
     # This handles the root path
    path('', lag, name='lag'),
    
    path('delete-recepie/<int:id>/', delete_recepie , name='delete-recepie'),
    path('update-recepie/<int:id>/', update_recepie , name='update-recepie'),
    path('admin/', admin.site.urls),
    path('login/', login_page , name='login_page'),
    path('register/', register_view, name='register'),
    path("logout/", logout_page, name="logout"),
    # end of urlpatterns
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                    document_root=settings.MEDIA_ROOT)

