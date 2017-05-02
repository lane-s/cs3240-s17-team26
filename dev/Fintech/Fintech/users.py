from django.shortcuts import redirect, render, get_object_or_404

from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Q
from django.forms import ModelForm, Form, CharField, PasswordInput

from Crypto.PublicKey import RSA
from Crypto import Random

from Fintech.models import UserDetails, CompanyDetails, Report, Message
from Fintech.decorators import request_passes_test
from Crypto.PublicKey import RSA
from Crypto import Random


#Forms
class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password', 'first_name', 'last_name', 'email')
        widgets = {
            'password': PasswordInput(),
        }

class UserSettings(ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','email')

class CompanySettings(ModelForm):
    class Meta:
        model = CompanyDetails
        fields = ('company_phone','company_location','industry','sector')

class UserDetailForm(ModelForm):
    class Meta:
        model = UserDetails
        exclude = ('user','key')

class CompanyForm(ModelForm):
    class Meta:
        model = CompanyDetails
        fields = ('company_name', 'company_ceo', 'company_phone', 'company_location', 'company_country')



class LoginForm(Form):
    username = CharField(label='Username', max_length=50)
    password = CharField(label='Password', max_length=50, widget=PasswordInput())

#Helper functions
def super_user(request):
    return {'super_user': request.user.is_superuser}


def is_company_user(user):
    return True if CompanyDetails.objects.filter(user=user) else False


def is_site_manager(user):
    return True if user.groups.filter(name="Site Managers") else False


def is_suspended(user):
    return True if user.groups.filter(name="Suspended Users") else False


def suspended_test(request):
    passes = not is_suspended(request.user)
    if not passes:
        messages.error(request, "Your account has been suspended. Please contact a Site Manager")
    return passes


def user_context_processor(request):
    if request.user.is_authenticated:
        company_user = is_company_user(request.user)
        site_manager = is_site_manager(request.user)
        suspended_user = is_suspended(request.user)

        return {'logged_in': True, 'company_user': company_user, 'site_manager': site_manager,
                'suspended_user': suspended_user}
    else:
        return {'logged_in': False, 'company_user': False, 'site_manager': False, 'suspended_user': False}

#Views
def index(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    # This is wasteful, but it's what the TA is requiring us to do as far as I can tell
    if not Group.objects.filter(name="Site Managers"):
        Group.objects.create(name="Site Managers")

    managerGroup = Group.objects.get(name="Site Managers")

    if not Group.objects.filter(name="Suspended Users"):
        Group.objects.create(name="Suspended Users")

    if not User.objects.filter(username="manager"):
        User.objects.create_user(username="manager", password="passwordsosecure", email="noreply@lokahifintech.com")

    siteManager = User.objects.get(username="manager")

    if not siteManager.groups.filter(name="Site Managers"):
        siteManager.groups.add(managerGroup)

    if not request.user.is_authenticated or is_suspended(request.user):
        # If not logged in render splash
        return render(request, 'splash.html')
    else:
        has_messages = False
        message_list = Message.objects.filter(receiver=request.user)
        for m in message_list:
            if m.opened == False:
                has_messages = True
                break
        # Otherwise render report view
        if is_company_user(request.user):
            report_list = Report.objects.filter(owner=request.user)
        elif is_site_manager(request.user):
            report_list = Report.objects.all()
        else:
            groupPermissions = [g.reportpermissions_set.all() for g in request.user.groups.all()];

            report_list = Report.objects.filter(Q(is_private=False)
                                                | Q(permissions__in=request.user.reportpermissions_set.all())
                                                | Q(
                permissions__in=[item for sublist in groupPermissions for item in sublist]))
        return render(request, 'splash.html',
                      {'report_list': report_list, 'has_messages': has_messages, 'username': username})


def signupform(request):
    if request.method == 'POST':
        investor_user_form = UserForm(request.POST, prefix="investor_user_form")
        company_user_form = UserForm(request.POST, prefix="company_user_form")
        company_detail_form = CompanyForm(request.POST, prefix="company_detail_form")
        user_detail_form = UserDetailForm(request.POST)

        if investor_user_form.is_valid() or company_user_form.is_valid() and company_detail_form.is_valid():

            # Assign unique key to each user when they sign up
            key_length = 1024
            keypair = RSA.generate(key_length, Random.new().read).exportKey()

            if company_user_form.is_valid():

                user = company_user_form.save(commit=False)
                user.set_password(company_user_form.cleaned_data['password'])
                user.save()

                company_detail = company_detail_form.save(commit=False)
                company_detail.user = user
                company_detail.save()

                # assign user details to set encryption key
                user_details = user_detail_form.save(commit=False)
                user_details.user = User.objects.get(username=user.username)
                user_details.key = keypair
                user_details.save()

            else:
                user = investor_user_form.save(commit=False)
                user.set_password(investor_user_form.cleaned_data['password'])
                user.save()

                # assign user details to set encryption key
                user_details = user_detail_form.save(commit=False)
                user_details.user = User.objects.get(username=user.username)
                user_details.key = keypair
                user_details.save()

            return redirect('index')
    else:
        investor_user_form = UserForm(prefix="investor_user_form")
        company_user_form = UserForm(prefix="company_user_form")
        company_detail_form = CompanyForm(prefix="company_detail_form")

    return render(request, 'registration/signup.html',
                  {'investor_user_form': investor_user_form, 'company_user_form': company_user_form,
                   'company_detail_form': company_detail_form})




@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def settings(request):
    username = None
    if is_company_user(request.user):
        username = request.user
        has_messages = False
        message_list = Message.objects.filter(receiver=request.user)
        for m in message_list:
            if m.opened == False:
                has_messages = True
                break
        is_company = True

        if request.method == 'POST':

            user_settings = UserSettings(request.POST, instance = request.user)
            company_settings = CompanySettings(request.POST, instance = request.user)

            if user_settings.is_valid() and company_settings.is_valid():
                user_settings.save()
                company_settings.save()
                messages.success(request, 'Changes have been saved')


        else:
            user_settings = UserSettings(instance = request.user)
            company_settings = CompanySettings(instance = request.user)

        return render(request, 'registration/settings.html', {'user_settings':user_settings,'company_settings':company_settings,'is_company':is_company,'username':username,'has_messages':has_messages})

    else:
        username = request.user
        has_messages = False
        message_list = Message.objects.filter(receiver=request.user)
        for m in message_list:
            if m.opened == False:
                has_messages = True
                break
        is_company = False

        if request.method == 'POST':

            user_settings = UserSettings(request.POST, instance=request.user)

            if user_settings.is_valid():
                user_settings.save()
                messages.success(request, 'Changes have been saved')

        else:

            user_settings = UserSettings(instance=request.user)

        return render(request, 'registration/settings.html', {'user_settings':user_settings,'is_company':is_company,'username':username,'has_messages':has_messages})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password.html', {
        'form': form
    })