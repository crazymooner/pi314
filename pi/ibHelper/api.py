import sys
from random import randint
from ib.ext.Order import Order
from ib.ext.Contract import Contract

def gen_tick_id():
    i = randint(100, 10000)
    while True:
        yield i
        i += 1
if sys.version_info[0] < 3:
    gen_tick_id = gen_tick_id().next
else:
    gen_tick_id = gen_tick_id().__next__
    
def make_contract(symbol):
    contract = Contract()
    contract.m_symbol = symbol
    contract.m_secType = 'STK'
    contract.m_exchange = 'SMART'
    contract.m_primaryExch = 'SMART'
    contract.m_currency = 'USD'
    contract.m_localSymbol = symbol
    return contract


def make_order(limit_price):
    order = Order()
    order.m_minQty = 100
    order.m_lmtPrice = limit_price
    order.m_orderType = 'MKT'
    order.m_totalQuantity = 100
    order.m_action = 'BUY'
    return order