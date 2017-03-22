from django.shortcuts import render
from django.shortcuts import redirect
from Fintech.forms import UserForm,UserDetailForm,CompanyForm

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
            user = user_form.save()
            user_detail = detail_form.save(commit=False)
            user_detail.user = user
            user_detail.save()
            if detail_form.cleaned_data['type'] == 'I' or company_form.is_valid():
                company_detail = company_form.save(commit=False)
                company_detail.user = user
                company_detail.save()
                return redirect('Fintech.views.index')

    else:
        user_form = UserForm(prefix="user_form")
        detail_form = UserDetailForm(prefix="detail_form")
        company_form = CompanyForm(prefix="company_form")

    return render(request, 'signup.html', {'user_form':user_form, 'detail_form':detail_form, 'company_form':company_form})

