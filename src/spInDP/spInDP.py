# This is the main file
import sys, getopt, time
from Spider import Spider
from BehaviorType import BehaviorType

def main(argv):
    spider = Spider()
    spider.initBevahiorLoop()
    time.sleep(1)
    spider.switchBehavior(BehaviorType.Autonome)
    time.sleep(1)
    spider.stop()
    print("program ended")

# Call main function when called from the command line
if __name__ == "__main__":
    main(sys.argv[1:])
