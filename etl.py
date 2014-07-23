'''
Created on Jul 22, 2014

@author: pi314
'''
from optparse import OptionParser
from pi.mysql.client import mysqlConnection
import csv
from csv import DictReader
from pi.ibHelper.barfeed import RealTimeBar

def get_options():
    parser = OptionParser()
    parser.add_option('-f', '--filename', dest='filename', action='store',
        help='filename')
    parser.add_option('-l', '--loadToDB', dest='loadToDB', default=False, action='store_true',
                      help='Load file to Database')
    opts, args = parser.parse_args()
    return opts

def dailyEtl(options):
    con = mysqlConnection()
    input_file = DictReader(open(options.filename, 'rb'))
    for row in input_file:
        print row
        symbol = row["InstrumentID"]
        bar = RealTimeBar(row["TradingDay"], row["LastPrice"], row["Volume"])
        con.addBar(symbol, bar)

if __name__ == '__main__':
    dailyEtl(get_options())