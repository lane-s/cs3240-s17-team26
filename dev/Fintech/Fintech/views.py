
from django.shortcuts import redirect, render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from Fintech.forms import UserForm, CompanyForm, LoginForm
from django.contrib.auth import views as auth_views
from Fintech.models import UserDetails

def index(request):
    #If not logged in render splash
    #Otherwise render report view
    return render(request,'splash.html')


def signupform(request):

    if request.method == 'POST':
        investor_user_form = UserForm(request.POST,prefix="investor_user_form")
        company_user_form = UserForm(request.POST,prefix="company_user_form")
        company_detail_form = CompanyForm(request.POST, prefix="company_detail_form")

        if investor_user_form.is_valid() or (company_user_form.is_valid() and company_detail_form.is_valid()):

                if company_user_form.is_valid():
                    user = company_user_form.save(commit = False)
                    user.set_password(company_user_form.cleaned_data['password'])
                    user.save()
                    company_detail = company_detail_form.save(commit=False)
                    company_detail.user = user
                    company_detail.save()
                    user_type = 'C'
                else:
                    user = investor_user_form.save(commit = False)
                    user.set_password(investor_user_form.cleaned_data['password'])
                    user.save()
                    user_type = 'I'


                user_detail = UserDetails.create(user,type)
                user_detail.save()

                return redirect('index')
    else:
        investor_user_form = UserForm(prefix="investor_user_form")
        company_user_form= UserForm(prefix="company_user_form")
        company_detail_form = CompanyForm(prefix="company_detail_form")

    return render(request, 'registration/signup.html', {'investor_user_form':investor_user_form,'company_user_form':company_user_form, 'company_detail_form':company_detail_form})


