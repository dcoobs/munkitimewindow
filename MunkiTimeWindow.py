#!/usr/bin/python
# encoding: utf-8
#
# Copyright 2018 Drew Coobs.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
munkitimewindow
"""

"""
This script is designed to work as a preflight script for Munki (in which case it needs to be renamed to preflight)
or as a preflight_abort.d script for MunkiReport. The script will get the current runtype passed from Munki, try to load the TimeWindowAllowManual
variable from either an MCX profile or from /Library/Preferences/ManagedInstalls.plist. If the job is started by a user and TimeWindowAllowManual
is set to True, the script will exit and allow Munki to continue. If there is an issue loading the TimeWindowAllowManual variable, it defaults to True.
If the job is a scheduled run started automatically by Munki, the script will get the current time and attempt to load the time window preferences, again, from either a MCX profile or from
/Library/Preferences/ManagedInstalls.plist. If there is an issue loading the preferences using either MCX or ManagedInstalls.plist, it uses 1am and 5am as the defaults.
It will then check whether it is within the set time window. If it is not within the time window, it will abort the Munki run.
"""

### Set Munki preference file location & MCX bundle ID variables ###
munki_prefs_location='/Library/Preferences/ManagedInstalls.plist'
BUNDLE_ID = u'edu.illinois.techservices.eps.MunkiTimeWindow'

# Import modules
import sys
from Foundation import CFPreferencesCopyAppValue #used to read MCX preferences/settings
import os
from datetime import datetime #used for date & time functions

# Append the munkilib directory to the system path so we can import munkilib modules (FoundationPlist)
thisdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(thisdir)
sys.path.append(parentdir)

# Import FoundationPlist module (used to interact with both XML and binary .plist files)
from munkilib import FoundationPlist

# Load Munki preferences file
munki_prefs=FoundationPlist.readPlist('/Library/Preferences/ManagedInstalls.plist')

#get runtype argument from Munki
if (len(sys.argv) > 1):
	runtype = sys.argv[1]
else:
	runtype = 'custom'
	
#Try to read TimeWindowAllowManual from MCX/mobileconfig
try:
	allowManualRun = CFPreferencesCopyAppValue('TimeWindowAllowManual', BUNDLE_ID)
	if allowManualRun == None:
		print "MunkiTimeWindow: No MCX/mobileconfig found for TimeWindowAllowManual"
		allowManualRun = True
# If there is any issue with loading TimeWindowAllowManual from MCX, try using values in ManagedInstalls.plist
except:
	try:
		print "MunkiTimeWindow: Attempting to load preferences from ",munki_prefs_location
		allowManualRun = managedInstallsTWManual()
	except:
# If all else fails, use default values (allow manual installs during time window)
		print "MunkiTimeWindow: Unable to find Munki time window manual install preference"
		print "MunkiTimeWindow: Using time window defaults (allow manual installs during time window)"
		allowManualRun = True

if allowManualRun:
	if runtype != 'auto':
		print "MunkiTimeWindow: Detected manual run. Allowing Munki to continue"
   		sys.exit(0)
   	else:
   		print "MunkiTimeWindow: AllowManualRunOutsideTimeWindow: False"
   		print "MunkiTimeWindow: Stopping Munki run"
   		sys.exit(1)

# Define isNowInTimeWindow function
def isNowInTimeWindow(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else: #Over midnight
        return nowTime >= startTime or nowTime <= endTime

# Define functions to read from ManagedInstalls.plist
def managedInstallsTWStart():	
		twStart=munki_prefs['TimeWindowStart']
		return twStart
		
def managedInstallsTWEnd():	
		twEnd=munki_prefs['TimeWindowEnd']
		return twEnd

def managedInstallsTWManual():	
		twManual=munki_prefs['TimeWindowAllowManual']
		return twManual
        
# Get current time
timeNow = datetime.now()

# Convert current time to match formatting of preference time settings and make it human-friendly
friendlyTimeNow = (timeNow.strftime("%-I:%M%p"))

# Try to load time window preferences from MCX/mobileconfig file
# If values equal "None", means something went wrong or preferences are not set
# So look in ManagedInstalls.plist for preferences
try:
	timeStart = CFPreferencesCopyAppValue('TimeWindowStart', BUNDLE_ID)
	timeEnd = CFPreferencesCopyAppValue('TimeWindowEnd', BUNDLE_ID)
	if ((timeStart == None) or (timeEnd == None)):
		print "MunkiTimeWindow: No MCX/mobileconfig found for TimeWindowStart or TimeWindowEnd"
		timeStart = managedInstallsTWStart()
		timeEnd = managedInstallsTWEnd()
# If there is any issue with loading time window preferences from mcx, try using values in ManagedInstalls.plist
except:
	try:
		print "MunkiTimeWindow: Attempting to load preferences from ",munki_prefs_location
		timeStart = managedInstallsTWStart()
		timeEnd = managedInstallsTWEnd()
	except:
# If all else fails, use default values (1am & 5am)
		print "MunkiTimeWindow: Unable to find Munki time window preferences"
		print "MunkiTimeWindow: Using time window defaults (1am & 5am)"
		timeStart = '1:00AM'
		timeEnd = '5:00AM'

# Convert time window preferences to format that can be used for calculations
try:
	timeStartConverted = datetime.strptime(timeStart, "%I:%M%p")
	timeEndConverted = datetime.strptime(timeEnd, "%I:%M%p")
	timeNowConverted = datetime.strptime(friendlyTimeNow, "%I:%M%p")
# If there is an issue with time conversions (typically due to malformed time pref), use defaults (1am & 5am)
except BaseException as e:
	print "MunkiTimeWindow: ERROR: ",e
	print "MunkiTimeWindow: Using time window defaults (1am & 5am)"
	timeStart = '1:00AM'
	timeEnd = '5:00AM'
	timeStartConverted = datetime.strptime(timeStart, "%I:%M%p")
	timeEndConverted = datetime.strptime(timeEnd, "%I:%M%p")
	timeNowConverted = datetime.strptime(friendlyTimeNow, "%I:%M%p")

# Calculate boolean of whether or not within time window
WithinWindow=(isNowInTimeWindow(timeStartConverted, timeEndConverted, timeNowConverted))

# Print outputs
print
print 'MunkiTimeWindow: Time Window Start Time:',timeStart
print 'MunkiTimeWindow: Time Window End Time:',timeEnd
print 'MunkiTimeWindow: Current Time: ',friendlyTimeNow
print 'MunkiTimeWindow: Within specified time window?: ',WithinWindow

# Exit script depending on value of boolean
if WithinWindow:
    print "MunkiTimeWindow: Currently within time window; allowing Munki to continue run"
    sys.exit(0)
else:
    print "MunkiTimeWindow: Currently NOT within time window; stopping Munki run"
    sys.exit(1)