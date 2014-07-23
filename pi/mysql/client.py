'''
Created on Jun 27, 2014

@author: tliu
'''
import MySQLdb
import csv
from pi.ibHelper.barfeed import RealTimeBar
from optparse import OptionParser
from pi import CONSTANTS


def addBarIntoDB(cur, symbol, bar):
    string = ("INSERT INTO `pi314`.`data` (`symbol`, `date`, `open`, `close`, `high`, `low`, `volume`)" + 
              "VALUES ('{0:s}', '{1:%Y-%m-%d %H:%M:%S}', '{2:f}', '{2:f}', '{2:f}', '{2:f}', '{3:f}')")
    queryStr = string.format(symbol, bar.getDateTime(), bar.getClose() ,bar.getVolume())
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
    con = MySQLdb.Connect(CONSTANTS.HOST,
                          CONSTANTS.USERNAME,
                          CONSTANTS.PASSWORD,
                          CONSTANTS.DATABASE)
    cur = con.cursor()
    filename = options.file
    count = 0
    with open(filename, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        next(reader, None)  # skip the header
        for row in reader:
            count = count + 1
            addBarIntoDB(cur, row[1], RealTimeBar(row[2], row[3], row[7]))
            if count%1000 == 0:
                con.commit()
                print "dump ",count," lines"
    con.commit()
    print "dump ",count," lines in DB"


if __name__ == '__main__':
    dumpFromFile(get_options())


class mysqlConnection:
    def __init__(self, 
                 host=CONSTANTS.HOST, 
                 username=CONSTANTS.USERNAME, 
                 password=CONSTANTS.PASSWORD, 
                 database=CONSTANTS.DATABASE):
        self.con = MySQLdb.Connect(host, username, password, database)
        self.__cur = self.con.cursor()

    def addBar(self, symbol, bar):
        string = ("INSERT INTO data (`symbol`, `date`, `open`, `close`, `high`, `low`, `volume`) " + 
                  "VALUES ('{0:s}', '{1:%Y-%m-%d %H:%M:%S}', '{2:f}', '{2:f}', '{2:f}', '{2:f}', '{3:f}')")
        queryStr = string.format(symbol, bar.getDateTime(), bar.getClose(), bar.getVolume())
        print queryStr
        self.__cur.execute(queryStr)
        self.con.commit()

    def addFromCSVFile(self, filename, header=True):
        with open(filename, 'rb') as csvfile:
            reader = csv.reader(csvfile)
            if header:
                next(reader, None)
            for row in reader:
                self.addBar(row[1], RealTimeBar(row[2], row[3], row[7]))
