import MySQLdb
import sys
import ConfigParser
import os
import shutil
import datetime


def read_LA_database(server, user, password):
  print "Opening MySQL database: youless"
  try:
    con = MySQLdb.connect(server, user, password, 'youless');
    cur = con.cursor()

  except MySQLdb.Error, e:
    #error while openening mysql
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  #get, process and store all records from -LA- database
  print "Getting datapoints from -LA- database..."
  cur.execute("SELECT * FROM data_h")
  data=cur.fetchall()
  lijst=[]
  for row in data:
    t2=row[1];
    str=row[4].split(',')

    for item in str:
      datapoint=(t2, int(item.strip('"')))
      lijst.append(datapoint)
      #print(datapoint[0].strftime("%Y-%m-%d %H:%M:%S") + ' %d') %datapoint[1]
      t2=t2+datetime.timedelta(minutes=1)

  cur.close()
  con.close()

  return(lijst)


def store_data_in_MySQL(cur, data):
  print "Sending data to table 'data'..."
  for item in data:
    str="REPLACE INTO data (datetime, watt) VALUES('%s', %d)" %(item[0].strftime('%Y-%m-%d %H:%M:%S',), item[1])
    cur.execute(str)

def open_mysql(server, user, password, database_name):
  try:
    print "Opening MySQL database: " + database_name
    con = MySQLdb.connect(server, user, password);
    cur = con.cursor()
    
  except MySQLdb.Error, e:
    #error while openening mysql
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

  try:
     cur.execute('USE '+database_name)

  except MySQLdb.Error, e:
    #error while openening 'database_name', so creating new one with table 'data'
    print "Error %d: %s" % (e.args[0], e.args[1])
    print "Creating database " + database_name
    cur.execute('CREATE DATABASE '+database_name)
    cur.execute('USE '+database_name)
    cur.execute('CREATE TABLE data(datetime datetime, watt int, PRIMARY KEY(datetime))');

  return(cur, con)

if __name__=='__main__':
  print "LA2WV: copy Youless data from -LA- MySQL-database to Witteveder MySQL-database."
  print "Version 0.0.1 by Witteveder\n"

  #use configparser to get youless http address and logfilename
  config=ConfigParser.ConfigParser()
  config.read('settings.ini')
  server=config.get('MYSQL SETTINGS', 'server')
  user=config.get('MYSQL SETTINGS', 'user')
  password=config.get('MYSQL SETTINGS', 'password')
  database_name=config.get('MYSQL SETTINGS', 'database_name')
  logfile_filename=config.get('SETTINGS', 'logfile_filename')

  lijst=read_LA_database(server, user, password)
  [cur, con]=open_mysql(server, user, password, database_name)
  store_data_in_MySQL(cur, lijst)
  cur.close()
  con.close()
  
  print "Done."
