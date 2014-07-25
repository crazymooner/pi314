'''
Created on Jul 22, 2014

@author: pi314
'''
from optparse import OptionParser
from pi.mysql.client import mysqlConnection
from csv import DictReader
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime, timedelta

def get_options():
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename', action='store',
        help='filename')
    parser.add_option('-l', '--log', dest='logFilename', action='store',
        help='logFilename')
    parser.add_option('-t', '--datetime', dest='datetime', action='store',
                      default=(datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                      help='datetime')
    parser.add_option('-d', '--dailyETL', dest='dailyETL', default=False, action='store_true',
                      help='Dump from Dropbox file to DB')
    parser.add_option('-v', '--dailyViewETL', dest='dailyViewETL', default=False, action='store_true',
                      help='Generate View from DATA Table')
    opts, args = parser.parse_args()
    return opts

def dailyEtl(options):
    con = mysqlConnection()
    input_file = DictReader(open(options.datetime + ".csv", 'rb'))
    for row in input_file:
        symbol = row["InstrumentID"]
        bar = RealTimeBar(row["TradingDay"], row["LastPrice"], row["Volume"])
        con.addBar(symbol, bar)

def dailyViewEtl(options):
    con = mysqlConnection()
    con.dailyupdate(86400, options.logFilename, options.datetime)
    con.dailyupdate(1800, options.logFilename, options.datetime)
    con.dailyupdate(300, options.logFilename, options.datetime)
    print "All ETLs DONE!!!" 

if __name__ == '__main__':
    options = get_options()
    if options.dailyETL:
        dailyEtl(options)
    if options.dailyViewETL:
        dailyViewEtl(options)