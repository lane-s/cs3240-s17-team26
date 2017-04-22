import os, sys, random, struct, datetime, getpass
from Crypto.Cipher import AES
import base64
import hashlib
from tkinter import filedialog
from tkinter import *
import urllib.request
import shutil

PATH=os.path.abspath(os.path.dirname(__file__))

sys.path.append("../")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Fintech.settings")

import django
django.setup()

from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from Fintech.models import Report, File

host = "http://127.0.0.1:8000"

def encrypt_file(key, in_filename, out_filename=None, chunksize=64*1024):
    if not out_filename:
        out_filename = in_filename + '.enc'

    iv = os.urandom(16)

    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))

def decrypt_file(key, in_filename, out_filename=None, chunksize=24*1024):
    if not out_filename:
        out_filename = os.path.splitext(in_filename)[0]

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)

menuLoop = True

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
	print("1. Download and decrypt files")
	print("2. Encrypt files")
	print("3. Quit")

	choice = int(input("Enter your choice [1-3]:"))

	if choice == 1:
		reportMenuLoop = True
		while(reportMenuLoop):
			groupPermissions = [g.reportpermissions_set.all() for g in user.groups.all()];

			reports = list(Report.objects.filter(Q(is_private=False) 
                | Q(permissions__in=user.reportpermissions_set.all()) 
                | Q(permissions__in=[item for sublist in groupPermissions for item in sublist])))

			if reports:
				print("---- All Reports ----")
				i = 0

				for r in reports:
					i+=1
					numFiles = len(File.objects.filter(report__pk=r.pk))
					s = str(numFiles)+" files available for download" if numFiles > 0 else "No files"
					print(str(i)+". "+r.title+" ---- "+s)

				print(str(i+1)+". Back to main menu")

				choice = input("Enter your choice [1-"+str(i+1)+"]:")

				if int(choice) == i+1:
					reportMenuLoop = False
				else:
					# try:
					report = reports[int(choice)-1]
					print("---- "+report.title+" ----")
					print("Date: "+str(report.timestamp))
					print("Company: "+report.company_name)
					print("CEO: "+report.company_ceo)
					print("Phone: "+report.company_phone)
					print("Location: "+report.company_location)
					print("Country: "+report.company_country)
					print("Sector: "+report.sector)
					print("Industry: "+report.industry)
					print("Current Projects: "+report.current_projects)
					print(report.current_projects)

					files = list(File.objects.filter(report__pk=report.pk))

					fileLoop = True

					while(fileLoop):
						print("---- Choose a file to download ----")
						fileNo = 0

						for f in files:
							fileNo += 1
							if f.is_encrypted:
								encrypted = "Encrypted"
							else:
								encrypted = "Not Encrypted"
							print(str(fileNo)+". "+f.title+" - "+f.upload.name.split('/')[-1]+" - "+encrypted)

						print(str(fileNo+1)+". Back to reports")

						file_choice = input("Enter your choice [1-"+str(fileNo+1)+"]:")

						if int(file_choice) == fileNo+1:
							fileLoop = False
						else:
							file = files[int(file_choice)-1]
							encrypted_suffix = "_encrypted" if file.is_encrypted else ""

							print(host+str(file.upload.url))
							filename = file.upload.name.split('/')[-1]

							urllib.request.urlretrieve(host+file.upload.url, filename)

							print("File downloaded to directory of this application")
							if file.is_encrypted:
								print("This file is encrypted. Would you like to decrypt it?")
								choice = input("(y/n): ")
								if choice == 'y':
									while(True):
										passkey = getpass.getpass("Enter password:")
										passkeyverify = getpass.getpass("Verify password:")
										if passkey == passkeyverify:
											break
										else:
											print("Passwords do not match. Try again")

									outname = filename+"_dec"
									if filename.endswith('_encrypted'):
										outname = filename[:-len('_encrypted')]

									decrypt_file(hashlib.sha256(str.encode(passkey)).digest(),filename,outname)



					# except Exception as e:
					# 	print(e)
					# 	print("Enter a number between 1 and "+str(i+1))
			else:
				print("No reports to display, returning to main menu")
				reportMenuLoop = False

	elif choice == 2:
		#instantiate a Tk window
		root = Tk()
		#dunno what this does, fixes askopenfilename if I use it.
		root.update()
		root.withdraw()
		file_path = filedialog.askopenfilename(title="Choose a file to encrypt")
		root.destroy()

		while(True):
			passkey = getpass.getpass("Set encryption password:")
			passkeyverify = getpass.getpass("Verify password:")
			if passkey == passkeyverify:
				break
			else:
				print("Passwords do not match. Try again")

		encrypt_file(hashlib.sha256(str.encode(passkey)).digest(),file_path,file_path+"_encrypted")	

		print("Encrypted file stored at "+str(file_path+"_encrypted"))

	elif choice == 3:
		exit()
	else:
		print("Please enter a number [1-3]")


	


