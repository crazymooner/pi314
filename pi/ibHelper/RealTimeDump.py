'''
Created on Jun 27, 2014

@author: tliu
'''
import MySQLdb
import csv
from barfeed import RealTimeBar
from optparse import OptionParser
from datetime import datetime


def addBarIntoDB(cur, symbol, bar):
    string = ("INSERT INTO `ptrading`.`DATA` (`symbol`, `date`, `open`, `close`, `high`, `low`, `volumn`)" + 
              "VALUES ('{0:s}', '{1:%Y-%m-%d %H:%M:%S}', '{2:f}', '{2:f}', '{2:f}', '{2:f}', '{3:f}')")
    queryStr = string.format(symbol, bar.getDateTime(), bar.getClose() ,bar.getVolume())
    print queryStr
    cur.execute(queryStr)


def get_options():
    parser = OptionParser()
    add = parser.add_option
    add('-f', '--file', dest='file', action='store',
        help='the file to import')
    opts, args = parser.parse_args()
    return opts


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def dumpFromFile(options):
    con = MySQLdb.Connect('localhost', 'ptrading', 'igmgm', 'ptrading')
    cur = con.cursor()
    filename = options.file
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None) #skip the header
        for row in reader:
            addBarIntoDB(cur, row[1], RealTimeBar(row[2], row[3], row[7]))
    con.commit()

dumpFromFile(get_options())
