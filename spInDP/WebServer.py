import subprocess
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
        self.app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    
    def format_response(self, message, mimetype='application/json'):
        resp = Response(message, status=200, mimetype=mimetype)
        resp.headers['Access-Control-Allow-Origin'] = '*'
        return resp

    @staticmethod
    @app.route("/")
    def api_root():
        return webserverinstance.format_response("Hello World!")

    @staticmethod
    @app.route("/app/servodata")
    def api_app():
        return webserverinstance.format_response(webserverinstance.spider.servoController.getServoDataJSON())
        
    @staticmethod
    @app.route("/app/graphdata")
    def api_app():
        return webserverinstance.format_response("Not implemented")
        
    @staticmethod
    @app.route("/app/debugdata")
    def api_app():
        return webserverinstance.format_response("Not implemented")
        
    @staticmethod
    @app.route("/sequence/<animation>")
    @app.route("/sequence/<animation>/<repeat>")
    def api_control_animation(animation, repeat = 1):
        print ("exec animation: " + animation)
        webserverinstance.spider.sequenceController.parseSequence("sequences/" + animation, repeat = int(repeat))
        return webserverinstance.format_response("animation executed: sequences/" + animation)
    
    @staticmethod
    @app.route("/behavior/<behaviortype>")
    def api_control_behavior(behaviortype):
        print ("got behavior command: " + behaviortype)
        webserverinstance.spider.switchBehavior(behaviortype)
        return webserverinstance.format_response("switch behavior: " + behaviortype)
    
    @staticmethod
    @app.route("/control/walk/<x>/<y>")
    def api_control_walk(x, y):
        print ("Got control walk command: " + x + ", " + y)
        
        return webserverinstance.format_response("Walk xy: " + x + ", " + y)
        
    @staticmethod
    @app.route("/control/reset")
    def api_control_reset():
        print ("Got control reset command")
        webserverinstance.spider.sequenceController.parseSequence("sequences/startup.txt", repeat = 1)
        return webserverinstance.format_response("reset")
        
        
    @staticmethod
    @app.route("/control/stop/")
    def api_control_stop():
        print ("Got control stop command")
        webserverinstance.spider.stop()
        return webserverinstance.format_response("stop")

    #def gen(self, camera):
    #    """Video streaming generator function."""
    #    while True:
    #        frame = camera.get_frame()
    #        yield (b'--frame\r\n'
    #               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #time.sleep(0.05)

    #@app.route("/app/camera")
    #def api_app_camera(self):
    #    return format_response(gen(Camera()), mimetype='multipart/x-mixed-replace; boundary=frame')