
from django.db import models
from django.contrib.auth.models import User

class UserDetails(models.Model):
    user = models.OneToOneField(User)
    user_types = (
        ('I', 'Investor'),
        ('C','Company'),
    )
    type = models.CharField(
        max_length=2,
        choices=user_types,
        default='I',
    )
    @classmethod
    def create(cls, user, type):
        details = cls(user = user, type = type)
        return details

class CompanyDetails(models.Model):
    user = models.OneToOneField(User)
    company_name = models.CharField(max_length=30)
    company_phone = models.CharField(max_length=30)
    company_location = models.CharField(max_length=30)
    company_country = models.CharField(max_length=30)#Look at django countries for choices


