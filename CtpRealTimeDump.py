from pi.ctp.ctpClient import MdApiClient
from optparse import OptionParser
from datetime import datetime, date, time, timedelta
from time import sleep
from apscheduler.scheduler import Scheduler
import atexit

def get_options():
    parser = OptionParser()
    add = parser.add_option
    add('-d', '--dumpToMysql', dest='dump', default=False, action='store_true',
        help='dump data to MySQL')
    opts, args = parser.parse_args()
    return opts

def dataDump(options):
    print "start, dump ", options.dump
    mdclient = MdApiClient()
    mdclient.addSymbol("IF1407")
    mdclient.addSymbol("IF1408")
    mdclient.addSymbol("IF1409")
    mdclient.addSymbol("IF1410")
    mdclient.addSymbol("IF1411")
    mdclient.addSymbol("IF1412")
    mdclient.addSymbol("IF1501")
    mdclient.addSymbol("IF1502")
    mdclient.addSymbol("IF1503")
    mdclient.addSymbol("IF1504")
    mdclient.dumpToMysql(options.dump)
    mdclient.run()

def main(options):
    d = date.today()
    t = time(16,30)
    startDate = datetime.combine(d,t)
    if (datetime.now() - startDate) > timedelta(seconds=1):
        startDate = startDate + timedelta(days=1)
        
    print "dump ", options.dump
    sched = Scheduler()
    sched.start()
    sched.add_interval_job(dataDump, days=1, start_date=startDate.strftime("%Y-%m-%d %H:%M:%S"), args=[options])
    sched.print_jobs()
    while True:
        sleep(60*10)
        print "."
    atexit.register(lambda: sched.shutdown(wait=True))
    
    
if __name__ == "__main__":
    main(get_options())
