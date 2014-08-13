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
import traceback


logger = logger.getLogger("mysqlconnection")

class mysqlConnection:
    def __init__(self, 
                 host=CONSTANTS.HOST, 
                 username=CONSTANTS.USERNAME, 
                 password=CONSTANTS.PASSWORD, 
                 database=CONSTANTS.DATABASE):
        self.__con = MySQLdb.Connect(host, username, password, database)

    def getConnection(self):
        return self.__con

    def __addBar(self, symbol, bar, cursor):
        string = ("INSERT INTO data (`symbol`, `date`,`milliseconds`, `open`, `close`, `high`, `low`, `volume`) " + 
                  "VALUES ('{0:s}', '{1:%Y-%m-%d %H:%M:%S}', '{4:d}','{2:f}', '{2:f}', '{2:f}', '{2:f}', '{3:f}')")
        queryStr = string.format(symbol, bar.getDateTime(), bar.getClose(), bar.getVolume(), bar.getMilliSeconds())
        cursor.execute(queryStr)

    def addFromCSVFile(self, filename):
        cursor = self.__con.cursor()
        input_file = DictReader(open(filename, 'rb'))
        count = 0
        for row in input_file:
            try:
                symbol = row["InstrumentID"]
                bar = RealTimeBar(row["TradingDay"], row["LastPrice"], row["Volume"], row["UpdateMillisec"])
                if count%1000 == 0:
                    logger.info("dump " + str(count) + " rows")
                self.__addBar(symbol, bar, cursor)
                count = count + 1
            except Exception:
                traceback.print_exc()
                logger.error("error line: " + " instrument: " + row["InstrumentID"] + 
                             " TradingDay: " + row["TradingDay"] +" LastPrice: "+ row["LastPrice"] +
                             " Volume: "+ row["Volume"])
                continue
        self.__con.commit()
        cursor.close()

    def deleteDataFromDate(self, date):
        cursor = self.__con.cursor()
        query = "delete from data where date(date) >= '{0:s}' and date(date) <= '{0:s}'"
        query = query.format(date)
        logger.info(query)
        cursor.execute(query)
        self.__con.commit()
        cursor.close()

    def getBars(self, frequency, instrument, fromDateTime, toDateTime):
        sql = ("select bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume" +
              " from {0:s} bar where bar.symbol = '{1:s}'" + 
              " and date(bar.date) >= '{2:s}'" + 
              " and date(bar.date) <= '{3:s}'" + 
              " order by bar.date asc")
        sql = sql.format(frequency + "_data", instrument, fromDateTime, toDateTime)
        cursor = self.__con.cursor()
        logger.info(sql)
        cursor.execute(sql)
        ret = []
        for row in cursor:
            ret.append(bar.BasicBar(row[0],row[1],row[2],row[3],row[4],row[5],0,frequency))
        cursor.close()
        for i in ret:
            print i.getClose()
        return ret

    def backFill(self, freq,filename, startDate, endDate):
        if freq == 86400:
            final_table = "1day_data"
        elif freq == 1800:
            final_table = "30mins_data"
        elif freq == 300:
            final_table = "5mins_data"
        cursor = self.__con.cursor() 
        cleanup_qry_text = ("""DELETE FROM %s WHERE date(date) >= '%s' and date(date) <= '%s'""" % (final_table, startDate, endDate))
        logger.info(cleanup_qry_text)
        cursor.execute(cleanup_qry_text)

        insert_qry_text = """INSERT INTO {0:s} (symbol, date, open, close, high, low, volume) 
                                select t0.symbol, t0.new_date date, avg(t2.open) open, avg(t1.close) close, avg(t0.high) high, 
                                avg(t0.low) low, avg(t0.volume) volume 
                                from (select data.symbol symbol,from_unixtime((floor((unix_timestamp(data.date) / {1:d})) * {1:d}){2:s}) new_date, 
                                        max(data.high) high, min(data.low) low, max(data.date) max_ts, min(data.date) min_ts, 
                                        avg(data.volume) volume 
                                        from data where date(date) >= '{3:s}' and date(date) <= '{4:s}' group by 1,2) t0 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) >= '{3:s}' and date(date) <= '{4:s}' 
                                    group by 1,2) t1 
                                on t0.symbol = t1.symbol and t0.max_ts = t1.date 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) >= '{3:s}' and date(date) <= '{4:s}' 
                                    group by 1,2) t2 
                                on t0.symbol = t2.symbol and t0.min_ts = t2.date group by 1,2""" 
        if freq == CONSTANTS.ONE_DAY:
            insert_qry_text = insert_qry_text.format(final_table, freq, '+8*3600', startDate, endDate)
        else:
            insert_qry_text = insert_qry_text.format(final_table, freq, '', startDate, endDate)
        logger.info(insert_qry_text)
        cursor.execute(insert_qry_text)
        self.__con.commit()
        cursor.close()
        text_file = open(filename, "a")
        text_file.writelines("Back fill job %s started at: %s, complete at: %s , end date %s\n" % (final_table, startDate, datetime.now(), endDate))
        text_file.close()
        
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
        cursor = self.__con.cursor() 
        cleanup_qry_text = ("""DELETE FROM %s WHERE date(date) = '%s'""" % (final_table, yesterday))
        logger.info(cleanup_qry_text)
        cursor.execute(cleanup_qry_text)

        insert_qry_text = """INSERT INTO {0:s} (symbol, date, open, close, high, low, volume) 
                                select t0.symbol, t0.new_date date, avg(t2.open) open, avg(t1.close) close, avg(t0.high) high, 
                                avg(t0.low) low, avg(t0.volume) volume 
                                from (select data.symbol symbol,from_unixtime((floor((unix_timestamp(data.date) / {1:d})) * {1:d}){2:s}) new_date, 
                                        max(data.high) high, min(data.low) low, max(data.date) max_ts, min(data.date) min_ts, 
                                        avg(data.volume) volume 
                                        from data where date(date) = '{3:s}' group by 1,2) t0 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) = '{3:s}' 
                                    group by 1,2) t1 
                                on t0.symbol = t1.symbol and t0.max_ts = t1.date 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) = '{3:s}' 
                                    group by 1,2) t2 
                                on t0.symbol = t2.symbol and t0.min_ts = t2.date group by 1,2""" 
        if freq == CONSTANTS.ONE_DAY:
            insert_qry_text = insert_qry_text.format(final_table, freq, '+8*3600', yesterday)
        else:
            insert_qry_text = insert_qry_text.format(final_table, freq, '', yesterday)
        cursor.execute(insert_qry_text)
        logger.info(insert_qry_text)
        self.__con.commit()
        cursor.close()
        text_file = open(filename, "a")
        text_file.writelines("Job %s started at: %s, completed at: %s with last_full_date: %s \n" % (final_table, start_time, datetime.now() , yesterday))
        text_file.close()


def get_options():
    parser = OptionParser()
    add = parser.add_option
    add('-f', '--file', dest='file', action='store',
        help='the file to import')
    opts, args = parser.parse_args()
    return opts

def dumpFromFile(options):
    con = mysqlConnection()
    con.addFromCSVFile(options.file)


if __name__ == '__main__':
    dumpFromFile(get_options())

