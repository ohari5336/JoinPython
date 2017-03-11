#!/usr/bin/env python3
import argparse, urllib.request, urllib.parse, json, os, re
os.chdir(os.path.dirname(__file__)) # sets a constant working dir
##### Argument Parser starts here #####
ap = argparse.ArgumentParser()
ap.add_argument('-te','--text',help='Text (Tasker Command or notification text)',nargs='*')
ap.add_argument('-ti','--title',help='Title (If set will create notification)',nargs='*')
ap.add_argument('-i','--icon',help='Icon URI (publicly accessible URL or local file URI; used whenever a notification is created)')
ap.add_argument('-s','--smallicon',help='Icon URI to be used as the statusbar icon')
ap.add_argument('-p','--priority',help='Priority of the notification from -2 (lowest) to 2 (highest and default)',type=int,choices=range(-2,3))
ap.add_argument('-v','--vibration',help='Vibration for when the notification is recived. Generate the pattern at http://autoremotejoaomgcd.appspot.com/AutoRemoteNotification.html')
ap.add_argument('-u','--url',help='URL')
ap.add_argument('-c','--clipboard',help='Clipboard',nargs='*')
ap.add_argument('-f','--file',help='File (must be a publicly accessible URL)')
ap.add_argument('-d','--device',help='The device name or a group (group.all, group.android, group.chrome, group.windows10, group.phone, group.tablet, group.pc)',nargs='*')
ap.add_argument('-smsn','--smsnumber',help='Phone number to send an SMS to. If you want to set an SMS you need to set this and the smstext values',nargs='*')
ap.add_argument('-cn','--callnumber',nargs='*',help='A number to call')
ap.add_argument('-smst','--smstext',help='Some text to send in an SMS. If you want to set an SMS you need to set this and the smsnumber values',nargs='*')
ap.add_argument('-fi','--find',help='Set to true to make your device ring loudly')
ap.add_argument('-w','--wallpaper',help='A publicly accessible URL of an image file. Will set the wallpaper on the receiving device')
ap.add_argument('-mms','--mmsfile',help='MMS file. smsnumber must be set for this to have an affect')
ap.add_argument('-lw','--lockWallpaper',help='The wallpaper to set on the lockscreen (Android 7+), must be publicly accessible URL')
opts = ap.parse_args()
##### Argument Parser ends here #####
try: # loads device json into a dictionary
    with open('devices.json','r') as device:
        deviceData = json.loads(device.read())
except:
    os.system('joinsetup.py -d')
    with open('devices.json','r') as device:
        deviceData = json.loads(device.read())
argsDict = vars(opts) # puts args into a dictionary for more convinient use
if argsDict['device'] is None:
    argsDict['device'] = deviceData['pref']
for key, value in argsDict.items(): # curcumvents the need to encase args in quotes
    if type(value) is list:
        argsDict[key] = ' '.join(value)
if opts.smsnumber or opts.callnumber is not None:
    try: # loads the contacts json as a dictionary if a number or name is supplied.
        with open('contacts.json','r') as contact:
            contactData = json.loads(contact.read())
    except: # defaults to a number if a name is not found in the json
        pass
if opts.smsnumber is not None:
    if argsDict['smsnumber'] in contactData:
        argsDict['smsnumber'] = contactData[argsDict['smsnumber']] # replaces the name with the number
    else:
        clean = re.sub('[^\d+]', '', argsDict['smsnumber'])
        if re.match('\+?\d{10,}', clean):
            argsDict['smsnumber'] = clean
        else:
            print('Not a valid name or number. SMS cancelled.')
            print('Make sure the number is valid or, if a name was used, run joinsetup.py -c to set up name support.')
            argsDict['smsnumber'] = None
            argsDict['smstext'] = None
if opts.callnumber is not None:
    if argsDict['callnumber'] in contactData:
        argsDict['callnumber'] = contactData[argsDict['callnumber']]
    else:
        clean = re.sub('[^\d+]', '', argsDict['callnumber'])
        if re.match('\+?\d{10,}', clean):
            argsDict['callnumber'] = clean
        else:
            print('Not a valid name or number. Phone call canceled.')
            print('Make sure the number is valid or, if a name was used, run joinsetup.py -c to set up name support.')
            argsDict['callnumber'] = None
deviceName = argsDict['device']
argsDict.pop('device',None) # removes device from argsDict to prevent sending extra params
argsDict['apikey'] = deviceData['apikey'] # https://plus.google.com/+Jo%C3%A3oDias/posts/GYwEvtSb238
if ',' in deviceName: # allows for multiple device names separated by commas
    argsDict['deviceNames'] = deviceName
    # Old device Id multiple device code. Now uses beta device name + api key.
    # deviceIds = []
    # deviceNames = deviceName.split(',')
    # for x in deviceNames:
    #     deviceIds.append(deviceData[x])
    # argsDict['deviceIds'] = ','.join('deviceIds')
elif 'group' in deviceName: # allows for groups (group.android, etc.)
    argsDict['deviceId'] = deviceName
else: # allows for single device
    argsDict['deviceId'] = deviceData[deviceName]
encoded = []
for key, value in argsDict.items():
    if value is not None:
        encoded.append('='.join([key, urllib.parse.quote_plus(value)]))
urllib.request.urlopen('https://joinjoaomgcd.appspot.com/_ah/api/messaging/v1/sendPush?' + '&'.join(encoded))
