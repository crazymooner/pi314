from ib.opt import ibConnection
from pyalgotrade import observer
import pyalgotrade.logger
import api
from functools import partial
from time import sleep

short_sleep = partial(sleep, 1)
long_sleep = partial(sleep, 10)
logger = pyalgotrade.logger.getLogger("ibClient")
    
def log_reply_handler(msg):
    print "Server Response: %s, %s" % (msg.typeName, msg)

def save_order_id(msg):
    print 'save_order_id handler'
    ibClient.order_ids.append(msg.orderId)


def save_tick(msg):
    ibClient.tick_msgs.append(msg)

def dump_req_data(reqId):
    data = ibClient.req_data[reqId]
    f = open(data['contract'] + '.csv', 'w')
    f.write('date,open,high,low,close,volume,count,WAP,hasGaps\n')
    for row in data['data']:
        f.write(row.date + ',')
        f.write(str(row.open) + ',')
        f.write(str(row.high) + ',')
        f.write(str(row.low) + ',')
        f.write(str(row.close) + ',')
        f.write(str(row.volume) + ',')
        f.write(str(row.count) + ',')
        f.write(str(row.WAP) + ',')
        f.write(str(row.hasGaps) + '\n')
    f.close()


def historical_data_handler(msg):
    logger.info("load historical data for request" + str(msg.reqId))
    if msg.date.find('finished') is not -1:
        dump_req_data(msg.reqId)
    else:
        ibClient.req_data[msg.reqId]['data'].append(msg)

class ibClient:
    order_ids = [0]
    tick_msgs = []
    req_status = {}
    req_data = {}

    def __init__(self, host='localhost', port=7496, clientid=0):
        self.__con = ibConnection(host, port, clientid)
        self.__con.registerAll(log_reply_handler)
        self.__con.register(save_order_id, 'NextValidId')
        self.__con.register(save_tick, 'TickSize', 'TickPrice')
        self.__con.register(historical_data_handler, 'HistoricalData')
        self.__con.connect()
        short_sleep()

    def registerHandler(self, handler, eventMsg):
        self.__con.rigister(handler, eventMsg)

    def next_order_id(self):
        print 'next_order_id handler'
        return ibClient.order_ids[-1]

    def get_connection(self):
        return self.__con

    def ReqHistroyData(self, reqContract, reqEndDateTime, reqDurationStr = '1 Y',
                       reqBarSizeSetting = '1 day', reqWhatToShow = 'TRADES',
                       reqUseRTH = 0, reqFormatDate = 1):
        reqId = api.gen_tick_id()
        ibClient.req_status[reqId] = 'submit'
        ibClient.req_data[reqId] = {'data':[], 'contract':reqContract.m_symbol}
        self.__con.reqHistoricalData(tickerId = reqId,
                                    contract = reqContract,
                                    endDateTime = reqEndDateTime,
                                    durationStr = reqDurationStr,
                                    barSizeSetting = reqBarSizeSetting,
                                    whatToShow = reqWhatToShow,
                                    useRTH = reqUseRTH,
                                    formatDate = reqFormatDate)
        short_sleep()
    

