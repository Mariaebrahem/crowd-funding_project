import re
from django import forms
from allauth.account.forms import SignupForm as _SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django.core.exceptions import ValidationError
from .models import Account
from datetime import date, timedelta


from django.contrib.auth import get_user_model


class SignupForm(_SignupForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone_number = PhoneNumberField(region="EG", required=True)
    profile_picture = forms.ImageField(required=False)


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            "first_name",
            "last_name",
            "phone_number",
            "profile_picture",
            "birthdate",
            "facebook_profile",
            "country",
        ]
        widgets = {
            "birthdate": forms.DateInput(attrs={"type": "date"}),
            "profile_picture": forms.ClearableFileInput(attrs={"multiple": False}),
        }


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
            "birthdate",
            "facebook_profile",
            "country",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your first name"}
            ),
            "last_name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your last name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "Enter your email"}
            ),
            "phone_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your phone number",
                }
            ),
            "profile_picture": forms.FileInput(attrs={"class": "form-control"}),
            "birthdate": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "facebook_profile": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter your Facebook profile URL",
                }
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Enter your country"}
            ),
        }

    def validate_facebook_url(self, value):
        # regex to match Facebook URLs
        facebook_url_regex = r"^https?://(www\.)?facebook\.com/.+"

        if value and not re.match(facebook_url_regex, value):
            return False
        return True

    def clean_birthdate(self):
        birthdate = self.cleaned_data.get("birthdate")
        if birthdate:
            today = date.today()
            # check if birthdate is after today's date
            if birthdate > today:
                raise forms.ValidationError("Birthdate cannot be in the future.")
        return birthdate

    def clean_facebook_profile(self):
        facebook_profile = self.cleaned_data.get("facebook_profile")
        if facebook_profile:
            if not self.validate_facebook_url(facebook_profile):
                raise ValidationError("Invalid Facebook URL")
        return facebook_profile


class ProfileDeleteForm(forms.ModelForm):
    password = forms.CharField()
    
    class Meta:
        model = get_user_model()
        fields = ["password"]
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        if not self.user.check_password(self.cleaned_data.get('password')):
            raise forms.ValidationError("Incorrect password.")
        return super().clean()