import time
from spInDP.Spider import Spider
from spInDP.BehaviorType import BehaviorType

def main():
    spider = Spider()
    spider.start()
    #spider.initBevahiorLoop()

    #time.sleep(1)

    #spider.switchBehavior(BehaviorType.Autonome)

    #time.sleep(1)

    #spider.stop()
    print("program ended")

# Call main function when called from the command line
if __name__ == "__main__":
    main()
