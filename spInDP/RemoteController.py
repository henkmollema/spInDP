from spInDP.RemoteContext import RemoteContext
import glob
import json

RemoteControllerInstance = None

class RemoteController(object):
    """Provides interaction with the physical remote controller."""

    Context = RemoteContext()

    def __init__(self, spider):
        global RemoteControllerInstance
        self.spider = spider
        RemoteControllerInstance = self

    
    @staticmethod
    @RemoteControllerInstance.spider.app.route("/behavior/<behaviortype>")
    def api_control_behavior(behaviortype):
        print("got behavior command: " + behaviortype)
        RemoteControllerInstance.spider.switchBehavior(behaviortype)
        return RemoteControllerInstance.spider.webserver.format_response("switch behavior: " + behaviortype)

    @staticmethod
    @RemoteControllerInstance.spider.app.route("/control/joystick/<x>/<y>")
    def api_control_walk(jX, jY):
        print("Got control joystick command: " + jX + ", " + jY)

        return RemoteControllerInstance.spider.webserver.format_response( jX + "," + jY)

    @staticmethod
    @RemoteControllerInstance.spider.app.route("/control/reset")
    def api_control_reset():
        print("Got control reset command")
        RemoteControllerInstance.spider.sequenceController.parseSequence(
            "sequences/startup.txt", repeat=1)
        return RemoteControllerInstance.spider.webserver.format_response("reset")

    @staticmethod
    @RemoteControllerInstance.spider.app.route("/control/stop/")
    def api_control_stop():
        print("Got control stop command")
        RemoteControllerInstance.spider.stop()
        return RemoteControllerInstance.spider.webserver.format_response("stop")
        
    @staticmethod
    @RemoteControllerInstance.spider.app.route("/control/sequencelist/")
    def api_control_getSequences():
        seqObj = {}
        seqObj['sequenceFiles'] = glob.glob("../sequences/*.txt")
        return json.dumps(seqObj, separators=(',', ':'))
