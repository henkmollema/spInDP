import atexit
from spInDP.Spider import Spider

spider = None
def main():
    spider = Spider()
    spider.start()
    spider.initBehaviorLoop()

    # Call to webserver.start() blocks the main thread
    spider.webserver.start()

def exit():
    if spider is not None:
        print ("Stopping the program...")
        spider.stop()
        print("Program stopped")
    else:
        print ("No Spider instance to stop")


# Call main function when called from the command line
if __name__ == "__main__":
    atexit.register(exit)
    main()
