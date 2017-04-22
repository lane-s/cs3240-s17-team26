from django.shortcuts import redirect, render, get_object_or_404
from django.core.urlresolvers import reverse

import datetime
import re

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.forms import inlineformset_factory

from Fintech.decorators import request_passes_test
from Fintech.forms import *
from Fintech.models import UserDetails, CompanyDetails, Report, File, Message


def super_user(request):
    return {'super_user': request.user.is_superuser}


def is_company_user(user):
    return True if CompanyDetails.objects.filter(user=user) else False


def is_site_manager(user):
    return True if user.groups.filter(name="Site Managers") else False


def is_suspended(user):
    return True if user.groups.filter(name="Suspended Users") else False

def can_view_report(user, report):
    return True if report.permissions.allowed_users.filter(pk=user.pk) or user.groups.filter(pk__in=[g.pk for g in report.permissions.allowed_groups.all()]) else False

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

    #This is wasteful, but it's what the TA is requiring us to do as far as I can tell
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
                | Q(permissions__in=[item for sublist in groupPermissions for item in sublist]))
        return render(request, 'splash.html', {'report_list': report_list,'has_messages':has_messages})


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


FileFormset = inlineformset_factory(Report, File, form=FileForm, extra=0)

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def createReport(request):
    company_user = CompanyDetails.objects.filter(user=request.user)

    if company_user or is_site_manager(request.user):
        if request.method == 'POST':
            report_form = ReportForm(request.POST, prefix="report_form")
            permissions_form = ReportPermissionsForm(request.POST, prefix="permissions_form")

            file_formset = FileFormset(request.POST,request.FILES,prefix="file_formset") 

            if report_form.is_valid() and permissions_form.is_valid() and file_formset.is_valid():
                report = report_form.save(commit=False)
                report.owner = request.user
                report.has_attachments = False
                report.save()

                permissions = permissions_form.save(commit=False);
                permissions.report = report;
                permissions.save();
                permissions_form.save_m2m();

                for form in file_formset:
                    file = form.save(commit=False)
                    file.upload_date = datetime.date.today()
                    file.report = report
                    file.save()
                    print("File saved")

                if File.objects.filter(report=report):
                    report.has_attachments = True;
                else:
                    report.has_attachments = False;

                report.save()

                messages.success(request, "Report created")
                return redirect('index')
        else:
            report_form = ReportForm(prefix="report_form")
            permissions_form = ReportPermissionsForm(prefix="permissions_form")
            file_formset = FileFormset(prefix="file_formset")
        return render(request, 'reports/createReport.html', {'report_form': report_form,'permissions_form':permissions_form,'file_formset':file_formset})

    else:
        return redirect('index')

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewReport(request, pk):
    report = get_object_or_404(Report, pk=pk)
    is_owner = report.owner.pk == request.user.pk
    if not report.is_private or is_owner or is_site_manager(request.user) or can_view_report(request.user,report):
        unencrypted_files = File.objects.filter(report__pk = report.pk, is_encrypted=False)
        # checks if user is in report group or is a collaborator
        return render(request, 'reports/viewReport.html', {'report': report, 'is_owner':is_owner,'unencrypted_files':unencrypted_files})
    else:
        return redirect('index')


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def editReport(request, pk):
    report = get_object_or_404(Report, pk=pk)

    #Apparently only managers should be allowed to edit reports
    if not is_site_manager(request.user):
        return redirect('index')

    if request.method == 'POST':
        report_form = ReportForm(request.POST, instance=report)
        permissions_form = ReportPermissionsForm(request.POST, instance=report.permissions)
        file_formset = FileFormset(request.POST,request.FILES,instance=report)

        if report_form.is_valid() and permissions_form.is_valid() and file_formset.is_valid():
            report_form.save()
            permissions_form.save()

            files = file_formset.save()

            for f in files:
                f.report = report
                if not f.upload_date:
                    f.upload_date = datetime.date.today()
                f.save()

            messages.success(request, "Report edited")
            return redirect('viewReport',pk=report.pk)
    else:
        report_form = ReportForm(instance=report)
        permissions_form = ReportPermissionsForm(instance=report.permissions)
        file_formset = FileFormset(instance=report)

    return render(request, 'reports/editReport.html', {'report_form': report_form,'permissions_form':permissions_form, 'report':report, 'file_formset':file_formset})

def deleteReport(request, pk):
    report = get_object_or_404(Report, pk=pk)

    if is_site_manager(request.user) or report.owner.pk == request.user.pk:
        report.delete()

    return redirect('index')  

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
                                    ['company_name', 'current_projects', 'title', 'timestamp', 'company_ceo', 'company_phone', 'company_location', 'company_country', 'sector', 'industry'])

            found_entries = Report.objects.filter(entry_query)

    return render(request, 'reports/searchReports.html',
                  {'query_string': query_string, 'found_entries': found_entries})


def createAdvancedSearch(request):
    advanced_search_form = advancedSearchForm(prefix="advanced_search_form")
    return render(request, 'reports/createAdvancedSearchReports.html', {'advanced_search_form': advanced_search_form})


def advancedSearch(request):
    found_entries = None
    search_values_array = []
    search_filters_array = []
    if request.method == 'POST':
        search_form = advancedSearchForm(request.POST, prefix="advanced_search_form")
        for each in search_form:
            search_form.fields
            search_values_array += each
        search_dict = {}
        for each in search_filters_array:
            search_dict[search_filters_array[each]] = search_values_array[each]
        found_entries = Report.objects
        if search_filters_array:
            for filters in search_filters_array:
                if search_dict[filters] != filters:
                    entry_query = get_query(search_dict[filters], filters)
                    found_entries = found_entries.filter(entry_query)
    return render(request, 'reports/advancedSearchReports.html',
                  {'search_filters': search_filters_array, 'search_values': search_values_array, 'found_entries': found_entries})


def sendMessage(request):
    if request.method == 'POST':
        message_form = MessageForm(request.POST, prefix="message_form")
        if message_form.is_valid():
            message = message_form.save(commit=False)
            message.sender = request.user
            message.opened = False
            message.save()
            # if report.has_attachments == True:
            # upload multiples files
            messages.success(request, "Message sent")
            return redirect('viewMessages')
    else:
            message_form = MessageForm(prefix="message_form")
    return render(request, 'messages/sendMessage.html', {'message_form': message_form})

def viewMessage(request, pk):
    message = get_object_or_404(Message, pk=pk)
    message.opened = True
    message.save()
    return render(request, 'messages/viewMessage.html', {'message': message})

def viewMessages(request):
    message_list = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'messages/viewMessages.html', {'message_list': message_list})

def deleteMessage(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.receiver == request.user:
        message.delete()
    return redirect("viewMessages")

