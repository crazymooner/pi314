'''
Created on Jun 23, 2014

@author: tliu
'''
from pyalgotrade.ib.ibClient import ibClient
from pyalgotrade.ib.api import make_contract 
from time import sleep, strftime, time
from functools import partial

client = ibClient()
contract = make_contract('GOOG')
endtime = strftime('%Y%m%d %H:%M:%S')
client.ReqHistroyData(reqContract = contract, reqEndDateTime = endtime)
print 'done'
