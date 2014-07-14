from pi.mysql import client
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime
from MdApi import *
from pi import CONSTANTS
from pyalgotrade import logger

logger = logger.getLogger("ctpClient")

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
        logger.info("OnFrontConnected")
        f = CThostFtdcReqUserLoginField()
        f.BrokerID = self.__broker_id
        f.UserUD = self.__user_id
        f.Password = self.__password
        self.__md.ReqUserLogin(f, self.__reqNum)
        self.__reqNum = self.__reqNum + 1

    def OnFrontDisconnected(self, *args):
        logger.info("OnFrontDisconnectet")
        logger.info("error code " + str(args[0]))
        logger.info("OnFrontDisconnectet End")

    def OnHeartBeatWarning(self, *args):
        print "OnHeartBeatWarning"
        print "time lapse ", args[0]
        print "OnHeartBeatWarning End"

    def OnRspUserLogin(self, *args):
        logger.info("OnRspUserLogin")
        if args:
            loginField = args[0]
            logger.info(loginField.TradingDay)
            logger.info(loginField.LoginTime)
            #construct contract ID
            date = datetime.strptime(loginField.TradingDay, "%Y%m%d")
            self.__md.SubscribeMarketData(self.__contactIDs, len(self.__contactIDs))
            logger.info("OnRspUserLogin End")

    def OnRspUserLogout(self, *args):
        print "OnRspUserLogout"
        print args
        print "OnRspUserLogout End"

    def OnRspError(self, *args):
        print "OnRspError"
        print args
        print "OnRspError End"

    def OnRspSubMarketData(self, *args):
        logger.info("OnRspSubMarketData")
        if args:
            rspInfoField = args[1]
            logger.info("Subscribe Instrument " + args[0].InstrumentID)
            logger.info("errorID " + str(rspInfoField.ErrorID))
            logger.info("errorMsg " + str(rspInfoField.ErrorMsg))
        logger.info("OnRspSubMarketData End")

    def OnRspUnSubMarketData(self, *args):
        logger.info("OnRspUnSubMarketData")
        if args:
            rspInfoField = args[1]
            logger.info("Subscribe Instrument " + args[0].InstrumentID)
            logger.info("errorID " + str(rspInfoField.ErrorID))
            logger.info("errorMsg " + str(rspInfoField.ErrorMsg))
        logger.info("OnRspUnSubMarketData End")

    def OnRtnDepthMarketData(self, *args):
        logger.info("OnRtnDepthMarketData")
        logger.info("id: "+args[0].InstrumentID)
        logger.info("TradingDay: " + args[0].TradingDay)
        logger.info("UpdateTime: " + args[0].UpdateTime)
        logger.info("LastPrice: " + str(args[0].LastPrice))
        logger.info("Volume: " + str(args[0].Volume))
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
        logger.info("OnRtnDepthMarketData End")


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
