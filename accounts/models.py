from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import RegexValidator
from django.db import models
from accounts.managers import UserManager


class Account(AbstractUser):
    class CountryChoices(models.TextChoices):
        EGYPT = "EG", "Egypt"
        USA = "US", "United States"
        UK = "UK", "United Kingdom"

    username = models.CharField(max_length=150, blank=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = PhoneNumberField(blank=False, region="EG")
    profile_picture = models.ImageField(blank=True, upload_to="profile_pics/")

    birthdate = models.DateField(null=True, blank=True)
    facebook_profile = models.URLField(null=True, blank=True)
    country = models.CharField(choices=CountryChoices.choices, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number"]
    objects = UserManager()

    def __str__(self):
        return f"{self.email}"
