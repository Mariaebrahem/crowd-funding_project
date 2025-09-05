from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        homepage_url = reverse("landing")
        return homepage_url
    
    def get_logout_redirect_url(self, request):
        login_url = reverse("account_login")
        return login_url