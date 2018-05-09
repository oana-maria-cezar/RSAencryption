#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
import tkinter
import base64
import os
import sys
import shutil

def encrypt(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = inputText.get("1.0",tkinter.END)
    outText.delete('1.0', tkinter.END)

    f = open(myTmpDir + 'pt' + str(identity) + '.bin','wb')
    f.write(msg)
    f.close()

    os.popen("rsa.exe e " + myTmpDir + "pt" + str(identity) + ".bin "+ myTmpDir + "locEnc" + str(identity) + ".bin")

    locEncFileName = myTmpDir + "locEnc" + str(identity) + ".bin"
    with open(locEncFileName, "rb") as f:
        readFile = f.read()
    # Convert to hex representation
    digest = base64.encodestring(bytes(readFile))

    # TODO: overwirite
    outText.insert(tkinter.END, digest)

def decrypt(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    msg = inputText.get("1.0",tkinter.END)
    outText.delete('1.0', tkinter.END)

    decB64Msg = base64.decodestring(msg)

    f = open(myTmpDir + 'ct' + str(identity) + '.bin','wb')
    f.write(decB64Msg)
    f.close()

    os.popen("rsa.exe d " + myTmpDir + "ct" + str(identity) + ".bin " + myTmpDir + "ptSender" + str(identity) + ".bin")

    with open(myTmpDir + "ptSender" + str(identity) + ".bin", "rb") as f:
        readFile = f.read()
    # Convert to hex representation
    decMsg = bytes(readFile)

    # TODO: overwirite
    outText.insert(tkinter.END, decMsg)

def clear(event=None):  # event is passed by binders.
    inputText.delete('1.0', tkinter.END)
    outText.delete('1.0', tkinter.END)

#updates text
def boxtext(new_value):
    # set nick name
    identity = new_value
    privKey = users[identity].split(" ")[0]
    pubKey = users[identity].split(" ")[1]
    mod = users[identity].split(" ")[2]

    print("privKey: ", pubKey, " mod: ", mod)
    print("pubKey: ", pubKey, " mod: ", mod)

def quit():
    top.quit()

identity = ""
privKey = ""
pubKey = ""
mod = ""

users={
    'Alice': "keys/Alice/AlicePrivExp keys/Alice/AlicePubExp keys/Alice/AliceMod1024",
    'Bob': "keys/Bob/BobPrivExp keys/Bob/BobPubExp keys/Bob/BobMod1024",
    }

# delete tmp files
myTmpDir = "./tmp/"
## Try to remove tree; if failed show an error using try...except on screen
try:
    shutil.rmtree(myTmpDir)
except OSError, e:
    print ("Error: %s - %s." % (e.filename,e.strerror))

# make the tmp dir
os.mkdir(myTmpDir)

top = tkinter.Tk()
top.title("Chatter")

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
