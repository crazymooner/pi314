from pi.ctp.ctpClient import MdApiClient
from optparse import OptionParser

def get_options():
    parser = OptionParser()
    parser.add_option('-d', '--dumpToMysql', dest='dump', default=False, action='store_true',
        help='dump data to MySQL')
    parser.add_option('-f', '--dumpToFile', dest='file', default=True, action='store_true',
                      help='dump date to file')
    opts, args = parser.parse_args()
    return opts

def dataDump(options):
    print "start dump", "Mysql ", options.dump, "File ", options.file
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
    mdclient.dumpToMysql(options.dump)
    mdclient.run()


if __name__ == "__main__":
    dataDump(get_options())
