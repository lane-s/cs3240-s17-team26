from django.forms import ModelForm, CharField, Form
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.models import User, Group
from Fintech.users import suspended_test, is_site_manager
from Fintech.decorators import request_passes_test
from Fintech.models import Message

#Forms
class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ('name',)


class GroupAddUser(Form):
    username = CharField(label='Username', max_length=50)


#Views
@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def createGroup(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    if request.method == 'POST':
        group_form = GroupForm(request.POST, prefix="group_form")

        if group_form.is_valid():
            group = group_form.save(commit="false")

            request.user.groups.add(group)
            messages.success(request, "Group created")
            return redirect('groups')


    else:
        group_form = GroupForm(prefix="group_form")

    return render(request, 'groups/createGroup.html', {'group_form': group_form, 'username': username}, )



@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewGroups(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    site_manager_group = None
    suspended_user_group = None

    if is_site_manager(request.user):
        site_manager_group = get_object_or_404(Group, name="Site Managers")
        suspended_user_group = get_object_or_404(Group, name="Suspended Users")
        group_list = Group.objects.all().exclude(name="Site Managers").exclude(name="Suspended Users")
    else:
        group_list = request.user.groups.all()

    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break

    return render(request, 'groups/viewGroups.html',
                  {'group_list': group_list, 'site_manager_group': site_manager_group,
                   'suspended_user_group': suspended_user_group, 'has_messages': has_messages, 'username': username})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewGroup(request, pk):
    username = None
    if request.user.is_authenticated():
        username = request.user
    group = get_object_or_404(Group, pk=pk)
    user_list = User.objects.filter(groups__pk=pk)

    in_group = request.user in user_list

    if not in_group and not is_site_manager(request.user):
        return redirect('groups')
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    return render(request, 'groups/viewGroup.html',
                  {'group': group, 'user_list': user_list, 'user_id': request.user.pk, 'in_group': in_group,
                   'has_messages': has_messages, 'username': username})


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
                messages.success(request, user.username+" removed from group")
                return redirect('viewGroup', pk=group.pk)

    return redirect('groups')


@login_required
def deleteGroup(request, pk):
    group = get_object_or_404(Group, pk=pk)

    if is_site_manager(request.user) and group.name != "Site Managers":
        group.delete()
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)

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
                messages.success(request, username+" added to group")

    else:
        add_user_form = GroupAddUser(prefix="add_user_form")
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    username = None
    if request.user.is_authenticated():
        username = request.user
    return render(request, 'groups/editGroup.html',
                  {'group': group, 'form': add_user_form, 'has_messages': has_messages, 'username': username})