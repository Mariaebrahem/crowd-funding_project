from allauth.account.views import SignupView as _SignupView, LoginView as _LoginView, LogoutView as _LogoutView
from django.shortcuts import render, redirect

from .forms import SignupForm
class LoginView(_LoginView):
    template_name = "account/login.html"

class SignupView(_SignupView):
    template_name = "account/signup.html"
    pass

def forgotpassword(request):
    return render(request,'account/forgotpassword.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'account/signup.html', {'form': form})
    






