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


def print_main_menu():
	print("1. Download files")
	print("2. Encrypt files")
	print("3. Quit")


menuLoop = True;

while(menuLoop):

	username = input("Enter your username:")
	password = getpass.getpass("Enter your password:")


	user = authenticate(username=username,password=password)

	if user:
		print("Successfully Authenticated... ")
		break
	else:
		print("Invalid credentials. Try again")

while(menuLoop):
	print("Welcome, "+user.username)
	print_main_menu()

	choice = int(input("Enter your choice [1-3]:"))

	if choice == 1:
		reportMenuLoop = True
		while(reportMenuLoop):
			reports = Report.objects.filter(Q(is_private=False) 
                | Q(permissions__in=request.user.reportpermissions_set.all()) 
                | Q(permissions__in=[item for sublist in groupPermissions for item in sublist]))

			if reports:
				print("---- All Reports ----")
				i = 0

				for r in reports:
					i+=1
					s = "Files available for download" if r.has_attachments else "No files available for download"
					print(str(i)+". "+r.title+" ---- "+s)

				choice = input("Enter your choice [1-"+str(i)+"]:")

				try:
					report = reports[int(choice)]
					print("---- "+report.title+" ----")
					print("Date: "+report.timestamp)
					print("Company: "+report.company_name)
					print("CEO: "+report.company_ceo)
					print("Phone: "+report.company_phone)
					print("Location: "+report.company_location)
					print("Country: "+report.company_country)
					print("Sector: "+report.sector)
					print("Industry: "+report.industry)
					print("Current Projects: ")
					print(report.current_projects)


				except:
					print("Enter a number between 1 and "+str(i))
			else:
				print("No reports to display, returning to main menu")
				reportMenuLoop = False

	elif choice == 2:
		print("Sorry this does nothing")
	elif choice == 3:
		exit()
	else:
		print("Please enter a number [1-3]")




print("Goodbye")
	


