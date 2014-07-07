from ib.opt import Connection, message
from ib.ext.Contract import Contract
from ib.ext.Order import Order

def error_handler(msg):
    """Handles the capturing of error messages"""
    print "Server Error: %s" % msg

def reply_handler(msg):
    """Handles of server replies"""
    print "Server Response: %s, %s" % (msg.typeName, msg)


def make_contract(symbol, sec_type, exch, prim_exch, curr):
	Contract.m_symbol = symbol
	Contract.m_secType = sec_type
	Contract.m_exchange = exch
	Contract.m_primaryExch = prim_exch
	Contract.m_currency = curr
	return Contract

def make_order(action, quantity, price = None):
	if price is not None:
		order = Order()
		order.m_orderType = 'LMT'
		order.m_totalQuantity = quantity
		order.m_action = action
		order.m_lmtPrice = price
	else:
		order = Order()
		order.m_orderType = 'MKT'
		order.m_totalQuantity = quantity
		order.m_action = action
	return order

def test_make_order():
	conn = Connection.create(port=7496, clientId=99)
	conn.connect()
	conn.register(error_handler, 'Error')
	conn.registerAll(reply_handler)
	print 'connect'
	oid = 7;
	contract = make_contract('TSLA', 'STK', 'SMART', 'SMART', 'USD')
	offer = make_order('BUY', 100, 200)
	print contract
	print offer
	conn.placeOrder(oid, contract, offer)
	#conn.disconnect()

test_make_order()
print "hello"