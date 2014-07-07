# -*- coding: utf-8 -*-
"""
Created on Wed Jun 18 11:05:22 2014

@author: tliu
"""

from pyalgotrade import strategy
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns


class Strategy(strategy.BacktestingStrategy):

    def __init__(self, feed, instrument, smaPeriod, cash=1000):
        strategy.BacktestingStrategy.__init__(self, feed, cash)
        self.__instrument = instrument
        self.__position = None
        # We'll use adjusted close values instead of regular close values.
        # self.setUseAdjustedValues(True)
        self.__adjClose = feed[instrument].getAdjCloseDataSeries()
        self.__sma = ma.SMA(self.__adjClose, smaPeriod)

    def getSMA(self):
        return self.__sma

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def onBars(self, bars):
        # If a position was not opened, check if we should enter a long
        # position.
        if self.__position is None:
            if cross.cross_above(self.__adjClose, self.__sma) > 0:
                # Enter a buy market order for 10 shares. The order is good
                # till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif cross.cross_below(self.__adjClose, self.__sma) > 0:
            self.__position.exitMarket()


if __name__ == '__main__':
    # Load the yahoo feed from the CSV file
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV("orcl", "orcl-2000.csv")

    # Evaluate the strategy with the feed's bars.
    myStrategy = Strategy(feed, "orcl", 20)

    # Attach a returns analyzers to the strategy.
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)

    # Attach the plotter to the strategy.
    plt = plotter.StrategyPlotter(myStrategy)
    # Include the SMA in the instrument's subplot to get it displayed along
    # with the closing prices.
    plt.getInstrumentSubplot("orcl").addDataSeries("SMA", myStrategy.getSMA())
    # Plot the strategy returns at each bar.
    plt.getOrCreateSubplot("returns").addDataSeries(
        "Net return", returnsAnalyzer.getReturns())
    plt.getOrCreateSubplot("returns").addDataSeries(
        "Cum. return", returnsAnalyzer.getCumulativeReturns())

    # Run the strategy.
    myStrategy.run()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())

    # Plot the strategy.
    plt.plot()
