import os
from django.db import models
from django.contrib.auth.models import User,Group
from django_countries.fields import CountryField

class UserDetails(models.Model):
    user = models.OneToOneField(User)
    key = models.TextField()

class CompanyDetails(models.Model):
    user = models.OneToOneField(User)
    company_name = models.CharField(max_length=30)
    company_phone = models.CharField(max_length=30)
    company_location = models.CharField(max_length=30)
    company_country = CountryField(blank_label='(Select Country)')#Look at django countries for choices


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

class ReportPermissions(models.Model):
    report = models.OneToOneField(Report,on_delete=models.CASCADE,
        related_name='permissions')
    allowed_users = models.ManyToManyField(User, blank=True)
    allowed_groups = models.ManyToManyField(Group, blank=True)


def generate_file_path(instance, filename):
    return os.path.join("reportFiles", instance.title.replace(" ",""), filename.replace(" ",""))

class File(models.Model):
    report = models.ForeignKey(Report)
    title = models.CharField(max_length=30)
    upload_date = models.DateTimeField(auto_now_add=True,auto_now=False)
    is_encrypted = models.BooleanField()
    upload = models.FileField(upload_to=generate_file_path)

    def filename(self):
        return os.path.basename(self.file.name)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver")
    subject = models.CharField(max_length=50)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True,auto_now=False)
    opened = models.BooleanField()
    encrypt = models.BooleanField()
    static_encrypt = models.BooleanField()

