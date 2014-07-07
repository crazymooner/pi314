'''
Created on Jun 24, 2014

@author: tliu
'''

from ibHelper.ibClient import ibClient
from ibHelper.api import make_contract
from optparse import OptionParser
from ib.ext.Contract import Contract
from time import strftime


def get_options():
    parser = OptionParser()
    add = parser.add_option
    add('-s', '--symbol', dest='symbol', action='store',
        help='the stock symbol to dump')
    add('-t', '--time', dest='time', action='store', default='current',
        help='End date, the format is yyyymmdd HH:mm:ss ttt, ttt is optional')
    add('-d', '--duration', dest='duration', action='store',
        help=('duration can be (integer)[space](S\D\W\\M\Y)'),default='2 M')
    add('-b', '--barSize', dest='barSize', default='1 day',
        help='value can be 1 day, 1 hour, 30 mins, 15mins, 1 mins, 30 secs ...')
    add('-l', '--longDate', dest='longDate', default = 1, type='int',
        help='return date as long number, 1 is str, 2 is long')
    opts, args = parser.parse_args()
    return opts


def dump(options):
    contract = make_contract(options.symbol)
    endtime = options.time
    if options.time is 'current':
        endtime =  strftime('%Y%m%d %H:%M:%S')
    client = ibClient()
    client.ReqHistroyData(reqContract = contract,
                          reqEndDateTime = endtime,
                          reqDurationStr = options.duration,
                          reqBarSizeSetting = options.barSize,
                          reqFormatDate = options.longDate)
    
dump(get_options())