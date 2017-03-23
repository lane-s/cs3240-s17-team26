
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from Fintech.forms import UserForm, UserDetailForm, CompanyForm, LoginForm
from django.contrib.auth import views as auth_views

def index(request):
    #If not logged in render splash
    #Otherwise render report view
    return render(request,'splash.html')


def signupform(request):
    
    if request.method == 'POST':
        user_form = UserForm(request.POST,prefix="user_form")
        detail_form = UserDetailForm(request.POST,prefix="detail_form")
        company_form = CompanyForm(request.POST, prefix="company_form")

        if user_form.is_valid() and detail_form.is_valid():
            user = user_form.save(commit = False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()
            user_detail = detail_form.save(commit=False)
            user_detail.user = user
            user_detail.save()
            if company_form.is_valid():
                company_detail = company_form.save(commit=False)
                company_detail.user = user
                company_detail.save()
                return redirect('Fintech.views.index')
    else:
        user_form = UserForm(prefix="user_form")
        detail_form = UserDetailForm(prefix="detail_form")
        company_form = CompanyForm(prefix="company_form")

    return render(request, 'registration/signup.html', {'user_form':user_form, 'detail_form':detail_form, 'company_form':company_form})


