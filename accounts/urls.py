from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    path('signup/',views.SignupView.as_view(),name='signup'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('register/',views.SignupView.as_view()),
    path('forgotpassword/',views.forgotpassword,name='forgotpassword'),
    path('reset_password/', auth_views. PasswordResetView.as_view(), name="reset_password"),
    path('reset_password_sent/', auth_views. PasswordResetDoneView.as_view(), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views. PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views. PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path('change_password/', auth_views.PasswordChangeView.as_view(), name="password_change"),
    path('change_password_done/', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),


]