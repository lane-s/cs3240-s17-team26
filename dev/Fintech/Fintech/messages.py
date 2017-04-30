from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm
from Fintech.users import suspended_test
from Fintech.decorators import request_passes_test
from Fintech.models import UserDetails, Message
from Crypto.PublicKey import RSA
from Crypto import Random
import ast
#Forms
class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ('receiver','subject','content','encrypt')
        exclude = ('static_encrypt',)

#Views
@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def sendMessage(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    if request.method == 'POST':
        message_form = MessageForm(request.POST, prefix="message_form")
        if message_form.is_valid():
            message_dict = message_form.cleaned_data
            receiver = message_dict['receiver']
            if receiver == request.user:
                messages.error(request, "Intended Message Recipient is You. Please Try Again.")
                return render(request, 'messages/sendMessage.html',
                              {'message_form': message_form, 'username': username})
            message = message_form.save(commit=False)
            message.sender = request.user
            message.opened = False

            if message.encrypt:
                message.static_encrypt = True
                receiver = UserDetails.objects.get(user=message.receiver)
                rsa_obj = RSA.importKey(receiver.key)
                pubkey = rsa_obj.publickey()
                content = message.content
                enc_content = pubkey.encrypt(content.encode('utf-8'), 32)
                message.content = str(enc_content)
                message.save()
            else:
                message.static_encrypt = False
                message.save()

            messages.success(request, "Message sent")
            return redirect('viewMessages')
    else:
        message_form = MessageForm(prefix="message_form")
    return render(request, 'messages/sendMessage.html', {'message_form': message_form, 'username': username})


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewMessage(request, pk):
    username = None
    if request.user.is_authenticated():
        username = request.user
    message = get_object_or_404(Message, pk=pk,receiver=request.user)
    if message.encrypt:
        recipient = True
        return render(request, 'messages/encryptedMessage.html', {'message': message,'recipient':recipient})
    else:
        message.opened = True
        message.save()
        has_messages = False
        message_list = Message.objects.filter(receiver=request.user)
        for m in message_list:
            if m.opened == False:
                has_messages = True
                break
        return render(request, 'messages/viewMessage.html', {'message': message, 'username': username, 'has_messages': has_messages})

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewSentMessage(request, pk):
    username = None
    if request.user.is_authenticated():
        username = request.user
    message = get_object_or_404(Message, pk=pk,sender=request.user)
    if message.static_encrypt:
        recipient = False
        return render(request, 'messages/encryptedMessage.html', {'message': message,'recipient':recipient})
    else:
        has_messages = False
        message_list = Message.objects.filter(receiver=request.user)
        for m in message_list:
            if m.opened == False:
                has_messages = True
                break
        return render(request, 'messages/viewSentMessage.html', {'message': message, 'username': username, 'has_messages': has_messages})

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewMessages(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    message_list = Message.objects.filter(receiver=request.user).order_by('-timestamp')
    return render(request, 'messages/viewMessages.html', {'message_list': message_list, 'has_messages': has_messages, 'username': username})

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def viewSentMessages(request):
    username = None
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    sent_message_list = Message.objects.filter(sender=request.user).order_by('-timestamp')
    return render(request, 'messages/SentMessages.html',{'sent_message_list': sent_message_list, 'has_messages': has_messages, 'username': username})

@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def deleteMessage(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.receiver == request.user:
        message.delete()
    return redirect("viewMessages")


@login_required
@request_passes_test(suspended_test, login_url='/', redirect_field_name=None)
def decryptMessage(request, pk):
    username = None
    message = get_object_or_404(Message, pk=pk)
    message.encrypt = False
    content = message.content
    user_details = UserDetails.objects.get(user=request.user)
    private_key = RSA.importKey(user_details.key)
    decrypted_content = private_key.decrypt(ast.literal_eval(content)).decode('utf-8')
    message.content = decrypted_content
    message.opened = True
    message.save()
    if request.user.is_authenticated():
        username = request.user
    has_messages = False
    message_list = Message.objects.filter(receiver=request.user)
    for m in message_list:
        if m.opened == False:
            has_messages = True
            break
    return render(request, 'messages/viewMessage.html', {'message': message, 'has_messages': has_messages, 'username': username})
