import time
from spInDP.Spider import Spider
from spInDP.BehaviorType import BehaviorType

def main():
    spider = Spider()
    spider.servoController.setComplianceMargin()
    print("done")

# Call main function when called from the command line
if __name__ == "__main__":
    main()
