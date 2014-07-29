from pi.ctp.ctpClient import MdApiClient
from optparse import OptionParser
from datetime import date

contractID=[["01","02","03","06","09"],
            ["02","03","04","06","09"],
            ["03","04","05","06","09"],
            ["04","05","06","09","12"],
            ["05","06","07","09","12"],
            ["06","07","08","09","12"],
            ["07","08","09","12","03"],
            ["08","09","10","12","03"],
            ["09","10","11","12","03"],
            ["10","11","12","03","06"],
            ["11","12","01","03","06"],
            ["12","01","02","03","06"]]


def get_options():
    parser = OptionParser()
    parser.add_option('-d', '--dumpToMysql', dest='dump', default=False, action='store_true',
        help='dump data to MySQL')
    parser.add_option('-f', '--dumpToFile', dest='file', default=True, action='store_true',
                      help='dump date to file')
    opts, args = parser.parse_args()
    return opts

def dataDump(options):
    year = date.today().year%100
    month = date.today().month
    MonID = contractID[month-1]
    symbols = []
    for mon in MonID:
        m = int(mon)
        if m < month:
            year = year + 1
        symbols.append("IF" + str(year) + str(mon))
    print symbols
    print "start dump", "Mysql ", options.dump, "File ", options.file
    mdclient = MdApiClient()
    for symbol in symbols:
        mdclient.addSymbol(symbol)
    mdclient.dumpToMysql(options.dump)
    mdclient.run()


if __name__ == "__main__":
    dataDump(get_options())
