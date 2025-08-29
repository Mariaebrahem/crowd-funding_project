from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.db import models


class Account(AbstractUser):
    phone_number = PhoneNumberField(blank=True)
    profile_picture = models.ImageField(blank=True, upload_to="profile_pics/")

    def __str__(self):
        return self.username
