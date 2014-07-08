from pi.ctp.ctpClient import MdApiClient


def main():
    print "start"
    mdclient = MdApiClient()
    mdclient.addSymbol("IF1407")
    mdclient.dumpToMysql(True)
    mdclient.run()

if __name__ == "__main__":
    main()
