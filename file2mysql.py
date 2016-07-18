import MySQLdb
import sys
import ConfigParser
import os
import shutil
import datetime


def store_data_in_MySQL(cur, data):
    print "Filling MySQL..."
    for item in data:
        str = "REPLACE INTO data (datetime, watt) VALUES('%s', %d)" % (item[0].strftime('%Y-%m-%d %H:%M:%S', ), item[1])
        cur.execute(str)


def read_youless_logfile(logfile_filename):
    # copy logfile first to local dir and remove logfile
    tempfile = ('%s-$s') % (logfile_filename, datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    try:
        shutil.copyfile(logfile_filename, tempfile)
    except IOError, e:
        print "Unable to copy " + logfile_filename + ". Aborting..."
        sys.exit(1)

    os.remove(logfile_filename)

    # read file, line by line, store in list of tuples
    data = []
    f = open(tempfile, 'r')
    for line in f:
        line = line.strip()
        columns = line.split()
        date = datetime.datetime.strptime(columns[0] + ' ' + columns[1], '%Y-%m-%d %H:%M:%S')
        watt = int(columns[2])
        # print date, int(watt)
        item = (date, watt)
        data.append(item)

    # remove tempfile and return list of tuple to main
    #os.remove(tempfile)
    return (data)


def open_mysql(server, user, password, database_name):
    try:
        print "Opening MySQL..."
        con = MySQLdb.connect(server, user, password);
        cur = con.cursor()

    except MySQLdb.Error, e:
        # error while openening mysql
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    try:
        cur.execute('USE ' + database_name)

    except MySQLdb.Error, e:
        # error while openening 'database_name', so creating new one with table 'data'
        print "Error %d: %s" % (e.args[0], e.args[1])
        print "Creating database " + database_name
        cur.execute('CREATE DATABASE ' + database_name)
        cur.execute('USE ' + database_name)
        cur.execute('CREATE TABLE data(datetime datetime, watt int, PRIMARY KEY(datetime))');

    return (cur, con)


if __name__ == '__main__':
    print "Youless_file2MySQL: read Youless file and store information in MySQL"
    print "Version 0.0.1 by Witteveder\n"

    # use configparser to get youless http address and logfilename
    config = ConfigParser.ConfigParser()
    config.read('settings.ini')
    server = config.get('MYSQL SETTINGS', 'server')
    user = config.get('MYSQL SETTINGS', 'user')
    password = config.get('MYSQL SETTINGS', 'password')
    database_name = config.get('MYSQL SETTINGS', 'database_name')
    logfile_filename = config.get('SETTINGS', 'logfile_filename')

    [cur, con] = open_mysql(server, user, password, database_name)
    data = read_youless_logfile(logfile_filename)
    store_data_in_MySQL(cur, data)

    cur.close()
    con.commit()
    con.close()

    print "Done."
