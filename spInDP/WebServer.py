import time
import json
import glob
import psutil
from BehaviorType import BehaviorType
from flask import Flask, render_template, request, Response

webserverinstance = None


class WebServer:
    app = Flask(__name__)
    spider = None
    spiderLegs = [0, 0, 0, 0, 0, 0]

    def __init__(self, spider):
        global webserverinstance
        webserverinstance = self
        self.spider = spider

    def start(self):
        self.app.run(host='0.0.0.0', port=80, debug=False, threaded=True)

    def format_response(self, message, mimetype='application/json'):
        resp = Response(message, status=200, mimetype=mimetype)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    def gen_cam(self):
        while True:
            frame = self.spider.visioncontroller.GetImage()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)

    def gen_cam_vision_redballoon(self):
        while True:
            frame = self.spider.visioncontroller.GetImageVisionRedBalloon()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)
    def gen_cam_vision_blueballoon(self):
        while True:
            frame = self.spider.visioncontroller.GetImageVisionBlueBalloon()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)
    def gen_cam_vision_line(self):
        while True:
            frame = self.spider.visioncontroller.GetImageLine()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(0.01)

    @staticmethod
    @app.route("/")
    def api_root():
        return webserverinstance.format_response("ScarJo says 'Hi!'")

    @staticmethod
    @app.route("/camera")
    def api_camera():
        return webserverinstance.format_response(webserverinstance.gen_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')
    @staticmethod
    @app.route("/vision/redballoon")
    def api_vision_redballoon():
        return webserverinstance.format_response(webserverinstance.gen_cam_vision_redballoon(), mimetype='multipart/x-mixed-replace; boundary=frame')
    @staticmethod
    @app.route("/vision/blueballoon")
    def api_vision_blueballoon():
        return webserverinstance.format_response(webserverinstance.gen_cam_vision_blueballoon(), mimetype='multipart/x-mixed-replace; boundary=frame')
    @staticmethod
    @app.route("/vision/line")
    def api_vision_line():
        return webserverinstance.format_response(webserverinstance.gen_cam_vision_line(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @staticmethod
    @app.route("/app/servodata")
    def api_servodata():
        return webserverinstance.format_response(webserverinstance.spider.servoController.getServoDataJSON())

    @staticmethod
    @app.route("/app/getsystemdata")
    def api_getsystemdata():
        retVal = {}
        cpuData = psutil.cpu_percent(interval=1, percpu=True)
        tiltVals = webserverinstance.spider.sensorDataProvider.getAccelerometer()
        batteryPercentage = round((webserverinstance.spider.servoController.getVoltage(1) - 9.2) / (2.8),
                                  2)  # based on voltage read on servo

        retVal['cpu'] = {"core1": cpuData[0], "core2": cpuData[1], "core3": cpuData[2], "core4": cpuData[3],
                         "time": time.time()}
        retVal['battery'] = batteryPercentage
        retVal['tilt'] = {'x': tiltVals[0], 'y': tiltVals[1], 'z': tiltVals[2]}

        jsonString = json.dumps(retVal, separators=(',', ':'))

        return webserverinstance.format_response(jsonString)

    @staticmethod
    @app.route("/app/graphdata")
    def api_graphdata():
        return webserverinstance.format_response("Not implemented")

    @staticmethod
    @app.route("/app/debugdata")
    def api_debugdata():
        return webserverinstance.format_response("Not implemented")

    @staticmethod
    @app.route("/sequence/<animation>")
    @app.route("/sequence/<animation>/<repeat>")
    @app.route("/sequence/<animation>/<repeat>/<speedModifier>")
    def api_control_animation(animation, repeat=1, speedModifier=1):
        print("exec animation: " + animation)
        webserverinstance.spider.sequenceController.parseSequence(
            "sequences/" + animation, repeat=int(repeat), speedModifier=float(speedModifier))
        return webserverinstance.format_response("animation executed: sequences/" + animation)

    @staticmethod
    @app.route("/erwin/turn4legs/<count>/<speed>")
    def api_erwin_turnwalk(count, speed):
        frameNr = 0
        for x in range(0, 4 * int(count)):
            execTime = webserverinstance.spider.animationController.turn4Legs(1, 0, frameNr, float(speed))
            time.sleep(execTime)
            frameNr += 1
        return webserverinstance.format_response("turn4legs executed")

    @staticmethod
    @app.route("/behavior/<behaviortype>")
    def api_control_behavior(behaviortype):
        print("got behavior command: " + behaviortype)
        webserverinstance.spider.switchBehavior(behaviortype)
        return webserverinstance.format_response("switch behavior: " + behaviortype)

    @staticmethod
    @app.route("/control/joystick/<x>/<y>")
    def api_control_walk(jX, jY):
        print("Got control joystick command: " + jX + ", " + jY)
        webserverinstance.spider.remoteController.context.JoystickX = jX
        webserverinstance.spider.remoteController.context.JoystickY = jY
        return webserverinstance.format_response(jX + "," + jY)

    @staticmethod
    @app.route("/control/reset")
    def api_control_reset():
        print("Got control reset command")
        webserverinstance.spider.sequenceController.parseSequence("sequences/startup.txt", repeat=1)
        return webserverinstance.format_response("reset")

    @staticmethod
    @app.route("/control/stop/")
    def api_control_stop():
        print("Got control stop command")
        webserverinstance.spider.stop()
        return webserverinstance.format_response("stop")

    @staticmethod
    @app.route("/control/sequencelist/")
    def api_control_getSequences():
        seqObj = {}
        seqObj['sequenceFiles'] = glob.glob("../sequences/*.txt")
        return json.dumps(seqObj, separators=(',', ':'))

    @staticmethod
    @app.route("/kinematics/")
    def api_kinematics():
        return render_template('kinnematics.html')

    @staticmethod
    @app.route("/kinematics/coords/")
    def api_get_coords():
        return webserverinstance.format_response(webserverinstance.spider.servoController.getAllLegsXYZ())

    @staticmethod
    @app.route("/kinematics/leg/<leg>/")
    def api_kinematics_legsOnOff(leg):
        index = 1

        for x in leg.split('_'):
            webserverinstance.spider.servoController.setLegTorque(index, x)
            print(x)
            index += 1

        legTorques = webserverinstance.spider.servoController.torqueStatus
        return webserverinstance.format_response(','.join(str(x) for x in legTorques))

    @staticmethod
    @app.route("/jquery.min.js")
    def api_kinematics_jquery():
        with open("spInDP/templates/jquery.min.js") as jquery:
            data = jquery.readlines()

        return webserverinstance.format_response(data)

    @staticmethod
    @app.route("/emotive/<command>")
    def api_emotive_command(command):
        webserverinstance.spider.emotiveContext.currentCommand = command
        return webserverinstance.format_response("emo: " + command)

    @staticmethod
    @app.route("/startDance")
    def api_startDance():
        print ("StartDance")
        webserverinstance.spider.switchBehavior(BehaviorType.Dance)
        return webserverinstance.format_response("startdance")

    @staticmethod
    @app.route("/stop")
    def api_stop():
        print ("Stop the spider")
        webserverinstance.spider.stop()

    @staticmethod
    @app.route("/shutdown")
    def api_shutdown():
        print("Shutdown the spider.")
        webserverinstance.spider.shutdown()

    @staticmethod
    @app.route("/reboot")
    def api_reboot():
        print("Rebooting the spider.")
        webserverinstance.spider.reboot()
