from django.urls import path
from django.urls import include
from django.views.generic.base import TemplateView
from . import views


urlpatterns = [

]


urlpatterns += [   
	path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('input/', views.inputURL, name='input_url'),
    path('login/', views.userlogin, name='userlogin'),
    path('logout/', views.userlogout, name='userlogout'),
    path('signup/', views.signup, name='signup'),
    path('history/', views.history, name='history')
]