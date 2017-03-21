# importing forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from Fintech.models import UserDetails,CompanyDetails


# creating our forms
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username','password','first_name','last_name', 'email')

class UserDetailForm(ModelForm):
    class Meta:
        model = UserDetails
        fields = ('type','bio')

class CompanyForm(ModelForm):
    class Meta:
        model = CompanyDetails
        fields = ('company_name','company_phone','company_location','company_country')
