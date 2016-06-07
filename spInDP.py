from spInDP.Spider import Spider


def main():
    spider = Spider()
    spider.start()
    spider.initBehaviorLoop()

    # Call to webserver.start() blocks the main thread
    spider.webserver.start()

    # spider.stop()
    print("program ended")

# Call main function when called from the command line
if __name__ == "__main__":
    main()
