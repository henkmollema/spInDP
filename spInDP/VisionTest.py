import time
from threading import Thread
from spInDP.WebServer import WebServer
from spInDP.VisionController import VisionController

class Spider:
    webserver = None
    visioncontroller = None
    
    def __init__(self):
        self.webserver = WebServer(self)
        self.visioncontroller = VisionController()
    
    def start(self):
        self.webserver.start()

spider = Spider()
spider.start()
