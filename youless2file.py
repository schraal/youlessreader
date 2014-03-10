import urllib2
import json
import os
import datetime
import time
import ConfigParser

def read_youless(httpaddress):

  params1='/V?h=1&f=j'
  params2='/V?h=2&f=j'

  #get readings from youless for last hour
  resp=urllib2.urlopen(httpaddress+params1)
  decoded=json.loads(resp.read())
  resp2=urllib2.urlopen(httpaddress+params2)
  decoded2=json.loads(resp2.read())

  #remove possible occuring None value at end
  if decoded['val'][-1]==None:
    del decoded['val'][-1]
  if decoded2['val'][-1]==None:
    del decoded2['val'][-1]

  #merge the two half hours
  decoded2['val']=decoded2['val']+decoded['val']

  return(decoded2)

def write_youless_data(yl_json, logfname):

  #get date and time of oldest entry
  t2=datetime.datetime.strptime(yl_json['tm'], "%Y-%m-%dT%H:%M:%S")

  #does log file exits?
  if not os.path.isfile(logfname):
    #no start one and write readings
    print "Logfile not found. Starting new one, file:", logfname
    logfile=open(logfname, 'w')
    for item in yl_json['val']:
      if not item==None:
        logfile.write(t2.strftime("%Y-%m-%d %H:%M:%S")+item+'\n')
        t2=t2+datetime.timedelta(minutes=1)
    logfile.close()

  else:
    #append readings to existing one
    print "Logfile found. Appending to file:", logfname
    t=os.path.getmtime(logfname)

    #get last entry, use it as starting point for adding newer entries
    logfile=open(logfname, 'r')
    logfile.seek(-50, 2)
    line=logfile.readlines()
    t3=datetime.datetime.strptime(line[-1][0:-6], "%Y-%m-%d %H:%M:%S") #is latest entry in file
    logfile.close()

    #start writing, newer entries only
    logfile=open(logfname, 'a')
    print "Updating", logfname, "starting from", str(t3)

    for item in yl_json['val']:
      if not item==None:
        if t2-t3 >= datetime.timedelta(minutes=1): #new data point
          logfile.write(t2.strftime("%Y-%m-%d %H:%M:%S")+item+'\n')
        t2=t2+datetime.timedelta(minutes=1)
        
    logfile.close()


if __name__=='__main__':

  print "Youless2file: read Youless and store information in a plain textfile (preventing duplicate entries)"
  print "Version 0.0.1 by Witteveder\n"

  #use configparser to get youless http address and logfilename
  config=ConfigParser.ConfigParser()
  config.read('settings.ini')
  ipaddress=config.get('SETTINGS', 'ipaddress')
  logfile_filename=config.get('SETTINGS', 'logfile_filename')

  #read the youless
  youless_json=read_youless('http://'+ipaddress)

  #write the data to a file
  write_youless_data(youless_json, logfile_filename)

