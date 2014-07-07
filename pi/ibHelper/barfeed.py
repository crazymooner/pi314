from pyalgotrade import bar
from datetime import datetime

class RealTimeBar(bar.Bar):
    # Optimization to reduce memory footprint.
    __slots__ = ('__dateTime', '__price', '__amount')

    def __init__(self, dateTime, price, volume):
        self.__dateTime = datetime.strptime(dateTime, "%Y-%m-%d %H:%M:%S")
        self.__price = float(price)
        self.__amount = float(volume)

    def __setstate__(self, state):
        (self.__dateTime, self.__price, self.__amount) = state

    def __getstate__(self):
        return (self.__dateTime, self.__price, self.__amount)

    def getFrequency(self):
        return bar.Frequency.TRADE

    def getDateTime(self):
        return self.__dateTime

    def getOpen(self, adjusted=False):
        return self.__price

    def getHigh(self, adjusted=False):
        return self.__price

    def getLow(self, adjusted=False):
        return self.__price

    def getClose(self, adjusted=False):
        return self.__price

    def getVolume(self):
        return self.__amount

    def getAdjClose(self):
        return None

    def getTypicalPrice(self):
        return self.__price