from pi.mysql import client
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime, timedelta
from MdApi.MdApi import *
from pi import CONSTANTS
from pyalgotrade import logger

logger = logger.getLogger("ctpClient")

class Quote(CThostFtdcMdSpi):
    def __init__(self, mdapi, broker_id, user_id, password):
        CThostFtdcMdSpi.__init__(self)
        self.__reqNum = 0
        self.__contactIDs = []
        self.__insertIntoMysql = False
        self.__dumpToFile = True
        self.__md = mdapi
        self.__broker_id = broker_id
        self.__user_id = user_id
        self.__password = password
        self.__mysqlCon = None
        self.__starttime = datetime.now()
        self.__file = None

    def isDumpToMysql(self, dump=True):
        self.__insertIntoMysql = dump

    def isDumpToFile(self, dump=True):
        self.__dumpToFile = dump

    def stopClient(self):
        logger.info("stopClient")
        logger.info(datetime.now())
        self.__md.Release()
#         f = CThostFtdcUserLogoutField()
#         f.BrokerID = self.__broker_id
#         f.UserID = self.__user_id
#         self.__md.ReqUserLogout(f, self.__reqNum)
#         self.__reqNum = self.__reqNum + 1

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
        if (datetime.now() - self.__starttime) > timedelta(seconds=60*60*10):
            self.stopClient()

    def OnFrontDisconnected(self, *args):
        logger.info("OnFrontDisconnectet")
        logger.info("error code " + str(args[0]))
        if (datetime.now() - self.__starttime) > timedelta(seconds=60*60*10):
            self.stopClient()
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
        self.__md.Release()
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

    def dumpToFile(self, row):
        if self.__dumpToFile:
            #first time
            if self.__file == None:
                filename = datetime.utcnow().strftime("%Y-%m-%d")
                filename = "~/Dropbox/dailyDate/" + filename + ".csv"
                self.__file = open(filename, 'w')
                header = ("TradingDay, InstrumentID, ExchangeID, ExchangeInstID, LastPrice, " + 
                          "PreSettlementPrice, PreClosePrice, PreOpenInterest, OpenPrice, " +
                          "HighestPrice, LowestPrice, Volume, Turnover, OpenInterest, ClosePrice, " +
                          "SettlementPrice, UpperLimitPrice, LowerLimitPrice, PreDelta, CurrDelta, " +
                          "UpdateTime, UpdateMillisec, BidPrice1, BidVolume1, AskPrice1, AskVolume1 " +
                          "BidPrice2, BidVolume2, AskPrice2, AskVolume2, BidPrice3, BidVolume3, " +
                          "AskPrice3, AskVolume3, BidPrice4, BidVolume4, AskPrice4, AskVolume4, " +
                          "BidPrice5, BidVolume5, AskPrice5, AskVolume5, AveragePrice, ActionDay")
                self.__file.writelines(header);
        row = CThostFtdcDepthMarketDataField()
        fields = [row.TradingDay, str(row.InstrumentId), str(row.ExchangeID), str(row.ExchangeInstID), str(row.LastPrice)]
        fields.extend([str(row.PreSettlementPrice), str(row.PreClosePrice), str(row.PreOpenInterest), str(row.OpenPrice)])
        fields.extend([str(row.HighestPrice), str(row.LowestPrice), str(row.Volume), str(row.Turnover), str(row.OpenInterest), str(row.ClosePrice)])
        fields.extend([str(row.SettlementPrice), str(row.UpperLimitPrice), str(row.LowerLimitPrice), str(row.PreDelta), str(row.CurrDelta)])
        fields.extend([row.UpdateTime, str(row.UpdateMillisec)])
        fields.extend([str(row.BidPrice1), str(row.BidVolume1), str(row.AskPrice1), str(row.AskVolume1)])
        fields.extend([str(row.BidPrice2), str(row.BidVolume2), str(row.AskPrice2), str(row.AskVolume2)])
        fields.extend([str(row.BidPrice3), str(row.BidVolume3), str(row.AskPrice3), str(row.AskVolume3)])
        fields.extend([str(row.BidPrice4), str(row.BidVolume4), str(row.AskPrice4), str(row.AskVolume4)])
        fields.extend([str(row.BidPrice5), str(row.BidVolume5), str(row.AskPrice5), str(row.AskVolume5)])
        fields.extend([str(row.AveragePrice), row.ActionDay])
        self.__file.writelines(','.join(fields))

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
        self.__starttime = datetime.now()
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
