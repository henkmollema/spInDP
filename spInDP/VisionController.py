import io
import time
import picamera
import picamera.array
import threading
import cv2
import numpy as np
from fractions import Fraction

class VisionController:
    """Main class for the vision, which is meant to be used from a Spider instance"""
    __camera = None
    __vision = None
    
    def __init__(self):
        self.__camera = Camera()
        self.__vision = Vision(self, self.__camera.resolution)

    def FindBalloon(self):
        foundBlob, frame, coords, size = self.__vision.getValues()
        return foundBlob, coords, size

    def GetImage(self):
        frame = self.__camera.getFrame()
        return frame
        
    def GetImageVision(self):
        """Get image from the vision part which contains threshold and is available as a JPEG"""
        foundBlob, frame, coords, size = self.__vision.getValues()
        #print("coords: " + str(coords) + " size: " + str(size))
        return cv2.imencode('.jpeg', frame)[1].tostring()

class Camera(object):
    """Camera object for the VisionController. Is made so frames can be send multiple times"""
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    resolution = (640, 480)
    
    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def getFrame(self):
        Camera.last_access = time.time()
        self.initialize()
        return self.frame

    @classmethod
    def _thread(self):
        with picamera.PiCamera() as camera:
            camera.resolution = self.resolution
            camera.framerate = 30
            camera.sharpness = 0
            camera.contrast = 0
            camera.brightness = 50
            camera.saturation = 0
            camera.ISO = 800
            camera.exposure_compensation = 0
            camera.awb_mode = 'off'
            camera.awb_gains = (1.19, 1.43)
            camera.shutter_speed = 20000

            camera.hflip = True
            camera.vflip = True
            
            #camera.start_preview()
            #time.sleep(1)
			
            output = picamera.array.PiRGBArray(camera, size=self.resolution)

            #for frame in camera.capture_continuous(output, format="bgr", use_video_port=True):
            #    output.seek(0)
            #    self.frame = frame.array
            #    output.seek(0)
            #    output.truncate()
            #    if time.time() - self.last_access > 5:
            #        break
            
            stream = io.BytesIO()

            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                stream.seek(0)
                self.frame = stream.getvalue()
                stream.seek(0)
                stream.truncate()
                if time.time() - self.last_access > 5:
                    break

        self.thread = None
        
class Vision:
    """Vision does all the thresholding and returns information about the largest blob aswell as a thresholded image"""
    visionController = None
    thread = None 
    __resolution = None
    last_access = 0
        
    foundBlob = None
    image = None
    coords = None
    size = None
    
    def __init__(self, visionController, resolution):
        self.visionController = visionController
        self.__resolution = resolution
    def initialize(self):
        if Vision.thread is None:
            Vision.thread = threading.Thread(target=self._thread)
            Vision.thread.start()
            while self.image is None:
                time.sleep(0)

    def _thread(self):
        while time.time() - self.last_access < 5:
            frame = self.visionController.GetImage()
            frame = np.fromstring(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            self.foundBlob, self.image, self.coords, self.size = self.detect(frame)
        Vision.thread = None

    def getValues(self):
        Vision.last_access = time.time()
        self.initialize()
        return self.foundBlob, self.image, self.coords, self.size
        
    def thresholdRange(self, img, min, max):
        """Makes it possible to give a range when thresholding instead of a min or max"""
        ret,img1 = cv2.threshold(img, min, 1, cv2.THRESH_BINARY)
        ret,img2 = cv2.threshold(img, max, 1, cv2.THRESH_BINARY_INV)
        if max >= min:
            result = cv2.multiply(img1, img2)
        else:
            result = cv2.add(img1, img2)
        return result

    def detect(self, image):
        imagehsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(imagehsv)
        h = self.thresholdRange(h, 170, 10)
        s = self.thresholdRange(s, 110, 250)
        v = self.thresholdRange(v, 140, 255)
        imageBin = h * s * v

        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7)))
        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9,9)))

        imageBin = imageBin*255

        params = cv2.SimpleBlobDetector_Params()
        params.filterByColor = True
        params.blobColor = 255
        params.filterByCircularity = False
        params.filterByArea = False
        params.filterByCircularity = False
        params.filterByConvexity = False
        params.filterByInertia = False

        detector = cv2.SimpleBlobDetector(params)
        keypoints = detector.detect(imageBin)

        foundBlob = False
        coords = None
        size = None
        if keypoints:
            i = 0
            biggest = 0
            for p in keypoints:
                if (p.size > keypoints[biggest].size):
                    biggest = i
                i += 1
            foundBlob = True
            coords = keypoints[biggest].pt
            coords = (coords[0] - (self.__resolution[0] / 2), coords[1] - (self.__resolution[1] / 2))
            size = keypoints[biggest].size
        else:
            coords = (-1,-1)
            size = -1

        if foundBlob:
            image = cv2.drawKeypoints(imageBin, keypoints, np.array([]), (255,0,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
		
        return foundBlob, image, coords, size

