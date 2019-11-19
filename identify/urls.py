from django.urls import path
from django.urls import include
from django.views.generic.base import TemplateView
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.conf import settings
# from identify import views as i_views
from . import views


urlpatterns = [

]


urlpatterns += [   
	# path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('input/', views.inputURL, name='input_url'),
    # path('login/', views.userlogin, name='userlogin'),
    # path('logout/', views.userlogout, name='userlogout'),
    # path('signup/', views.signup, name='signup'),
    path('history/', views.history, name='history'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)