from pyalgotrade import strategy
from pi.mysql.MysqlFeed import MysqlFeed
from pyalgotrade.technical import ma
from pyalgotrade.technical import cross
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.stratanalyzer import sharpe
from pyalgotrade.stratanalyzer import drawdown
from pyalgotrade.stratanalyzer import trades

'''
class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, newpara):
        strategy.BacktestingStrategy.__init__(self, feed, 100000)
        self.__position = None
        self.__instrument = instrument
        # self.__indicator1 = lib.func(feed[instrument].getCloseDataSeries(), ...)

    def onEnterOk(self, position):
        pass
        #
        #

    def onEnterCanceled(self, position):
        pass
        #
        #

    def onExitOk(self, position):
        pass
        #
        #

    def onExitCanceled(self, position):
        pass
        #
        #
'''
class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument, smaPeriod):
        strategy.BacktestingStrategy.__init__(self, feed, 100000)
        self.__position = None
        self.__instrument = instrument
        # We won't use adjusted close values instead of regular close values.
        #self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getCloseDataSeries(), smaPeriod)

    def onEnterOk(self, position):
        execInfo = position.getEntryOrder().getExecutionInfo()
        self.info("BUY at $%.2f" % (execInfo.getPrice()))

    def onEnterCanceled(self, position):
        self.__position = None

    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None

    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()

    def getSMA(self):
        return self.__sma

    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return

        bar = bars[self.__instrument]
        self.info("%s %s" % (bar.getClose(), self.__sma[-1]))
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getClose() > self.__sma[-1]:
                # Enter a buy market order for 10 shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument, 10, True)
        # Check if we have to exit the position.
        elif bar.getClose() < self.__sma[-1]:
            self.__position.exitMarket()

def run_strategy(smaPeriod):
    # Load the mysql feed from mysql database
    feed = MysqlFeed("30mins")
    feed.loadBars("IF1408", "2014-07-15", "2014-07-23")

    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, "IF1408", smaPeriod)
    
    # Attach a returns analyzers to the strategy.
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    sharpeRatioAnalyzer = sharpe.SharpeRatio()
    myStrategy.attachAnalyzer(sharpeRatioAnalyzer)
    drawDownAnalyzer = drawdown.DrawDown()
    myStrategy.attachAnalyzer(drawDownAnalyzer)
    tradesAnalyzer = trades.Trades()
    myStrategy.attachAnalyzer(tradesAnalyzer)
    
    plt = plotter.StrategyPlotter(myStrategy)
    # Plot the strategy returns at each bar.
    plt.getInstrumentSubplot("IF1408").addDataSeries("SMA", myStrategy.getSMA())
    plt.getOrCreateSubplot("returns").addDataSeries(
        "Net return", returnsAnalyzer.getReturns())
    plt.getOrCreateSubplot("returns").addDataSeries(
        "Cum. return", returnsAnalyzer.getCumulativeReturns())
    
    myStrategy.run()
    print "Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity()
    myStrategy.info("Final portfolio value: $%.2f" % myStrategy.getResult())
    myStrategy.info("Cumulative returns: %.2f %%" % (returnsAnalyzer.getCumulativeReturns()[-1] * 100))
    myStrategy.info("Sharpe ratio: %.2f" % (sharpeRatioAnalyzer.getSharpeRatio(0.05)))
    myStrategy.info("Max. drawdown: %.2f %%" % (drawDownAnalyzer.getMaxDrawDown() * 100))
    myStrategy.info("Longest drawdown duration: %s" % (drawDownAnalyzer.getLongestDrawDownDuration()))

    print
    print "Total trades: %d" % (tradesAnalyzer.getCount())
    if tradesAnalyzer.getCount() > 0:
        profits = tradesAnalyzer.getAll()
        print "Avg. profit: $%2.f" % (profits.mean())
        print "Profits std. dev.: $%2.f" % (profits.std())
        print "Max. profit: $%2.f" % (profits.max())
        print "Min. profit: $%2.f" % (profits.min())
        returns1 = tradesAnalyzer.getAllReturns()
        print "Avg. return: %2.f %%" % (returns1.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns1.std() * 100)
        print "Max. return: %2.f %%" % (returns1.max() * 100)
        print "Min. return: %2.f %%" % (returns1.min() * 100)

    print
    print "Profitable trades: %d" % (tradesAnalyzer.getProfitableCount())
    if tradesAnalyzer.getProfitableCount() > 0:
        profits = tradesAnalyzer.getProfits()
        print "Avg. profit: $%2.f" % (profits.mean())
        print "Profits std. dev.: $%2.f" % (profits.std())
        print "Max. profit: $%2.f" % (profits.max())
        print "Min. profit: $%2.f" % (profits.min())
        returns2 = tradesAnalyzer.getPositiveReturns()
        print "Avg. return: %2.f %%" % (returns2.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns2.std() * 100)
        print "Max. return: %2.f %%" % (returns2.max() * 100)
        print "Min. return: %2.f %%" % (returns2.min() * 100)
    
    print
    print "Unprofitable trades: %d" % (tradesAnalyzer.getUnprofitableCount())
    if tradesAnalyzer.getUnprofitableCount() > 0:
        losses = tradesAnalyzer.getLosses()
        print "Avg. loss: $%2.f" % (losses.mean())
        print "Losses std. dev.: $%2.f" % (losses.std())
        print "Max. loss: $%2.f" % (losses.min())
        print "Min. loss: $%2.f" % (losses.max())
        returns3 = tradesAnalyzer.getNegativeReturns()
        print "Avg. return: %2.f %%" % (returns3.mean() * 100)
        print "Returns std. dev.: %2.f %%" % (returns3.std() * 100)
        print "Max. return: %2.f %%" % (returns3.max() * 100)
        print "Min. return: %2.f %%" % (returns3.min() * 100)
    plt.plot()

if __name__ == '__main__':
    run_strategy(3)