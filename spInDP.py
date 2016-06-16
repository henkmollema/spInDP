import signal
import sys

from spInDP.Spider import Spider

spider = None


def signal_handler(signal, frame):
    print ("\nExiting...")
    exit()


signal.signal(signal.SIGINT, signal_handler)


def main():
    global spider
    spider = Spider()

    spider.start()
    spider.initBehaviorLoop()

    spider.webserver.start()


def exit():
    if spider is not None:
        print ("Stopping the program...")
        spider.stop()
        print("Program stopped")
        sys.exit(0)
    else:
        print ("No Spider instance to stop")


# Call main function when called from the command line
if __name__ == "__main__":
    # atexit.register(exit)
    main()
