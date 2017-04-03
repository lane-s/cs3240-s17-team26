
from django.shortcuts import redirect, render, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from Fintech.forms import *
from django.contrib.auth import views as auth_views
from Fintech.models import UserDetails

def logged_in(request):
    return {'logged_in':request.user.is_authenticated}

def company_user(request):
    return {'company_user': CompanyDetail.objects.filter(user=request.user)}

def index(request):
    if not request.user.is_authenticated:
        #If not logged in render splash
        return render(request,'splash.html',{})
    else:
        #Otherwise render report view
        return render(request,'splash.html',{}) 


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
                else:
                    user = investor_user_form.save(commit = False)
                    user.set_password(investor_user_form.cleaned_data['password'])
                    user.save()

                return redirect('index')
    else:
        investor_user_form = UserForm(prefix="investor_user_form")
        company_user_form= UserForm(prefix="company_user_form")
        company_detail_form = CompanyForm(prefix="company_detail_form")

    return render(request, 'registration/signup.html', {'investor_user_form':investor_user_form,'company_user_form':company_user_form, 'company_detail_form':company_detail_form})


@login_required
def createGroup(request):

    if request.method == 'POST':
        group_form = GroupForm(request.POST, prefix="group_form")

        if group_form.is_valid():
            group = group_form.save(commit="false")

            request.user.groups.add(group)
            messages.success(request, "Group created")
            return redirect('groups')


    else:
        group_form = GroupForm(prefix="group_form")

    return render(request, 'groups/createGroup.html', {'group_form':group_form})

@login_required
def viewGroups(request):
    group_list = request.user.groups.all()

    return render(request, 'groups/viewGroups.html',{'group_list':group_list})

@login_required
def viewGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    return render(request, 'groups/viewGroup.html',{'group':group, 'user_list':user_list})

@login_required
def leaveGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)
    request.user.groups.remove(group)

    #Delete empty groups
    user_list = User.objects.filter(groups__pk=pk)

    if not user_list:
        group.delete()
        messages.success(request, "You were the last user, so the group has been deleted")
    else:
        messages.success(request, "You left the group")

    return redirect('groups')

@login_required
def editGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    if request.method == 'POST':
        add_user_form = GroupAddUser(request.POST, prefix="add_user_form")

        if add_user_form.is_valid():
            username = add_user_form.cleaned_data['username'];
            user = User.objects.get(username=username)
            if not user:
                messages.error(request, "No user with that username exists")
            elif user.groups.filter(pk=pk):
                messages.error(request, "User is already in that group")
            else:
                user.groups.add(group)
                messages.success(request, "User added to group")

    else:
        add_user_form = GroupAddUser(prefix="add_user_form")
               

    return render(request, 'groups/editGroup.html',{'group':group, 'form':add_user_form})




