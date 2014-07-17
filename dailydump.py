'''
Created on Jul 17, 2014

@author: tliu
'''
from datetime import datetime, date, time, timedelta
from time import sleep
from apscheduler.scheduler import Scheduler
from dateutil import tz
import atexit
from subprocess import call
import logging
logging.basicConfig()

def runDateDump():
    call("python CtpRealTimeDump.py -d", shell=True)

def main():
    d = date.today()
    t = time(00,30)
    startDate = datetime.combine(d,t)
    startDate = startDate.replace(tzinfo=tz.tzutc())
    startDate = startDate.astimezone(tz.tzlocal())
    timeStr = startDate.strftime("%Y-%m-%d %H:%M:%S")
    print timeStr
    startDate = datetime.strptime(timeStr, "%Y-%m-%d %H:%M:%S")
    if (datetime.now() - startDate) > timedelta(seconds=1):
        startDate = startDate + timedelta(days=1)
    sched = Scheduler()
    sched.start()
    sched.add_interval_job(runDateDump, days=1, start_date=startDate.strftime("%Y-%m-%d %H:%M:%S"))
    sched.print_jobs()
    while True:
        sleep(1)
        print "."
    atexit.register(lambda: sched.shutdown(wait=True))

if __name__ == '__main__':
    main()