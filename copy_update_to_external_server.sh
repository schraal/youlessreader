#/bin/bash
cd /volume1/@appstore/youlessreader
source ./settings.ini
echo $logfile_filename
echo $external_server
/bin/python2.7 youless2file.py >/dev/null && scp $logfile_filename $external_server
tail -2 $logfile_filename
