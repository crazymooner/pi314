from MdApi import *

FRONT_ADDR = "tcp://ctp1-md5.citicsf.com:41213";
FRONT_ADDR1 ="tcp://115.238.108.184:41213";
BROKER_ID = "1017";	
INVESTOR_ID = "00000071";
PASSWORD = "123456";
INSTRUMENT_ID = "IF1312";
DIRECTION = THOST_FTDC_D_Sell;

md = CThostFtdcMdApi_CreateFtdcMdApi("./qlog")

class Quote(CThostFtdcMdSpi):

	def __init__(self):
		CThostFtdcMdSpi.__init__(self)
		self.reqNum = 0
		self.contactIDs = []
		self.filename = "output"

	def OnFrontConnected(self):
		print "OnFrontConnected"
		f = CThostFtdcReqUserLoginField()
		f.BrokerID = BROKER_ID
		f.UserUD = INVESTOR_ID
		f.Password = PASSWORD
		md.ReqUserLogin(f,self.reqNum)
		self.reqNum = self.reqNum + 1

	def OnFrontDisconnected(self, *args):
		print "OnFrontDisconnectet"
		pass

	def OnHeartBeatWarning(self, *args):
		print "OnHeartBeatWarning"
		pass

	def OnRspUserLogin(self, *args):
		print "OnRspUserLogin"
		ppInst = ["IF1407","IF1408"]
		md.SubscribeMarketData(ppInst,2)
		print "OnRspUserLogin End"

	def OnRspUserLogout(self, *args):
		print "OnRspUserLogout"
		pass

	def OnRspError(self, *args):
		print "OnRspError"
		pass

	def OnRspSubMarketData(self, *args):
		print "OnRspSubMarketData"
		print args

	def OnRspUnSubMarketData(self, *args):
		print "OnRspUnSubMarketData"
		print args
		pass

	def OnRtnDepthMarketData(self, *args):
		print "OnRtnDepthMarketData"
		print "id: ", args[0].InstrumentID
		print "LastPrice: ",args[0].LastPrice
		print "TradingDay: ",args[0].TradingDay
		print "UpdateTime: ",args[0].UpdateTime
		print "OpenPrice: ",args[0].OpenPrice
		print "HighestPrice: ",args[0].HighestPrice
		print "LowestPrice: ",args[0].LowestPrice
		print "Volume: ",args[0].Volume
		print "ClosePrice: ",args[0].ClosePrice
		pass


def run():
	q = Quote()
	data = CThostFtdcDepthMarketDataField()
	#data.InstrumentID = "IF1408"
	#data.LastPrice = 123
	#q.OnRtnDepthMarketData(data)
	#q.OnFrontConnected()
	#q.OnRspUserLogin()
	#spi = CThostFtdcMdSpi()
	#spi.OnFrontConnected()
	md.RegisterSpi(q)
	md.RegisterFront(FRONT_ADDR)
	md.Init()
	md.Join()

	print "hello world"

run()