import os, sys, random, struct, datetime, getpass
from Crypto.Cipher import AES
import base64
import hashlib
from tkinter import filedialog
from tkinter import *
import urllib.request
import shutil
import requests
from requests.auth import HTTPBasicAuth


host = "https://lokahifintech26.herokuapp.com"
api = host+"/api"

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

    r = requests.get(api+"/reports",auth=HTTPBasicAuth(username,password));
    reports = r.json();

    if 'detail' in reports:
        print("Invalid credentials. Try again")
    else:
        print("Successfully Authenticated... ")
        break

while(menuLoop):
    print("1. Download and decrypt files")
    print("2. Encrypt files")
    print("3. Quit")

    choice = int(input("Enter your choice [1-3]:"))

    if choice == 1:
        reportMenuLoop = True
        while(reportMenuLoop):
            reports = requests.get(api+"/reports",auth=HTTPBasicAuth(username,password)).json();

            if reports:
                print("---- All Reports ----")
                i = 0

                for r in reports:
                    i+=1
                    reportFiles = requests.get(api+"/reports/"+str(r['id'])+"/files",auth=HTTPBasicAuth(username,password)).json();
                    numFiles = len(reportFiles)
                    s = str(numFiles)+" files available for download" if numFiles > 0 else "No files"
                    print(str(i)+". "+r['title']+" ---- "+s)

                print(str(i+1)+". Back to main menu")

                choice = input("Enter your choice [1-"+str(i+1)+"]:")

                if int(choice) == i+1:
                    reportMenuLoop = False
                else:
                    try:
                        report = reports[int(choice)-1]
                        print("---- "+report['title']+" ----")
                        print("Date: "+str(report['timestamp']))
                        print("Company: "+report['company_name'])
                        print("CEO: "+report['company_ceo'])
                        print("Phone: "+report['company_phone'])
                        print("Location: "+report['company_location'])
                        print("Country: "+report['company_country'])
                        print("Sector: "+report['sector'])
                        print("Industry: "+report['industry'])
                        print("Current Projects: ")
                        print(report['current_projects'])

                        files = requests.get(api+"/reports/"+str(report['id'])+"/files",auth=HTTPBasicAuth(username,password)).json();

                        fileLoop = True

                        while(fileLoop):
                            print("---- Choose a file to download ----")
                            fileNo = 0

                            for f in files:
                                fileNo += 1
                                if f['is_encrypted']:
                                    encrypted = "Encrypted"
                                else:
                                    encrypted = "Not Encrypted"
                                print(str(fileNo)+". "+f['title']+" - "+f['upload'].split('/')[-1]+" - "+encrypted)

                            print(str(fileNo+1)+". Back to reports")

                            file_choice = input("Enter your choice [1-"+str(fileNo+1)+"]:")

                            if int(file_choice) == fileNo+1:
                                fileLoop = False
                            else:
                                file = files[int(file_choice)-1]
                                encrypted_suffix = "_encrypted" if file['is_encrypted'] else ""

                                filename = file['upload'].split('/')[-1]

                                urllib.request.urlretrieve(file['upload'], filename)

                                print("File downloaded to directory of this application")
                                if file['is_encrypted']:
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

                                        try:
                                            decrypt_file(hashlib.sha256(str.encode(passkey)).digest(),filename,outname)
                                            os.remove(filename);
                                            print("Decrypted filed stored as "+outname+" in the directory of this script")
                                        except:
                                            print("Decryption error! Incorrect password or encryption method")
                        except Exception as e:
                            print(e)
                            print("Enter a number between 1 and "+str(i+1))
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

        try:
            encrypt_file(hashlib.sha256(str.encode(passkey)).digest(),file_path,file_path+"_encrypted") 
        except:
            "Encryption error!"

        print("Encrypted file stored at "+str(file_path+"_encrypted"))

    elif choice == 3:
        exit()
    else:
        print("Please enter a number [1-3]")


    


