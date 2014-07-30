'''
Created on Jul 24, 2014

@author: pi314
'''

from pyalgotrade.barfeed import dbfeed
from pyalgotrade.barfeed import membf
from pyalgotrade import bar
from pyalgotrade import dataseries
from pyalgotrade.utils import dt

import sqlite3
import os
from pi.mysql.client import mysqlConnection


class MysqlFeed(membf.BarFeed):
    def __init__(self, frequency, maxLen=dataseries.DEFAULT_MAX_LEN):
        membf.BarFeed.__init__(self, frequency, maxLen)
        self.__db = mysqlConnection()

    def barsHaveAdjClose(self):
        return False

    def getDatabase(self):
        return self.__db

    def loadBars(self, instrument, fromDateTime=None, toDateTime=None):
        bars = self.__db.getBars(self.getFrequency(), instrument, fromDateTime, toDateTime)
        self.addBarsFromSequence(instrument, bars)

if __name__ == '__main__':
    feed = MysqlFeed("5mins")
    feed.loadBars("IF1408", "2014-07-01", "2014-07-20")