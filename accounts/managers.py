from django.contrib.auth.models import UserManager as _UserManager

class UserManager(_UserManager):
    def create_user(
        self, email, first_name=None, last_name=None, phone_number=None, password=None
    ):
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, first_name, last_name, phone_number, password):
        user = self.create_user(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user