from django.shortcuts import render
from Fintech.forms import UserForm,UserDetailForm,CompanyForm

def index(request):
    return render(request, 'index.html')

def signupform(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST,prefix="user_form")
        detail_form = UserDetailForm(request.POST,prefix="detail_form")
        company_form = CompanyForm(request.POST, prefix="company_form")

        if user_form.is_valid() and detail_form.is_valid():
            if detail_form.cleaned_data['type'] == 'I' or company_form.is_valid():
                return redirect('Fintech.views.index')

    else:
        user_form = UserForm(prefix="user_form")
        detail_form = UserDetailForm(prefix="detail_form")
        company_form = CompanyForm(prefix="company_form")

    return render(request, 'signup.html', {'user_form':user_form, 'detail_form':detail_form, 'company_form':company_form})

