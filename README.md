A lot of the documentation below is from the original project. It is only partially up-to-date.

nginx config based on: http://webpy.org/cookbook/fastcgi-nginx


Installation
============
Introduction
------------

This series of python scripts is created to read electrity use with the youless device.
All scripts have been developed on a synology NAS (DS209+II).

The youless device can only store 1 hour of readings.
This means every hour the device has to be read.
To avoid unnecessary disk use (electricity use and wear) the hourly data is written to a USB stick.
Once a day (can be chosen more often) the stick-file is written to a MySQL database.

Electricity use can be visualized using a web interface.
In this web interface specific days or part of days can be picked.
In the interface, the MySQL database can also be updated to include to latest actual readings.

Details
-------

The python scripts use the libraries MySQL-python and web.py. These need to be installed.
Hourly readings of the youless device are done with crontab, using:

```
0 * * * * cd /volume1/@appstore/youless && /volume1/@optware/bin/python2.7 youless2file.py >/dev/null
```

This means the device is read every hours at 0 minutes.
Once a day (at 07.05), I sent all readings to the MySQLDB, using;
```
5 7 * * * cd /volume1/@appstore/youless && /volume1/@optware/bin/python2.7 file2mysql.py >/dev/null
```

This can be changed to be as often as you want.

How to run the server
---------------------

I run the python server using the following commands:
```
cd /volume1/@appstore/youless nohup /opt/bin/python2.7 code2.py 12345 &
```

First I go to the right directory and start the python script (code2.py) using python2.7.
The nohup and "&" ensure the script starts in the background.
The server can than be accessed by going in a web browser to:
```
http://youripaddres:12345/
```

Files
=====

* code2.py - this is the actual python code for the webserver
* file2mysql.py - this file sent all entries from the USB file to the MySQL DB
* la2wv.py - this script converts all measurements from the -LA- database to this database
* settings.ini - file where all necessary variables are set
* youless2file.py - this script reads the youless device and sets readings to the USB file
* start_youless.sh - script for starting python server

The directories static and templates contain images, javascripts and the template web page for the python server.


Settings
========

The scripts are controlled by variables that need to be set in the SETTINGS.INI file.

These are the settings I actually use:

```
[SETTINGS]
logfile_filename=/volumeUSB1/usbshare/youless_logfile.txt
ipaddress=192.168.178.14
kwhprice=0.22

[MYSQL SETTINGS]
server=localhost
user=root
password=secret
database_name=youless_wv
```

Short explanation

* logfile_filename=path tofile on usb stick + filename
* ipaddress=internal IP address of youless
* kwhprice=cost of 1 KWH
* server=where to reach MySQL DB
* user=typically root
* password=yourpasswordhere
* database_name=name of database, do not choose "youless" if you have also -LA-'s script working


External server
===============
It is possible to use the Synology to read the data from the Youless and have the user interface running on an 
external server. To do so the software needs to be installed on the Synology and on the external server.

Synology
--------

* Make sure you have Python running on the Synology
* Install the software in ```/volume1/@appstore/youless```.
* Make a copy of ```settings.ini.template``` to ```settings.ini``` and fill in the values under ```[SETTINGS]```. 
```external_server``` should have the form of ```user@server:``` (it is used to scp the youless logfile).
* Add an hourly call to  ```copy_update_to_external_server.sh``` in the Task Scheduler.
* Make sure the root user has passwordless access to the external server. How to configure that, e.g.: 
  https://www.howtogeek.com/66776/HOW-TO-REMOTELY-COPY-FILES-OVER-SSH-WITHOUT-ENTERING-YOUR-PASSWORD/
  
External server
---------------