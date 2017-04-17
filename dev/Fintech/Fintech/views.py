from django.shortcuts import redirect, render, get_object_or_404
from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from Fintech.decorators import request_passes_test
import re
from django.db.models import Q
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from Fintech.forms import *
from django.contrib.auth import views as auth_views
from Fintech.models import UserDetails, CompanyDetails, Report, File, Message


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


def index(request):
    if not request.user.is_authenticated or is_suspended(request.user):
        # If not logged in render splash
        return render(request, 'splash.html')
    else:
        # Otherwise render report view
        if is_company_user(request.user):
            report_list = Report.objects.filter(owner=request.user)
        else:
            report_list = Report.objects.all()

        return render(request, 'splash.html', {'report_list': report_list})


def signupform(request):
    if request.method == 'POST':
        investor_user_form = UserForm(request.POST, prefix="investor_user_form")
        company_user_form = UserForm(request.POST, prefix="company_user_form")
        company_detail_form = CompanyForm(request.POST, prefix="company_detail_form")

        if investor_user_form.is_valid() or (company_user_form.is_valid() and company_detail_form.is_valid()):

            if company_user_form.is_valid():
                user = company_user_form.save(commit=False)
                user.set_password(company_user_form.cleaned_data['password'])
                user.save()
                company_detail = company_detail_form.save(commit=False)
                company_detail.user = user
                company_detail.save()
            else:
                user = investor_user_form.save(commit=False)
                user.set_password(investor_user_form.cleaned_data['password'])
                user.save()

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

    return render(request, 'groups/createGroup.html', {'group_form': group_form})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewGroups(request):
    site_manager_group = None
    suspended_user_group = None

    if is_site_manager(request.user):
        site_manager_group = get_object_or_404(Group, name="Site Managers")
        suspended_user_group = get_object_or_404(Group, name="Suspended Users")
        group_list = Group.objects.all().exclude(name="Site Managers").exclude(name="Suspended Users")
    else:
        group_list = request.user.groups.all()

    return render(request, 'groups/viewGroups.html',
                  {'group_list': group_list, 'site_manager_group': site_manager_group,
                   'suspended_user_group': suspended_user_group})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewGroup(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    in_group = request.user in user_list

    if not in_group and not is_site_manager(request.user):
        return redirect('groups')

    return render(request, 'groups/viewGroup.html',
                  {'group': group, 'user_list': user_list, 'user_id': request.user.pk, 'in_group': in_group})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def leaveGroup(request, pk, user_id):
    group = get_object_or_404(Group, pk=pk)

    if group.name != "Site Managers":
        user = get_object_or_404(User, pk=user_id)

        user.groups.remove(group)

        # Delete empty groups
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
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def editGroup(request, pk):
    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    # Make sure only users in the group can add users
    if request.user not in user_list and not is_site_manager(request.user):
        return redirect('groups')

    if request.method == 'POST':
        add_user_form = GroupAddUser(request.POST, prefix="add_user_form")

        if add_user_form.is_valid():
            username = add_user_form.cleaned_data['username'];
            user = User.objects.filter(username=username)
            if not user:
                messages.error(request, "No user with that username exists")
            elif user[0].groups.filter(pk=pk):
                messages.error(request, "User is already in that group")
            elif is_site_manager(user[0]) and group.name == "Suspended Users":
                messages.error(request, "Site Managers cannot be suspended")
            else:
                user[0].groups.add(group)
                messages.success(request, "User added to group")

    else:
        add_user_form = GroupAddUser(prefix="add_user_form")

    return render(request, 'groups/editGroup.html', {'group': group, 'form': add_user_form})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def createReport(request):
    company_user = CompanyDetails.objects.filter(user=request.user)

    if company_user or is_site_manager(request.user):
        if request.method == 'POST':
            report_form = ReportForm(request.POST, prefix="report_form")
            if report_form.is_valid():
                report = report_form.save(commit=False)
                report.owner = request.user
                report.save()
                # if report.has_attachments == True:
                # upload multiples files
                messages.success(request, "Report created")
                return redirect('index')
        else:
            report_form = ReportForm(prefix="report_form")
        return render(request, 'reports/createReport.html', {'report_form': report_form})

    else:
        return redirect('index')


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def uploadFile(request):
    if request.method == 'POST':
        file_form = FileForm(request.Post, prefix="")
        file_form.save(commit="false")
        messages.success(request, "File uploaded to report")
        return redirect('reports')
    else:
        file_form = FileForm(prefix="file_form")
    return render(request, 'reports/uploadFiles.html', {'file_form': file_form})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewReport(request, pk):
    report = get_object_or_404(Report, pk=pk)
    if not report.is_private or report.owner.pk == request.user.pk or is_site_manager(request.user):
        # checks if user is in report group or is a collaborator
        return render(request, 'reports/viewReport.html', {'report': report})
    else:
        return redirect('index')


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def editReport(request, pk):
    report = get_object_or_404(Report, pk=pk)
    report_form = ReportForm(instance=report)

    if report.owner.pk != request.user.pk and not is_site_manager(request.user):
        return redirect('index')

    if request.method == 'POST':
        report_form = ReportForm(request.POST, instance=report)
        if report_form.is_valid():
            report_form.save()
            messages.success(request, "Report edited")
            return redirect('index')
    else:
        report_form = ReportForm(instance=report)

    return render(request, 'reports/editReport.html', {'report_form': report_form})


def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:

        ( some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']

    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)]


def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.

    '''
    query = None  # Query to search for every search term
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None  # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


def search(request):
    query_string = ''
    found_entries = None
    if request.method == 'GET':
            query_string = request.GET.get('q')
            entry_query = get_query(query_string,
                                    ['company_name', 'current_projects', 'title', 'current_projects'])

            found_entries = Report.objects.filter(entry_query).order_by('title')

    return render(request, 'reports/searchReports.html',
                  {'query_string': query_string, 'found_entries': found_entries})

def sendMessage(request):
    if request.method == 'POST':
        message_form = MessageForm(request.POST, prefix="message_form")
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.save()
            # if report.has_attachments == True:
            # upload multiples files
            messages.success(request, "Message sent")
            return redirect('index')
    else:
            message_form = MessageForm(prefix="message_form")
    return render(request, 'messages/sendMessage.html', {'message_form': message_form})

def viewMessage(request):
    message = get_object_or_404(Message)
    return render(request, 'messages/viewMessage.html', {'message': message})

def viewMessages(request):
    message_list = Message.objects.filter(receiver=request.user)
    return render(request, 'messages/viewMessages.html', {'message_list': message_list})