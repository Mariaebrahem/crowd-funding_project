from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
class MyAccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        url = reverse("landing")
        return url
        