# Introduction #

The scripts are controlled by variables that need to be set in the SETTINGS.INI file.


# Details #
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

**Short explanation**

logfile\_filename=path tofile on usb stick + filename

ipaddress=internal IP address of youless

kwhprice=cost of 1 KWH

server=where to reach MySQL DB

user=typically root

password=yourpasswordhere

database\_name=name of database, do not choose "youless" if you have also -LA-'s script working