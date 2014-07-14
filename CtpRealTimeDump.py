from pi.ctp.ctpClient import MdApiClient

def main():
    print "start"
    mdclient = MdApiClient()
    mdclient.addSymbol("IF1407")
    mdclient.addSymbol("IF1408")
    mdclient.addSymbol("IF1409")
    mdclient.addSymbol("IF1410")
    mdclient.addSymbol("IF1411")
    mdclient.addSymbol("IF1412")
    mdclient.addSymbol("IF1501")
    mdclient.addSymbol("IF1502")
    mdclient.addSymbol("IF1503")
    mdclient.addSymbol("IF1504")
    mdclient.dumpToMysql(True)
    mdclient.run()

if __name__ == "__main__":
    main()
