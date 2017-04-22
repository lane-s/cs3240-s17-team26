import django
import getpass
import os
import sys

PATH=os.path.abspath(os.path.dirname(__file__))

sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fintech.settings")

import django
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from Fintech.models import Report
menuLoop = True;

while(menuLoop):
	username = input("Enter your username:")
	password = getpass.getpass("Enter your password:")


	user = authenticate(username=username,password=password)

	if user:
		print("Successfully Authenticated... ")
		break

while(menuLoop):
	reports = 


print("Goodbye")
	


