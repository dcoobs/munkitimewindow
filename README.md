# munkitimewindow
Preflight script for setting a time window in which [Munki](https://github.com/munki/munki) will run.  

Munki Time Window will look for preferences in the following order:  
	-MCX/Configuration Profiles  
	-Set in /Library/Preferences/ManagedInstalls.plist  
	
MunkiTimeWindow.py can be set as a preflight script for either Munki (placed in /usr/local/munki/ and renamed to preflight) or [munkireport-php](https://github.com/munkireport/munkireport-php) (placed in /usr/local/munki/preflight_abort.d).

Note that munkireport-php will overwrite the Munki preflight script upon install so if you intend to use munkireport-php, it's recommended to install munkireport-php before Munki Time Window.

### MCX/Configuration Profiles
Tim Sutton has written a handy, command-line utility ([mcxToProfile](https://github.com/timsutton/mcxToProfile)) to create "Custom Settings" Configuration Profiles.

A sample command, feeding it a .plist that contains the time window preferences:
```
./mcxToProfile.py --plist /path/to/org.example.my.MunkiTimeWindow.plist --identifier MunkiTimeWindowPrefs --manage Always --organization “My Awesome Company” --output MunkiTimeWindow.mobileconfig
```
Note that the identifier corresponds to the variable *BUNDLE_ID* in MunkiTimeWindow.py.

See MunkiTimeWindow.mobileconfig for an example of a generated mobileconfig file.  

### Preferences .plist
If you're setting Munki Time Window preferences using a plist, they should be set in the Munki preferences file (/Library/Preferences/ManagedInstalls.plist) as follows:
```
<key>TimeWindowStart</key>
<string>2:30AM</string>
<key>TimeWindowEnd</key>
<string>7:30AM</string>
```
  
Another plist file can be used in place of ManagedInstalls.plist by modifying the variable *munki_prefs_location* in MunkiTimeWindow.py.
