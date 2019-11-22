"""web_application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib import admin, auth
from django.urls import path
from django.urls import include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from identify import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('trending', views.trending, name='trending'),
    # AUTH
    path('signup', views.SignUp.as_view(), name='signup'),
    path('login', auth_views.LoginView.as_view(), name='login'),
    path('logout', auth_views.LogoutView.as_view(), name='logout'),
    # channel
    path('channel/create', views.CreateChannel.as_view(), name='create_channel'),
    path('channel/<int:pk>', views.DetailChannel.as_view(), name='detail_channel'),
    path('channel/<int:pk>/update', views.UpdateChannel.as_view(), name='update_channel'),
    path('channel/<int:pk>/delete', views.DeleteChannel.as_view(), name='delete_channel'),
    # Video
    path('channel/<int:pk>/addvideo', views.add_video, name='add_video'),
    path('video/<int:pk>/delete', views.DeleteVideo.as_view(), name='delete_video'),
    # path('video/<int:pk>/delete1', views.DeleteVideo.as_view(), name='delete_video1'),
    # path('video/<int:pk>', views.DetailVideo.as_view(), name='detail_video'),
    path('video/<int:pk>', views.DetailVideoRender, name='detail_video'),
]





urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)