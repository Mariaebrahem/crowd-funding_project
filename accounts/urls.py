from django.urls import path
from accounts import views
from allauth.account import views as allauth_views

urlpatterns = [
    path(
        "profile/",
        views.ProfileDetailView.as_view(template_name="account/profile_detail.html"),
        name="profile",
    ),
    path(
        "profile_update/",
        views.ProfileUpdateView.as_view(template_name="account/profile_update.html"),
        name="profile_update",
    ),
    path(
        "profile_delete/",
        views.ProfileDeleteView.as_view(template_name="account/profile_delete.html"),
        name="profile_delete",
    ),
]
