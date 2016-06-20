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

    def FindBalloon(self, detectBlue = True):
        foundBlob, redBalloonFrame, blueBalloonFrame, coords, size = self.__vision.getBalloonValues(detectBlue)
        return foundBlob, coords, size
    def getBalloonIsLeft(self):
        return self.__vision.getBalloonIsLeft()

    def GetImage(self):
        frame = self.__camera.getFrame()
        return frame
        
    def GetImageVisionRedBalloon(self):
        """Get image from the vision part which contains the threshold for the RED balloon and is available as a JPEG"""
        foundBlob, redBalloonFrame, blueBalloonFrame, coords, size = self.__vision.getBalloonValues()
        return cv2.imencode('.jpeg', redBalloonFrame)[1].tostring()
    def GetImageVisionBlueBalloon(self):
        """Get image from the vision part which contains the threshold for the BLUE balloon and is available as a JPEG"""
        foundBlob, redBalloonFrame, blueBalloonFrame, coords, size = self.__vision.getBalloonValues()
        return cv2.imencode('.jpeg', blueBalloonFrame)[1].tostring()
    def GetImageLine(self):
        frame = self.__vision.getLineValues()
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
    __resolution = None

    #Balloon variables
    balloonThread = None
    last_balloon_access = 0

    detectBlue = False
    foundRedBlob = None
    redBalloonImage = None
    blueBalloonImage = None
    redBalloonCoords = None
    redBalloonSize = None
    redleftCount = 0
    redRightCount = 0

    #Line variables
    lineThread = None
    last_line_access = 0

    foundLineBlob = None
    lineCoords = None
    lineImage = None
    
    def __init__(self, visionController, resolution):
        self.visionController = visionController
        self.__resolution = resolution
    def initializeBalloon(self):
        if Vision.balloonThread is None:
            Vision.balloonThread = threading.Thread(target=self._balloonThread)
            Vision.balloonThread.start()
            while self.redBalloonImage is None:
                time.sleep(0)
    def _balloonThread(self):
        self.redleftCount = 0
        self.redRightCount = 0
        while time.time() - self.last_balloon_access < 5:
            frame = self.visionController.GetImage()
            frame = np.fromstring(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, 1)
            self.foundRedBlob, self.redBalloonImage, self.redBalloonCoords, self.redBalloonSize = self.detectRedBalloon(frame)
            foundBlueBlob = False
            if self.detectBlue:
                foundBlueBlob, self.blueBalloonImage, blueCoords = self.detectBlueBalloon(frame)
            if foundBlueBlob:
                if blueCoords[0] > self.redBalloonCoords[0]:
                    self.redleftCount += 1
                else:
                    self.redRightCount += 1
        Vision.balloonThread = None
    def getBalloonValues(self, detectBlue = True):
        Vision.last_balloon_access = time.time()
        if self.detectBlue is not detectBlue:
            self.detectBlue = detectBlue
        self.initializeBalloon()
        return self.foundRedBlob, self.redBalloonImage, self.blueBalloonImage, self.redBalloonCoords, self.redBalloonSize
    def getBalloonIsLeft(self):
        return self.redleftCount > self.redRightCount

    def initializeLine(self):
        if Vision.lineThread is None:
            Vision.lineThread = threading.Thread(target=self._lineThread)
            Vision.lineThread.start()
            while self.lineImage is None:
                time.sleep(0)
    def _lineThread(self):
        while time.time() - self.last_line_access < 5:
            """
            fd = open('linetest.jpg')
            img_str = fd.read()
            frame = np.fromstring(img_str, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.CV_LOAD_IMAGE_COLOR)
            self.foundLineBlob, self.lineImage, self.lineCoords = self.detectLineNew(frame)
            """
            frame = self.visionController.GetImage()
            frame = np.fromstring(frame, dtype=np.uint8)
            frame = cv2.imdecode(frame, cv2.CV_LOAD_IMAGE_COLOR)
            cropFrame = frame[self.__resolution[1] - 50:self.__resolution[1], 0:self.__resolution[0]]
            self.foundLineBlob, self.lineImage, self.lineCoords = self.detectLineNew(cropFrame)

        Vision.lineThread = None
    def getLineValues(self):
        Vision.last_line_access = time.time()
        self.initializeLine()
        return self.lineImage

    def thresholdRange(self, img, min, max):
        """Makes it possible to give a range when thresholding instead of a min or max"""
        ret, img1 = cv2.threshold(img, min, 1, cv2.THRESH_BINARY)
        ret, img2 = cv2.threshold(img, max, 1, cv2.THRESH_BINARY_INV)
        if max >= min:
            result = cv2.multiply(img1, img2)
        else:
            result = cv2.add(img1, img2)
        return result

    def detectRedBalloon(self, image):
        imagehsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(imagehsv)
        h = self.thresholdRange(h, 170, 10)
        s = self.thresholdRange(s, 110, 255)
        v = self.thresholdRange(v, 110, 255)
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
            coords = (-1, -1)
            size = -1

        if foundBlob:
            image = imageBin

        return foundBlob, image, coords, size
    def detectBlueBalloon(self, image):
        imagehsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(imagehsv)
        h = self.thresholdRange(h, 90, 110) #TODO
        s = self.thresholdRange(s, 200, 255) #TODO
        v = self.thresholdRange(v, 160, 255) #TODO
        imageBin = h * s * v

        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))

        imageBin = imageBin * 255

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
        else:
            coords = (-1, -1)

        if foundBlob:
            image = imageBin

        return foundBlob, image, coords

    def detectLine(self, image):
        imagegray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, imageBin = cv2.threshold(imagegray, 120, 255, cv2.THRESH_BINARY)

        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

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
            coords = (-1, -1)
            size = -1

        if foundBlob:
            image = cv2.drawKeypoints(imageBin, keypoints, np.array([]), (255, 0, 0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

        #return foundBlob, image, coords, size
        return image
    def detectLineNew(self, image):
        print("detectLineNew called")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        ret, imageBin = cv2.threshold(blur, 120, 255, cv2.THRESH_BINARY)

        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
        imageBin = cv2.morphologyEx(imageBin, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))

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
        else:
            coords = (-1, -1)

        return foundBlob, imageBin, coords