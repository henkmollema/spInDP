# This is the main file
import sys, getopt
from Spider import Spider

def main(argv):
    spidr = Spider()
    spidr.printHello()
    print("program ended")

# Call main function when called from the command line
if __name__ == "__main__":
    main(sys.argv[1:])