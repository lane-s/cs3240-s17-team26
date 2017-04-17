# importing forms
from django.forms import ModelForm, Form, CharField, PasswordInput
from django import forms
from django.contrib.auth.models import User, Group
from Fintech.models import UserDetails, CompanyDetails, Report, ReportPermissions, File, Message


# creating our forms
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        widgets = {
            'password': PasswordInput(),
        }


class CompanyForm(ModelForm):
    class Meta:
        model = CompanyDetails
        fields = ('company_name', 'company_phone', 'company_location', 'company_country')


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ('name',)


class GroupAddUser(Form):
    username = CharField(label='Username', max_length=50)


class LoginForm(Form):
    username = CharField(label='Username', max_length=50)
    password = CharField(label='Password', max_length=50, widget=PasswordInput())


class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ('title', 'company_name', 'company_ceo', 'company_phone', 'company_location', 'company_country',
                  'sector', 'industry', 'current_projects', 'is_private', 'has_attachments')

class ReportPermissionsForm(ModelForm):
    class Meta:
        model = ReportPermissions
        fields = ('allowed_users','allowed_groups')

    def __init__ (self, *args, **kwargs):
        super(ReportPermissionsForm, self).__init__(*args, **kwargs)
        self.fields["allowed_users"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["allowed_users"].help_text = ""
        self.fields["allowed_users"].queryset = User.objects.all()
        self.fields["allowed_groups"].widget = forms.widgets.CheckboxSelectMultiple()
        self.fields["allowed_groups"].help_text = ""
        self.fields["allowed_groups"].queryset = Group.objects.all()


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ('title', 'is_encrypted', 'upload')

class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ('receiver','subject','content')


