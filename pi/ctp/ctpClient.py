from pi.mysql import client
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime
from MdApi import *
from pi import CONSTANTS


class Quote(CThostFtdcMdSpi):
    def __init__(self, mdapi, broker_id, user_id, password):
        CThostFtdcMdSpi.__init__(self)
        self.md = mdapi
        self.reqNum = 0
        self.contactIDs = []
        self.__insertIntoMysql = False
        self.__volume = 0

    def isDumpToMysql(self, dump=True):
        self.__insertIntoMysql = dump

    def addSymbol(self, symbol):
        self.contactIDs.append(symbol)

    def getSuper(self):
        return super

    def OnFrontConnected(self):
        print "OnFrontConnected"
        f = CThostFtdcReqUserLoginField()
        f.BrokerID = self.broker_id
        f.UserUD = self.user_id
        f.Password = self.password
        self.md.ReqUserLogin(f, self.reqNum)
        self.reqNum = self.reqNum + 1

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
        self.md.SubscribeMarketData(self.contactIDs, len(self.contactIDs))
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
        if self.__insertIntoMysql:
            mysqlcon = client.mysqlConnection(CONSTANTS.HOST,
                                              CONSTANTS.USERNAME,
                                              CONSTANTS.PASSWORD,
                                              CONSTANTS.DATABASE)
            date = datetime.datetime.strptime(args[0].TradingDay, "%Y%m%d")
            dateStr = date.strftime("%Y-%m-%d")
            dateStr = dateStr + " " + args[0].UpdateTime
            mysqlcon.addBar(args[0].InstrumentID,
                            RealTimeBar(dateStr,
                                        args[0].LastPrice,
                                        args[0].Volume - self.__volume))
            self.__volume = args[0].Volume

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
        pass


class MdApiClient:
    def __init__(self, front_addr="tcp://ctp1-md5.citicsf.com:41213",
                 broker_id="1017", user_id="00000071", password="123456"):
        self.md = CThostFtdcMdApi_CreateFtdcMdApi("./qlog")
        self.md.RegisterSpi(Quote(self.md, broker_id, user_id, password))
        self.md.RegisterFront(front_addr)

    def run(self):
        self.md.Init()
        self.md.Join()
