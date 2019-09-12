#!/usr/bin/python
# encoding: utf-8
#
# Copyright 2018-2019 Drew Coobs.
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
or as a preflight_abort.d script for MunkiReport. The script will get the current runtype passed from Munki, try to load the
TimeWindowAllowManual variable from either an MCX profile or from /Library/Preferences/ManagedInstalls.plist. If the job is
started by a user and TimeWindowAllowManual is set to True, the script will exit and allow Munki to continue. If there is an
issue loading the TimeWindowAllowManual variable, it defaults to True. If the job is a scheduled run started automatically
by Munki, the script will get the current time and attempt to load the time window preferences, again, from either a
MCX profile or from /Library/Preferences/ManagedInstalls.plist. If there is an issue loading the preferences using either MCX
or ManagedInstalls.plist, it uses 1am and 5am as the defaults.It will then check whether it is within the set time window.
If it is not within the time window, it will abort the Munki run.
"""

# Import modules
import sys
import os
from datetime import datetime #used for date & time functions
from Foundation import CFPreferencesCopyAppValue #used to read MCX preferences/settings

# Append the munkilib directory to the system path so we can import munkilib modules
# regardless of whether script is a Munki preflight script or preflight_abort.d script for
# munkireport-php
thisdir = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(thisdir)
sys.path.append(parentdir)

# Import FoundationPlist module (used to interact with both XML and binary .plist files)
from munkilib import FoundationPlist

### Set Munki preference file location & MCX bundle ID variables ###
munki_prefs_location='/Library/Preferences/ManagedInstalls.plist'
BUNDLE_ID = u'org.example.my.MunkiTimeWindow'

# Default preferences
DEFAULT_PREFS = {
    'TimeWindowAllowManual': True,
    'TimeWindowStart': '1:00AM',
    'TimeWindowEnd': '5:00AM',
}

# Load Munki preferences file
munki_prefs=FoundationPlist.readPlist(munki_prefs_location)

# Define functions
def isNowInTimeWindow(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else: #Over midnight
        return nowTime >= startTime or nowTime <= endTime
		
def getPrefs(preferenceName, bundleid=''):
# Attempt to get pref from MCX
	try:
		print('MunkiTimeWindow: Attempting to load %s from MCX' % preferenceName)
		pref = CFPreferencesCopyAppValue(preferenceName, bundleid)
		if pref == None:
			print('MunkiTimeWindow: No MCX/mobileconfig found for %s' % preferenceName)
			print('MunkiTimeWindow: Attempting to load preference from %s' % munki_prefs_location)
			try:
				pref = munki_prefs[preferenceName]
				
			except:
				print('MunkiTimeWindow: Error loading %s from %s' % (preferenceName, munki_prefs_location))
				print('MunkiTimeWindow: Unable to obtain %s preference' % preferenceName)
				pref = DEFAULT_PREFS.get(preferenceName)
				print('MunkiTimeWindow: Using default value for %s (%s)' % (preferenceName, pref))
		print('MunkiTimeWindow: %s is %s' % (preferenceName, pref))
		return pref
	except:
		print('MunkiTimeWindow: Error loading %s from MCX' % preferenceName)
		print('MunkiTimeWindow: Attempting to load preference from %s' % munki_prefs_location)
		try:
			pref = munki_prefs[preferenceName]
		except:
			print('MunkiTimeWindow: Error loading %s from %s' % (preferenceName, munki_prefs_location))
			print('MunkiTimeWindow: Unable to obtain %s preference' % preferenceName)
			pref = DEFAULT_PREFS.get(preferenceName)
			print('MunkiTimeWindow: Using default value for %s (%s)' % (preferenceName, pref))

#get runtype argument from Munki
if (len(sys.argv) > 1):
	runtype = sys.argv[1]
else:
	runtype = 'custom'
	print('')
print('MunkiTimeWindow: Runtype= %s' % runtype)

# Obtain TimeWindowAllowManual preference
allowManualRun = getPrefs('TimeWindowAllowManual', BUNDLE_ID)

# If runtype is anything other than auto (typically a manual run), allow Munki run to continue
if allowManualRun:
	if runtype != 'auto':
		print('MunkiTimeWindow: Detected manual run. Allowing Munki to continue')
   		sys.exit(0)
        
# Get current time
timeNow = datetime.now()

# Convert current time to match formatting of preference time settings and make it human-friendly
friendlyTimeNow = (timeNow.strftime("%-I:%M%p"))

# Obtain TimeWindowStart and TimeWindowEnd preferences
timeStart = getPrefs('TimeWindowStart', BUNDLE_ID)
timeEnd = getPrefs('TimeWindowEnd', BUNDLE_ID)

# Convert time window preferences to format that can be used for calculations
try:
	timeStartConverted = datetime.strptime(timeStart, "%I:%M%p")
	timeEndConverted = datetime.strptime(timeEnd, "%I:%M%p")
	timeNowConverted = datetime.strptime(friendlyTimeNow, "%I:%M%p")
# If there is an issue with time conversions (typically due to malformed time pref), use defaults
except BaseException as e:
	print('MunkiTimeWindow: ERROR: %s' % e)
	print('MunkiTimeWindow: Using time window defaults')
	timeStart = DEFAULT_PREFS.get(TimeWindowStart)
	timeEnd = DEFAULT_PREFS.get(TimeWindowEnd)
	timeStartConverted = datetime.strptime(timeStart, "%I:%M%p")
	timeEndConverted = datetime.strptime(timeEnd, "%I:%M%p")
	timeNowConverted = datetime.strptime(friendlyTimeNow, "%I:%M%p")

# Calculate boolean of whether or not within time window
WithinWindow=(isNowInTimeWindow(timeStartConverted, timeEndConverted, timeNowConverted))

# Print final outputs
print('')
print('MunkiTimeWindow: Time Window Start Time: %s' % timeStart)
print('MunkiTimeWindow: Time Window End Time: %s' % timeEnd)
print('MunkiTimeWindow: Current Time: %s' % friendlyTimeNow)
print('MunkiTimeWindow: Within specified time window?: %s' % WithinWindow)

# Abort Munki run depending on value of boolean
if WithinWindow:
    print('MunkiTimeWindow: Currently within time window; allowing Munki to continue run')
    sys.exit(0)
else:
    print('MunkiTimeWindow: Currently NOT within time window; stopping Munki run')
    sys.exit(1)
