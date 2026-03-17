"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from announcements.views import (
    register, user_login, user_logout,   # ← новые
    HomeView, create_announcement,
    AnnouncementDetailView, add_response,
    accept_response, reject_response, profile_view, delete_announcement,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', HomeView.as_view(), name='home'),
    
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),          # ← здесь
    path('logout/', user_logout, name='logout'),       # ← здесь
    
    path('create/', create_announcement, name='create_announcement'),
    path('announcement/<int:pk>/', AnnouncementDetailView.as_view(), name='announcement_detail'),
    path('announcement/<int:pk>/respond/', add_response, name='add_response'),
    path('response/<int:response_id>/accept/', accept_response, name='accept_response'),
    path('response/<int:response_id>/reject/', reject_response, name='reject_response'),
    path('profile/', profile_view, name='profile'),
    path('announcement/<int:pk>/delete/', delete_announcement, name='delete_announcement'),
]
