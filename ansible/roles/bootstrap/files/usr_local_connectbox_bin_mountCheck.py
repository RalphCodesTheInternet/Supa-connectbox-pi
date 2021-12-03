#!/usr/bin/env Python3
# -*- coding: utf-8 -*-
# Loop to test for insertion of USB stick and to mount it as /media/usb0
#  Also tests for removal of USB and responds with umount /media/usb0

import os
import time
import re

DEBUG = 0

global total
total = 0
c=["","",""]
loc=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
# mnt[x]>=0 where x is the usb port of the mount and mnt[x] is the line of the /dev/sdx1
global mnt
mnt=[-1,-1,-1,-1,-1,-1,-1,-1,-1, -1, -1, -1]
d=["","","","","","","","","","","","","","","","","","","","","",""]

def mountCheck():
    global mnt
    global total
    j = 0                   #mount iterator looking for unmounted devices
    b = os.popen('lsblk').read()
    while (j < total):
      if DEBUG: print("loop 1, iterate",j)
      if (mnt[j] >= 0):
        if not ('usb' + chr(ord('0')+j) in b):
          c = "umount /media/usb" + chr(ord('0')+j)
          res = os.system(c)
          if DEBUG: print("completed unmount /media/usb", chr(ord('0')+j))
          if not res:
            mnt[j] = -1
            if j>0:
               os.popen('rmdir /media/usb'+chr(ord('0')+j))
            j += 1
          else:
            if DEBUG: print("Failed to " + c)
            mnt[j] = -1
            j += 1
            # Run these functions on mount -- added 20211111
            # Enhanced Content Load
            os.system("/usr/bin/python /usr/local/connectbox/bin/enhancedInterfaceUSBLoader.py >/tmp/enhancedInterfaceUSBLoader.log 2>&1 &")
        else:
          #Were here with the device still mounted
          j += 1
      else:
        #were here because there was no mount device detected
        if DEBUG: print("device not mounted usb", j)
        j += 1
    i=0                       #line iterator
    j=0                       #used for finding sdx1's
    k=0                       #used for usb mounts
    loc=[-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1,-1]
    b = os.popen('lsblk').read()
    c = b.partition("\n")
# while we have lines to parse we check each line for an sdx1 device and mount it if not already
    while ((c[0] != "") and (i<10)):
      if DEBUG: print("Loop 2, iterate:",i, c[0])
      d[i] = c[0]
      e=re.search('sd[a-z]1', d[i])
      if e: 
        loc[j]=i
        if not (('usb' in d[i]) or ('part /' in d[i])):     #True if were not mounted but should be
          while (k < 10) and (mnt[k] >= 0):                 #Find an empty usbX to mount to
            if DEBUG: print("loop 3, iterate:",k)
            k += 1
          if not (os.path.exists("/media/usb"+chr(ord("0")+k))):  #if the /mount/usbx isn't there create it
            res = os.system("mkdir /media/usb"+chr(ord("0")+k))
          b = "mount /dev/" + e.group() + " /media/usb" + chr(ord('0')+k) + " -o noatime,nodev,nosuid,sync,iocharset=utf8"
          res = os.system(b)
          if DEBUG: print("completed mount /dev/",e.group)
          if (k == 0):
            # Run these functions on mount -- added 20211111
            # SSH Enabler
            os.system("/bin/sh -c '/usr/bin/test -f /media/usb0/.connectbox/enable-ssh && (/bin/systemctl is-active ssh.service || /bin/systemctl enable ssh.service && /bin/systemctl start ssh.service)'")
            # Moodle Course Loader
            os.system("/bin/sh -c '/usr/bin/test -f /media/usb0/*.mbz && /usr/bin/php /var/www/moodle/admin/cli/restore_courses_directory.php /media/usb0/' >/tmp/restore_courses_directory.log 2>&1 &")
            # Enhanced Content Load
            os.system("/usr/bin/python /usr/local/connectbox/bin/enhancedInterfaceUSBLoader.py >/tmp/enhancedInterfaceUSBLoader.log 2>&1 &")
          mnt[k]=i
          k += 1
          j += 1
        else:
          if ('usb' in d[i]):
            a = d[i].partition("usb")
            if (a[2] != "") and (a[2].isalnum()):
              l = ord(a[2])-ord("0")
              mnt[l]=i
              j+=1
              if DEBUG: print("/dev/sdx1 is already mounted as usb",chr(l+ord('0')))
            else:
              if DEBUG: print("Error parsing usb# in line", i)
              j+= 1
          else:
              if DEBUG: print("/dev/sdx1 is already mounted but not as usb", d[i])
              j+= 1
      c = c[2].partition("\n")
      i += 1
# now that we have looked at all lines in the current lsblk we need to count up the mounts
    j = -1
    i = 0
    while (i < 10):            # we will check a maximum of 10 mounts
      if DEBUG: print("loop 4, iterate:",i)
      if (mnt[i] != -1):
        i +=1
        j +=1
      else:                   # we have a hole or are done but need to validate
        k = i+1
        while (k < 10) and (mnt[i] == -1):  #checking next mount to see if it is valid
          if DEBUG: print("loop 5, iterate:",k,i)
          if (mnt[k] != -1):
            mnt[i] = mnt[k]   # move the mount into this hole and clear the other point
            j += 1
            mnt[k] = -1
            i += 1
            k += 1
            if DEBUG: print("had to move mount to new location",k," from ",i)
          else:			# we have no mount here
            k += 1
        if (k == 10):           # if we have look at all mounts then were done otherwise we will check again
          i=10
    total = j+1
    if DEBUG: print("total of devices mounted is", total)
    if DEBUG: print("located", mnt)
    return()


if __name__ == '__main__':
    try: os.remove('/usr/local/connectbox/PauseMount')
    except:
      if DEBUG: print("there was no PauseMount file keeping us from going forward")
    while True:
        loop_time = 3
        if not os.path.exists('/usr/local/connectbox/PauseMount'):
            mountCheck()
        time.sleep(loop_time)

