#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import tkinter
import base64
import os
import sys
import shutil
import time

identity = ""
privKey = ""
pubKey = ""
mod = ""


def encrypt(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global identity
    global myTmpDir
    global privKey
    global pubKey
    global mod

    msg = inputText.get("1.0",tkinter.END)[:-1]
    outText.delete('1.0', tkinter.END)

    # create file
    f = open(myTmpDir + "locEnc" + str(identity) + ".bin","w+")
    f.close()

    f = open(myTmpDir + 'pt' + str(identity) + '.bin','w')
    f.write(msg)
    f.close()

    command = "rsa.exe e " + myTmpDir + "pt" + str(identity) + ".bin "+ myTmpDir + "locEnc" + str(identity) + ".bin " + mod + " " + pubKey
    print("command encrypt: ", command, "\n")
    os.popen(command)
    time.sleep(1)

    locEncFileName = myTmpDir + "locEnc" + str(identity) + ".bin"
    print(locEncFileName)

    ctP = open(locEncFileName, "rb")
    readFile = ctP.read()
    ctP.close()

    print(bytes(readFile))
    # Convert to hex representation
    digest = base64.encodestring(bytes(readFile))

    outText.insert(tkinter.END, digest)

def decrypt(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    global identity
    global myTmpDir
    global privKey
    global pubKey
    global mod

    msg = inputText.get("1.0",tkinter.END)
    outText.delete('1.0', tkinter.END)

    # create file
    f = open(myTmpDir + "ptSender" + str(identity) + ".bin", "w+")
    f.close()

    decB64Msg = base64.decodestring(str.encode(msg))

    f = open(myTmpDir + 'ct' + str(identity) + '.bin','wb')
    f.write(decB64Msg)
    f.close()

    command = "rsa.exe d " + myTmpDir + "ct" + str(identity) + ".bin " + myTmpDir + "ptSender" + str(identity) + ".bin " + mod + " " + privKey
    print("command decrypt: ", command, "\n")
    os.popen(command)
    time.sleep(1)

    with open(myTmpDir + "ptSender" + str(identity) + ".bin", "rb") as f:
        readFile = f.read()
    f.close()
    # Convert to hex representation
    decMsg = bytes(readFile)

    outText.insert(tkinter.END, decMsg)

def clear(event=None):  # event is passed by binders.
    inputText.delete('1.0', tkinter.END)
    outText.delete('1.0', tkinter.END)

#updates text
def boxtext(new_value):
    # set nick name
    global identity
    global privKey
    global pubKey
    global mod

    identity = new_value
    privKey = users[identity].split(" ")[0]
    pubKey = users[identity].split(" ")[1]
    mod = users[identity].split(" ")[2]
    print("-------------")
    print(str(identity))
    type(identity)
    print("-------------")


    print("privKey: ", pubKey, " mod: ", mod)
    print("pubKey: ", pubKey, " mod: ", mod)

def quit():
    global myTmpDir
    try:
        shutil.rmtree(myTmpDir)
    except OSError as e:
        print ("Error: %s - %s." % (e.filename,e.strerror))

    top.quit()

users={
    'Alice': "keys/Alice/AlicePrivExp.dat keys/Alice/AlicePubExp.dat keys/Alice/AliceMod.dat",
    'Bob': "keys/Bob/BobPrivExp.dat keys/Bob/BobPubExp.dat keys/Bob/BobMod.dat",
    }

# delete tmp files
myTmpDir = "./tmp/"
## Try to remove tree; if failed show an error using try...except on screen
try:
    shutil.rmtree(myTmpDir)
except OSError as e:
    print ("Error: %s - %s." % (e.filename,e.strerror))

# make the tmp dir
os.mkdir(myTmpDir)

top = tkinter.Tk()
top.title("RSA encryption/decryption")

messages_frame = tkinter.Frame(top)
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
inputText = tkinter.Text(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
# inputText = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
inputText.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
inputText.insert(tkinter.END, 'Input data')
inputText.pack()
messages_frame.pack()

outText = tkinter.Text(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
outText.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
outText.insert(tkinter.END, 'Output data')
outText.pack()

encButton = tkinter.Button(top, text="Encrypt", command=encrypt)
encButton.pack()

decButton = tkinter.Button(top, text="Decrypt", command=decrypt)
decButton.pack()

clearButton = tkinter.Button(top, text="Clear", command=clear)
clearButton.pack()

boxTextVal = tkinter.StringVar()
boxTextVal.set('Select nick name')
userDropDown = tkinter.OptionMenu(top, boxTextVal, *users, command=boxtext)
userDropDown.pack()

top.protocol("WM_DELETE_WINDOW", quit)

tkinter.mainloop()  # Starts GUI execution.
