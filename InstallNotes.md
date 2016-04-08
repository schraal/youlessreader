# Introduction #

This series of python scripts is created to read electrity use with the [youless](http://www.youless.nl) device.
All scripts have been developed on a synology NAS (DS209+II).

The youless device can only store 1 hour of readings. This means every hour the device has to be read. To avoid unnecessary disk use (electricity use and wear) the hourly data is written to a USB stick. Once a day (can be chosen more often) the stick-file is written to a MySQL database.

Electricity use can be visualized using a web interface. In this web interface specific days or part of days can be picked. In the interface, the MySQL database can also be updated to include to latest actual readings.

# Details #

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

# How to run the server #

I run the python server using the following commands:
```
cd /volume1/@appstore/youless
nohup /opt/bin/python2.7 code2.py 12345 &
```


First I go to the right directory and start the python script (code2.py) using python2.7. The nohup en "&" ensure the script starts in the background.

The server can than be accessed by going in a web browser to:

```
http://youripaddres:12345/
```
