import subprocess
import time
import os
from flask import Flask, render_template, Response

webserverinstance = None

class WebServer:
    app = Flask(__name__)
    spider = None
    
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

    @staticmethod
    @app.route("/")
    def api_root():
        return webserverinstance.format_response("Hello World!")

    @staticmethod
    @app.route("/app")
    def api_app():
        return webserverinstance.format_response("{\"spiderstatus\": \"Hoi\"}")

    @staticmethod
    @app.route("/control/<animation>")
    @app.route("/control/<animation>/<repeat>")
    def api_control_animation(animation, repeat = 1):
        print ("exec animation: " + animation)
        webserverinstance.spider.sequenceController.parseSequence("sequences/" + animation, repeat = int(repeat))
        return webserverinstance.format_response("animation executed: sequences/" + animation)
    
    @staticmethod
    @app.route("/camera")
    def api_camera():
        return webserverinstance.format_response(webserverinstance.gen_cam(), mimetype='multipart/x-mixed-replace; boundary=frame')