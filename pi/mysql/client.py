'''
Created on Jun 27, 2014

@author: tliu
'''
import MySQLdb
import csv
from pi.ibHelper.barfeed import RealTimeBar
from optparse import OptionParser
from pi import CONSTANTS
from datetime import datetime, timedelta
from pyalgotrade import bar
from csv import DictReader
from pyalgotrade import logger

logger = logger.getLogger("mysqlconnection")


def normalize_instrument(instrument):
    return instrument.upper()

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
    logger.info("dump " + str(count) + " lines in DB")


if __name__ == '__main__':
    dumpFromFile(get_options())


class mysqlConnection:
    def __init__(self, 
                 host=CONSTANTS.HOST, 
                 username=CONSTANTS.USERNAME, 
                 password=CONSTANTS.PASSWORD, 
                 database=CONSTANTS.DATABASE):
        self.__con = MySQLdb.Connect(host, username, password, database)
        self.__cur = self.__con.cursor()

    def getConnection(self):
        return self.__con

    def __addBar(self, symbol, bar):
        string = ("INSERT INTO data (`symbol`, `date`, `open`, `close`, `high`, `low`, `volume`) " + 
                  "VALUES ('{0:s}', '{1:%Y-%m-%d %H:%M:%S}', '{2:f}', '{2:f}', '{2:f}', '{2:f}', '{3:f}')")
        queryStr = string.format(symbol, bar.getDateTime(), bar.getClose(), bar.getVolume())
        self.__cur.execute(queryStr)

    def addFromCSVFile(self, filename):
        input_file = DictReader(open(filename, 'rb'))
        count = 0
        for row in input_file:
            symbol = row["InstrumentID"]
            bar = RealTimeBar(row["TradingDay"], row["LastPrice"], row["Volume"])
            if count%1000 == 0:
                logger.info("dump " + str(count) + " rows")
            self.__addBar(symbol, bar)
            count = count + 1
        self.__con.commit()

    def deleteDataFroDate(self, date):
        query = "delete from data where date(date) >= '{0:s}' and date(date) <= '{0:s}'"
        query = query.format(date)
        logger.info(query)
        self.__cur.execute(query)
        self.__con.commit()

    def getBars(self, frequency, instrument, fromDateTime, toDateTime):
        instrument = normalize_instrument(instrument)
        sql = ("select bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume" +
              " from {0:s} bar where bar.symbol = '{1:s}'" + 
              " and date(bar.date) >= '{2:s}'" + 
              " and date(bar.date) <= '{3:s}'" + 
              " order by bar.date asc")
        sql = sql.format(frequency + "_data", instrument, fromDateTime, toDateTime)
        cursor = self.__cur
        logger.info(sql)
        cursor.execute(sql)
        ret = []
        for row in cursor:
            ret.append(bar.BasicBar(row[0],row[1],row[2],row[3],row[4],row[5],0,frequency))
        cursor.close()
        for i in ret:
            print i.getClose()
        return ret

    def dailyupdate(self, freq, filename, yesterday):
        if freq == 86400:
            final_table = "1day_data"
        elif freq == 1800:
            final_table = "30mins_data"
        elif freq == 300:
            final_table = "5mins_data"
        start_time = datetime.now()
        #last_updated_date_qry_text = ("""SELECT max(date(date)) from data""")
        #self.__cur.execute(last_updated_date_qry_text)
        #last_updated_date = self.__cur.fetchone()
        #if len(last_updated_date) < 1:
        #    print "no last updated date found!"
        #    return
        
        
        #last_full_date = datetime.strptime(last_updated_date[0], "%Y-%m-%d") - timedelta(1)
        #last_full_date = last_full_date.strftime("%Y-%m-%d")

        cleanup_qry_text = ("""DELETE FROM %s WHERE date(date) = '%s'""" % (final_table, yesterday))
        logger.info(cleanup_qry_text)
        self.__cur.execute(cleanup_qry_text)

        insert_qry_text = ("""INSERT INTO %s (symbol, date, open, close, high, low, volume) 
                                select t0.symbol, t0.new_date date, avg(t2.open) open, avg(t1.close) close, avg(t0.high) high, 
                                avg(t0.low) low, avg(t0.volume) volume 
                                from (select data.symbol symbol,from_unixtime((floor((unix_timestamp(data.date) / %i)) * %i)) new_date, 
                                        max(data.high) high, min(data.low) low, max(data.date) max_ts, min(data.date) min_ts, 
                                        avg(data.volume) volume 
                                        from data where date(date) = '%s' group by 1,2) t0 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) = '%s' 
                                    group by 1,2) t1 
                                on t0.symbol = t1.symbol and t0.max_ts = t1.date 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) = '%s' 
                                    group by 1,2) t2 
                                on t0.symbol = t2.symbol and t0.min_ts = t2.date group by 1,2""" 
                                % (final_table, freq, freq, yesterday, yesterday, yesterday))
        self.__cur.execute(insert_qry_text)
        logger.info(insert_qry_text)
        self.__con.commit()
        text_file = open(filename, "a")
        text_file.writelines("Job %s started at: %s, completed at: %s with last_full_date: %s \n" % (final_table, start_time, datetime.now() , yesterday))
        text_file.close()
