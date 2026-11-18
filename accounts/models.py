from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=20, blank=True)
    is_organization = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=True)
    email_verification_code_hash = models.CharField(max_length=128, blank=True)
    email_verification_code_expires = models.DateTimeField(null=True, blank=True)
    password_reset_code_hash = models.CharField(max_length=128, blank=True)
    password_reset_code_expires = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username
