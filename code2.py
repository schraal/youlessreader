#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ConfigParser
import datetime

import MySQLdb
import web
from web import form

from file2mysql import read_youless_logfile, store_data_in_MySQL
from youless2file import read_youless, write_youless_data


def openMySQLdb():
    # open MySQL database
    con = MySQLdb.connect(server, user, password);
    cur = con.cursor()
    cur.execute('USE ' + database_name)
    return (con, cur)


def closeMySQLdb(con, cur):
    # close MySQL database
    cur.close()
    con.close()


def updateyouless2mysql():
    con, cur = openMySQLdb()

    # get latest reading from youless
    youless_json = read_youless("http://" + ipaddress)
    write_youless_data(youless_json, logfile_filename)

    # get latest readings from youless stored file
    data = read_youless_logfile(logfile_filename)
    store_data_in_MySQL(cur, data)

    closeMySQLdb(con, cur)


# function to get first or last date entry in MySQLdb
def getSpecialDate(which):
    con, cur = openMySQLdb()
    latest_entry = cur.execute('SELECT ' + which + '(datetime) FROM data')
    t = cur.fetchall()
    t = [element for tupl in t for element in tupl]
    closeMySQLdb(con, cur)
    return (t[0])


def make_form():
    con, cur = openMySQLdb()
    # get years present in DB
    query = cur.execute('SELECT DISTINCT(YEAR(datetime)) FROM data')
    raw_years = cur.fetchall()
    closeMySQLdb(con, cur)

    years = []
    for i in raw_years:
        years.append(str(i[0]))

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
              'November', 'December']

    a = range(1, 32)
    days = []
    for i in a:
        days.append(str(i))

    t1 = getSpecialDate('MAX')

    myform = form.Form(
        form.Dropdown('Day', days, value=str(t1.day)),
        form.Dropdown('Month', months, value=months[t1.month - 1]),
        form.Dropdown('Year', years, value=str(t1.year)),
        form.Radio('Timeframe', ['Day', 'Week'], value='Day')
    )

    return (myform)


def ObtainDate(fac):
    while True:
        try:
            t = datetime.datetime.strptime(
                myform['Day'].value + ' ' + myform['Month'].value + ' ' + myform['Year'].value, "%d %B %Y")
            return (t + fac * datetime.timedelta(days=1))
        except ValueError:
            i = myform['Day'].args.index(myform['Day'].value)
            if not i == len(myform['Day'].args):
                myform['Day'].value = myform['Day'].args[i + fac]
            else:
                myform['Day'].value = myform['Day'].args[0]
                j = myform['Month'].args.index(myform['Month'].value)
                myform['Month'].value = myform['Month'].args[j + fac]


def handlepage(t):
    datestringEnd = "%s-%s-%s" % (t.year, t.month, t.day)
    remark = "%s %s %s" % (myform['Day'].value, myform['Month'].value, myform['Year'].value)

    if myform['Timeframe'].value == 'Week':
        t2 = t - datetime.timedelta(days=7)
        datestringBegin = "%s-%s-%s" % (t2.year, t2.month, t2.day)
        remark = "of week ending @ " + remark
    else:
        datestringBegin = datestringEnd

    try:
        con, cur = openMySQLdb()
        query = cur.execute(
            'SELECT datetime,watt FROM data WHERE DATE(datetime) BETWEEN "' + datestringBegin + '" and "' + datestringEnd + '"')
        raw_data = cur.fetchall()
        closeMySQLdb(con, cur)

        data = ""
        kwh = 0
        for i in raw_data:
            data += "[Date.UTC(%d,%d,%d,%d,%d),%d],\n" % (
                i[0].year, i[0].month - 1, i[0].day, i[0].hour, i[0].minute, i[1])
            kwh += float(i[1])

    except ValueError:
        print "MySQL error:", query
        data = ",\n"

    return (remark, data[:-2], kwh / (60000))


class index:
    def GET(self, name):
        fac = 0
        if name == "previous":
            fac = -1
        if name == "next":
            fac = 1
        if name == "update":
            updateyouless2mysql()
        if name == 'stop':
            app.stop()
            return ("Webserver is shutting down in 5 secs...")
        if name == 'last':
            t = getSpecialDate('MAX')
            myform['Year'].value = str(t.year)
            myform['Month'].value = myform['Month'].args[t.month - 1]
            myform['Day'].value = str(t.day)
        if name == 'first':
            t = getSpecialDate("MIN")
            myform['Year'].value = str(t.year)
            myform['Month'].value = myform['Month'].args[t.month - 1]
            myform['Day'].value = str(t.day)

        # get valid date plus or minus one day
        t = ObtainDate(fac)

        if t > getSpecialDate('MAX'):
            t = ObtainDate(0)

        if t < getSpecialDate('MIN'):
            t = ObtainDate(0)

        # store new valid date
        myform.Day.value = str(t.day)
        myform.Month.value = t.strftime("%B")
        myform.Year.value = str(t.year)

        # process and return result
        remark, data, kwh = handlepage(t)
        return render.formtest(myform, remark, data, "%.2f" % kwh, "%.2f" % (kwh * kwhprice))

    def POST(self, name):
        # process form
        if not myform.validates():
            return render.formtest(myform, "Not Found")
        else:
            # get date from form
            t = ObtainDate(0)

            # process and return result
            remark, data, kwh = handlepage(t)
            return render.formtest(myform, remark, data, "%.2f" % kwh, "%.2f" % (kwh * kwhprice))


if __name__ == "__main__":
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

    print "Youless energymonitor."
    print "Version  0.0.1 by Witteveder\n"

    # use configparser to get settings
    config = ConfigParser.ConfigParser()
    config.read('settings.ini')

    # read settings
    server = config.get('MYSQL SETTINGS', 'server')
    user = config.get('MYSQL SETTINGS', 'user')
    password = config.get('MYSQL SETTINGS', 'password')
    database_name = config.get('MYSQL SETTINGS', 'database_name')
    logfile_filename = config.get('SETTINGS', 'logfile_filename')
    ipaddress = config.get('SETTINGS', 'ipaddress')
    kwhprice = float(config.get('SETTINGS', 'kwhprice'))
    print "Using database: %s" % database_name

    # get latest readings that were not yet in the MySQL DB
    # updateyouless2mysql()

    # make webform elements
    myform = make_form()

    # do web.py server stuff
    render = web.template.render('templates/')
    urls = ('/(.*)', 'index')
    app = web.application(urls, globals())
    web.internalerror = web.debugerror
    app.run()
