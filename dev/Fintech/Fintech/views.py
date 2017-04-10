
from django.shortcuts import redirect, render, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from Fintech.decorators import request_passes_test

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from Fintech.forms import *
from django.contrib.auth import views as auth_views
from Fintech.models import UserDetails


def super_user(request):
    return {'super_user':request.user.is_superuser}

def is_company_user(user):
    return True if CompanyDetails.objects.filter(user=user) else False

def is_site_manager(user):
    return True if user.groups.filter(name="Site Managers") else False

def is_suspended(user):
    return True if user.groups.filter(name="Suspended Users") else False

def suspended_test(request):
    passes = not is_suspended(request.user);
    if not passes:
        messages.error(request,"Your account has been suspended. Please contact a Site Manager")
    return passes;


def user_context_processor(request):
    if request.user.is_authenticated:
        company_user = is_company_user(request.user)
        site_manager = is_site_manager(request.user)
        suspended_user = is_suspended(request.user)

        return {'logged_in':True,'company_user':company_user,'site_manager':site_manager,'suspended_user':suspended_user}
    else:
        return {'logged_in':False,'company_user':False,'site_manager':False,'suspended_user':False}


def index(request):
    if not request.user.is_authenticated:
        #If not logged in render splash
        return render(request,'splash.html')
    else:
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
@request_passes_test(suspended_test,login_url='/',redirect_field_name=None)
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
@request_passes_test(suspended_test,login_url='/',redirect_field_name=None)
def viewGroups(request):

    site_manager_group = None
    suspended_user_group = None

    if is_site_manager(request.user):
        site_manager_group = get_object_or_404(Group, name="Site Managers")
        suspended_user_group = get_object_or_404(Group, name="Suspended Users")
        group_list = Group.objects.all().exclude(name="Site Managers").exclude(name="Suspended Users")
    else:
        group_list = request.user.groups.all()

    return render(request, 'groups/viewGroups.html',{'group_list':group_list,'site_manager_group':site_manager_group,'suspended_user_group':suspended_user_group})

@login_required
@request_passes_test(suspended_test,login_url='/',redirect_field_name=None)
def viewGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    in_group = request.user in user_list

    if not in_group and not is_site_manager(request.user):
        return redirect('groups')

    return render(request, 'groups/viewGroup.html',{'group':group, 'user_list':user_list, 'user_id':request.user.pk, 'in_group':in_group})

@login_required
@request_passes_test(suspended_test,login_url='/',redirect_field_name=None)
def leaveGroup(request, pk, user_id):

    group = get_object_or_404(Group, pk=pk)

    if group.name != "Site Managers":
        user = get_object_or_404(User, pk=user_id)

        user.groups.remove(group)

        #Delete empty groups
        user_list = User.objects.filter(groups__pk=pk)

        if not user_list and group.name != "Suspended Users":
            group.delete()
            if request.user.pk == user_id:
                messages.success(request, "You were the last user, so the group has been deleted")
            else:
                messages.success(request, "You removed the last user, so the group has been deleted")
        else:
            if request.user.pk == user.id:
                messages.success(request, "You left the group")
            else:
                messages.success(request, "User removed from group")
                return redirect('viewGroup', pk=group.pk)

    return redirect('groups')

@login_required
def deleteGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)

    if is_site_manager(request.user) and group.name != "Site Managers":
        group.delete()

    return redirect('groups')

@login_required
@request_passes_test(suspended_test,login_url='/',redirect_field_name=None)
def editGroup(request, pk):

    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    #Make sure only users in the group can add users
    if request.user not in user_list and not is_site_manager(request.user):
        return redirect('groups')

    if request.method == 'POST':
        add_user_form = GroupAddUser(request.POST, prefix="add_user_form")

        if add_user_form.is_valid():
            username = add_user_form.cleaned_data['username'];
            user = User.objects.get(username=username)
            if not user:
                messages.error(request, "No user with that username exists")
            elif user.groups.filter(pk=pk):
                messages.error(request, "User is already in that group")
            elif is_site_manager(user) and group.name == "Suspended Users":
                messages.error(request, "Site Managers cannot be suspended")
            else:
                user.groups.add(group)
                messages.success(request, "User added to group")

    else:
        add_user_form = GroupAddUser(prefix="add_user_form")
               

    return render(request, 'groups/editGroup.html',{'group':group, 'form':add_user_form})




