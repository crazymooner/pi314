import MySQLdb
from datetime import datetime, timedelta
 
class ETLHandler():
    def __init__(self):
        pass
    def connect(self):
        self.con = MySQLdb.connect(host='pi314.cn6qs5axgapc.us-west-1.rds.amazonaws.com', user='pi314admin', passwd='pi314159', db='pi314')
        return self.con
    def disconnect(self):
        self.con.close()
    def dailyupdate(self,freq):
        con = self.connect()
        cur = con.cursor()
        if freq == 86400:
            final_table = "1day_data"
        elif freq == 1800:
            final_table = "30mins_data"
        elif freq == 300:
            final_table = "5mins_data"
        start_time = datetime.now()
        last_updated_date_qry_text = ("""SELECT max(date(date)) from data""")
        cur.execute(last_updated_date_qry_text)
        last_updated_date = cur.fetchone()
        if len(last_updated_date) < 1:
            print "no last updated date found!"
            return
        
        last_full_date = datetime.strptime(last_updated_date[0], "%Y-%m-%d") - timedelta(1)
        last_full_date = last_full_date.strftime("%Y-%m-%d")

        cleanup_qry_text = ("""DELETE FROM %s WHERE date(date) >= '%s'""" % (final_table, last_full_date))
        print cleanup_qry_text
        cur.execute(cleanup_qry_text)

        insert_qry_text = ("""INSERT INTO %s (symbol, date, open, close, high, low, volume) 
                                select t0.symbol, t0.new_date date, avg(t2.open) open, avg(t1.close) close, avg(t0.high) high, 
                                avg(t0.low) low, avg(t0.volume) volume 
                                from (select data.symbol symbol,from_unixtime((floor((unix_timestamp(data.date) / %i)) * %i)) new_date, 
                                        max(data.high) high, min(data.low) low, max(data.date) max_ts, min(data.date) min_ts, 
                                        avg(data.volume) volume 
                                        from data where date(date) >= '%s' group by 1,2) t0 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) >= '%s' 
                                    group by 1,2) t1 
                                on t0.symbol = t1.symbol and t0.max_ts = t1.date 
                                join 
                                    (select symbol, date, avg(data.close) close, avg(data.open) open from data where date(date) >= '%s' 
                                    group by 1,2) t2 
                                on t0.symbol = t2.symbol and t0.min_ts = t2.date group by 1,2""" 
                                % (final_table, freq, freq, last_full_date, last_full_date, last_full_date))
        cur.execute(insert_qry_text)
        print insert_qry_text
        cur.close()
        self.disconnect()
        text_file = open("/Users/tony/Dropbox/etl/etl_logs.txt", "a")
        text_file.writelines("Job %s started at: %s, completed at: %s with last_full_date: %s \n" % (final_table, start_time, datetime.now() , last_full_date))
        text_file.close()
    
    def main(self):
        self.dailyupdate(freq = 86400)
        self.dailyupdate(freq = 1800)
        self.dailyupdate(freq = 300)
        print "All ETLs DONE!!!" 
 
if __name__ == '__main__':
    a = ETLHandler()
    a.main()