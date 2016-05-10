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

    @app.route("/")
    def api_root():
        return webserverinstance.format_response("Hello World!")

    @app.route("/app")
    def api_app():
        return webserverinstance.format_response("{\"spiderstatus\": \"Hoi\"}")
        
    @app.route("/control/<animation>")
    @app.route("/control/<animation>/<repeat>")
    def api_control_animation(animation, repeat = 1):
        print ("exec animation: " + animation)
        webserverinstance.spider.sequenceController.parseSequence("sequences/" + animation, repeat = int(repeat))
        return webserverinstance.format_response("animation executed: sequences/" + animation)

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