import time
from threading import Thread
from WebServer import WebServer
from VisionController import VisionController

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