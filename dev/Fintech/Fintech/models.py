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


class Report(models.Model):
    owner = models.ForeignKey(User)
    title = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)
    company_name = models.CharField(max_length=30)
    company_ceo = models.CharField(max_length=30)
    company_phone = models.CharField(max_length=30)
    company_location = models.CharField(max_length=30)
    company_country = models.CharField(max_length=30)
    sector = models.CharField(max_length=30)
    industry = models.CharField(max_length=30)
    current_projects = models.TextField()
    is_private = models.BooleanField()
    has_attachments = models.BooleanField()


class File(models.Model):
    report = models.ForeignKey(Report)
    title = models.CharField(max_length=30)
    upload_date = models.DateTimeField(auto_now_add=True,auto_now=False)
    is_encrypted = models.BooleanField()
    upload = models.FileField(upload_to='reports/')
