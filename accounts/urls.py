from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views
from .views import ProfileDetailView, ProfileUpdateView

urlpatterns = [
    path('profile/', ProfileDetailView.as_view(template_name = "account/profile_detail.html"), name='profile'),
    path('profile_update/', ProfileUpdateView.as_view(template_name = "account/profile_update.html"), name='profile_update'),
    path('profile_delete/', ProfileUpdateView.as_view(template_name = "account/profile_delete.html"), name='profile_delete')


]