# munkitimewindow
A preflight script for setting a time window in which [Munki](https://github.com/munki/munki) will run.  

Munki Time Window will look for preferences in the following order:  
	-MCX/Configuration Profiles  
	-Set in /Library/Preferences/ManagedInstalls.plist  
	
MunkiTimeWindow.py can be set as a preflight script for either Munki (placed in /usr/local/munki/ and renamed to preflight) or [munkireport-php](https://github.com/munkireport/munkireport-php) (placed in /usr/local/munki/preflight_abort.d).

Note that munkireport-php will overwrite the Munki preflight script upon install so if you intend to use munkireport-php, it's recommended to install munkireport-php before Munki Time Window.

### Keys
Munki Time Window has three preference keys:

| Key | Type | Default | Description |
| --- | -------- | ------- | ----------- |
| TimeWindowStart | string | 1:00AM | Time at which Munki Time Window will begin allowing Munki to run |
| TimeWindowEnd | string | 5:00AM | Time at which Munki Time Window will begin preventing Munki from running |
| TimeWindowAllowManual | boolean | True | If true, users will be able to run Munki manually outside the set time window (both MSC and from Terminal |

### MCX/Configuration Profiles
Tim Sutton has written a handy, command-line utility ([mcxToProfile](https://github.com/timsutton/mcxToProfile)) to create "Custom Settings" Configuration Profiles.

A sample command, feeding it a .plist that contains the time window preferences:
```
./mcxToProfile.py --plist /path/to/org.example.my.MunkiTimeWindow.plist --identifier MunkiTimeWindow --manage Always --organization "My Awesome Company"
```
Note that the name of the .plist corresponds to the variable *BUNDLE_ID* in MunkiTimeWindow.py. So for the example above, BUNDLE_ID should be set to 'org.example.my.MunkiTimeWindow'.

See MunkiTimeWindow.mobileconfig for an example of a generated mobileconfig file.  

### Preferences .plist
If you're setting Munki Time Window preferences using a plist, they should be set in the Munki preferences file (/Library/Preferences/ManagedInstalls.plist) as follows:
```
<key>TimeWindowAllowManual</key>
<True/>
<key>TimeWindowStart</key>
<string>2:30AM</string>
<key>TimeWindowEnd</key>
<string>7:30AM</string>
```
  
Another plist file can be used in place of ManagedInstalls.plist by modifying the variable *munki_prefs_location* in MunkiTimeWindow.py.
