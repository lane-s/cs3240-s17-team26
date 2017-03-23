# importing forms
from django.forms import ModelForm, Form, CharField, PasswordInput
from django.contrib.auth.models import User
from Fintech.models import UserDetails,CompanyDetails


# creating our forms
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name', 'email')
        widgets = {
            'password': PasswordInput(),
        }

class UserDetailForm(ModelForm):
    class Meta:
        model = UserDetails
        fields = ('type',)

class CompanyForm(ModelForm):
    class Meta:
        model = CompanyDetails
        fields = ('company_name','company_phone','company_location','company_country')

class LoginForm(Form):
	username = CharField(label='Username', max_length=50)
	password = CharField(label='Password', max_length=50, widget=PasswordInput())
