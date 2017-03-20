from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    type_choices = (
                    ('SM', 'Site Manager'),
                    ('C', 'Company'),
                    ('I', 'Investor'),
                    )
                    user_type = models.CharField(max_length=2,
                                                 choices=type_choices,
                                                 default='I')

class UserDetails(model.Model):
    type = models.OneToOneField('CustomUser')
    extra_info = models.CharField(max_length=200)
