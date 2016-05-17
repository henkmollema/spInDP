import subprocess
import time
import os
from flask import Flask, render_template, Response, request

webserverinstance = None


class WebServer:
    app = Flask(__name__)
    spider = None

    def __init__(self, spider):
        global webserverinstance
        webserverinstance = self
        self.spider = spider

    def start(self):
        self.app.run(host='0.0.0.0', port=80, debug=True, threaded=True)

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

    @staticmethod
    @app.route("/")
    def api_root():
        return webserverinstance.format_response("Hello World!")

    @staticmethod
    @app.route("/camera")
    def api_camera():
        return webserverinstance.format_response(webserverinstance.gen_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')

    @staticmethod
    @app.route("/app/servodata")
    def api_servodata():
        return webserverinstance.format_response(webserverinstance.spider.servoController.getServoDataJSON())

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
    def api_control_animation(animation, repeat=1):
        print("exec animation: " + animation)
        webserverinstance.spider.sequenceController.parseSequence(
            "sequences/" + animation, repeat=int(repeat))
        return webserverinstance.format_response("animation executed: sequences/" + animation)

    @staticmethod
    @app.route("/behavior/<behaviortype>")
    def api_control_behavior(behaviortype):
        print("got behavior command: " + behaviortype)
        webserverinstance.spider.switchBehavior(behaviortype)
        return webserverinstance.format_response("switch behavior: " + behaviortype)

    @staticmethod
    @app.route("/control/walk/<x>/<y>")
    def api_control_walk(x, y):
        print("Got control walk command: " + x + ", " + y)

        return webserverinstance.format_response("Walk xy: " + x + ", " + y)

    @staticmethod
    @app.route("/control/reset")
    def api_control_reset():
        print("Got control reset command")
        webserverinstance.spider.sequenceController.parseSequence(
            "sequences/startup.txt", repeat=1)
        return webserverinstance.format_response("reset")

    @staticmethod
    @app.route("/control/stop/")
    def api_control_stop():
        print("Got control stop command")
        webserverinstance.spider.stop()
        return webserverinstance.format_response("stop")
        
    @staticmethod
    @app.route("/remote/", methods=['GET','POST'])
    def remote():
        if request.method == 'POST':
            animation = request.form['motion']
            value = request.form['value']
            if value == "stop":
                webserverinstance.api_control_stop()
            elif value == "reset":
                webserverinstance.api_control_reset()
            else:
                webserverinstance.api_control_animation(animation,1)
            return render_template('temp.html')
        else:
            return render_template('test.html')