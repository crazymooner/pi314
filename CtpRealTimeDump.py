from pi.ctp.ctpClient import MdApiClient


def main():
    print "start"
    mdclient = MdApiClient()
    mdclient.run()

if __name__ == "__main__":
    main()
