from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, Form, CharField
from Fintech.users import suspended_test
from Fintech.decorators import request_passes_test
from Fintech.models import Message, Report
from django.db.models import Q

import re
#Forms
class advancedSearchForm(Form):
    title = CharField(label= 'Title', required=False, max_length=30,)
    company_name = CharField(label= 'Company Name', max_length=30, required=False,)
    company_ceo = CharField(label= 'Company CEO', max_length=30, required=False,)
    company_phone = CharField(label= 'Company Phone', max_length=30, required=False,)
    company_location = CharField(label= 'Company Location', max_length=30, required=False,)
    company_country = CharField(label= 'Company Country', max_length=30, required=False,)
    sector = CharField(label= 'Sector', max_length=30, required=False,)
    industry = CharField(label= 'Industry', max_length=30, required=False,)
    current_projects = CharField(label= 'Current Projects', required=False,)

#Helper functions
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


#Views
@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def search(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    query_string = ''
    found_entries = None
    if request.method == 'GET':
        query_string = request.GET.get('q')
        if query_string != '':
            entry_query = get_query(query_string,
                                    ['company_name', 'current_projects', 'title', 'timestamp', 'company_ceo',
                                     'company_phone', 'company_location', 'company_country', 'sector', 'industry'])

            found_entries = Report.objects.filter(entry_query)
            found_entries = list(found_entries)
            for each in found_entries:
                if each.is_private:
                    found_entries.remove(each)

    return render(request, 'reports/searchReports.html',
                  {'query_string': query_string, 'found_entries': found_entries, 'has_messages': has_messages,
                   'username': username})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def createAdvancedSearch(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    advanced_search_form = advancedSearchForm(prefix="advanced_search_form")
    return render(request, 'reports/createAdvancedSearchReports.html',
                  {'advanced_search_form': advanced_search_form, 'has_messages': has_messages, 'username': username})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def advancedSearch(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    found_entries = []
    all_entries = Report.objects.all()
    search_form = None
    if request.method == 'POST':
        search_form = advancedSearchForm(request.POST, prefix="advanced_search_form")
        if search_form.is_valid():
            search_form = search_form.cleaned_data
            for field, value in search_form.items():
                if value != "" and value != None:
                    found_entries = all_entries
                    entry_query = get_query(value, [field])
                    found_entries = found_entries.filter(entry_query)
                    all_entries = found_entries
            found_entries = list(found_entries)
            for each in found_entries:
                if each.is_private:
                    found_entries.remove(each)

    return render(request, 'reports/advancedSearchReports.html', {'found_entries': found_entries},
                  {'search_form': search_form, 'has_messages': has_messages, 'username': username})
