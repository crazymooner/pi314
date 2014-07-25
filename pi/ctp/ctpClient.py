from pi.mysql import client
from pi.ibHelper.barfeed import RealTimeBar
from datetime import datetime, timedelta
from MdApi.MdApi import *
from pi import CONSTANTS
from pyalgotrade import logger
import sys

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
        self.__file.close()
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
                filename = datetime.now().strftime("%Y-%m-%d")
                filename = "/home/pi314/Dropbox/daily_data/" + filename + ".csv"
                logger.info("Create file " + filename)
                self.__file = open(filename, 'w')
                header = ("TradingDay,InstrumentID,ExchangeID,ExchangeInstID,UpdateMillisec,ActionDay," + 
                          "LastPrice,PreSettlementPrice,PreClosePrice,PreOpenInterest,OpenPrice," +
                          "HighestPrice,LowestPrice,Volume,Turnover,OpenInterest,ClosePrice," +
                          "SettlementPrice,UpperLimitPrice,LowerLimitPrice,PreDelta,CurrDelta," +
                          "BidPrice1,BidVolume1,AskPrice1,AskVolume1," +
                          "BidPrice2,BidVolume2,AskPrice2,AskVolume2,BidPrice3,BidVolume3," +
                          "AskPrice3,AskVolume3,BidPrice4,BidVolume4,AskPrice4,AskVolume4," +
                          "BidPrice5,BidVolume5,AskPrice5,AskVolume5,AveragePrice")
                self.__file.write(header + '\n');
        #Data PreProcess
        date = datetime.strptime(row.TradingDay, "%Y%m%d")
        dateStr = date.strftime("%Y-%m-%d")
        dateStr = dateStr + " " + row.UpdateTime
        fields = [dateStr, row.InstrumentID, row.ExchangeID, row.ExchangeInstID, str(row.UpdateMillisec), row.ActionDay]
        numbers = [row.LastPrice,row.PreSettlementPrice, row.PreClosePrice, row.PreOpenInterest, row.OpenPrice]
        numbers.extend([row.HighestPrice, row.LowestPrice, row.Volume, row.Turnover, row.OpenInterest, row.ClosePrice])
        numbers.extend([row.SettlementPrice, row.UpperLimitPrice, row.LowerLimitPrice, row.PreDelta, row.CurrDelta])
        numbers.extend([row.BidPrice1, row.BidVolume1, row.AskPrice1, row.AskVolume1])
        numbers.extend([row.BidPrice2, row.BidVolume2, row.AskPrice2, row.AskVolume2])
        numbers.extend([row.BidPrice3, row.BidVolume3, row.AskPrice3, row.AskVolume3])
        numbers.extend([row.BidPrice4, row.BidVolume4, row.AskPrice4, row.AskVolume4])
        numbers.extend([row.BidPrice5, row.BidVolume5, row.AskPrice5, row.AskVolume5])
        numbers.append(row.AveragePrice)
        for i in range(len(numbers)):
            if numbers[i] == sys.float_info.max:
                numbers[i] = "-1"
            else:
                numbers[i] = str(numbers[i])
        fields.extend(numbers)
        self.__file.write(','.join(fields) + "\n")
        self.__file.flush()

    def OnRtnDepthMarketData(self, *args):
        
        logger.info("OnRtnDepthMarketData")
        logger.info("id: "+args[0].InstrumentID)
        logger.info("TradingDay: " + args[0].TradingDay + " " + args[0].UpdateTime)
        logger.info("LastPrice: " + str(args[0].LastPrice))
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
        if self.__dumpToFile:
            try:
                self.dumpToFile(args[0])
            except Exception as e:
                print "except", e
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
