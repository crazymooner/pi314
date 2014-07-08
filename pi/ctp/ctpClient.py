from pi.mysql import client
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime
from MdApi import *
from pi import CONSTANTS



class Quote(CThostFtdcMdSpi):
    def __init__(self, mdapi, broker_id, user_id, password):
        CThostFtdcMdSpi.__init__(self)
        self.__reqNum = 0
        self.__contactIDs = []
        self.__insertIntoMysql = False
        self.__md = mdapi
        self.__broker_id = broker_id
        self.__user_id = user_id
        self.__password = password
        self.__mysqlCon = None
    
    def isDumpToMysql(self, dump=True):
        self.__insertIntoMysql = dump

    def addSymbol(self, symbol):
        self.__contactIDs.append(symbol)

    def getSuper(self):
        return super

    def OnFrontConnected(self):
        print "OnFrontConnected"
        f = CThostFtdcReqUserLoginField()
        f.BrokerID = self.__broker_id
        f.UserUD = self.__user_id
        f.Password = self.__password
        self.__md.ReqUserLogin(f, self.__reqNum)
        self.__reqNum = self.__reqNum + 1

    def OnFrontDisconnected(self, *args):
        print "OnFrontDisconnectet"
        print args
        print "OnFrontDisconnectet End"

    def OnHeartBeatWarning(self, *args):
        print "OnHeartBeatWarning"
        print args
        print "OnHeartBeatWarning End"

    def OnRspUserLogin(self, *args):
        print "OnRspUserLogin"
        print self.__contactIDs
        self.__md.SubscribeMarketData(self.__contactIDs, len(self.__contactIDs))
        print "OnRspUserLogin End"

    def OnRspUserLogout(self, *args):
        print "OnRspUserLogout"
        print args
        print "OnRspUserLogout End"

    def OnRspError(self, *args):
        print "OnRspError"
        print args
        print "OnRspError End"

    def OnRspSubMarketData(self, *args):
        print "OnRspSubMarketData"
        print args
        print "OnRspSubMarketData End"

    def OnRspUnSubMarketData(self, *args):
        print "OnRspUnSubMarketData"
        print args
        print "OnRspUnSubMarketData End"

    def OnRtnDepthMarketData(self, *args):
        print "OnRtnDepthMarketData"
        print "id: ", args[0].InstrumentID
        print "LastPrice: ", args[0].LastPrice
        print "TradingDay: ", args[0].TradingDay
        print "UpdateTime: ", args[0].UpdateTime
        print "OpenPrice: ", args[0].OpenPrice
        print "HighestPrice: ", args[0].HighestPrice
        print "LowestPrice: ", args[0].LowestPrice
        print "Volume: ", args[0].Volume
        print "ClosePrice: ", args[0].ClosePrice
        if self.__insertIntoMysql:
            if self.__mysqlCon == None:
                self.__mysqlCon = client.mysqlConnection(CONSTANTS.HOST,
                                                         CONSTANTS.USERNAME,
                                                         CONSTANTS.PASSWORD,
                                                         CONSTANTS.DATABASE)
            date = datetime.strptime(args[0].TradingDay, "%Y%m%d")
            dateStr = date.strftime("%Y-%m-%d")
            dateStr = dateStr + " " + args[0].UpdateTime
            self.__mysqlCon.addBar(args[0].InstrumentID,
                            RealTimeBar(dateStr,
                                        args[0].LastPrice,
                                        args[0].Volume))
            #self.__mysqlCon.commit()
        pass


class MdApiClient:
    def __init__(self, front_addr="tcp://ctp1-md5.citicsf.com:41213",
                 broker_id="1017", user_id="00000071", password="123456"):
        self.__md = CThostFtdcMdApi_CreateFtdcMdApi("./qlog")
        self.__front_addr = front_addr
        self.__broker_id = broker_id
        self.__user_id = user_id
        self.__password = password
        self.__quote = Quote(self.__md, self.__broker_id, self.__user_id, self.__password)

    def addSymbol(self, symbol):
        self.__quote.addSymbol(symbol)

    def dumpToMysql(self, isTrue):
        self.__quote.isDumpToMysql(isTrue)

    def run(self):
        self.__quote.OnRspUserLogin()
        self.__md.RegisterSpi(self.__quote)
        self.__md.RegisterFront(self.__front_addr)
        self.__md.Init()
        self.__md.Join()
