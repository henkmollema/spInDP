import bluetooth
import time
import threading
from spInDP.RemoteContext import RemoteContext

class RemoteController(object):
    """Provides interaction with the physical remote controller."""

    stop = False
    Context = None
    spider = None
    sock = None
    updateLoop = None

    def __init__(self, spider):
        self.spider = spider
        self.Context = RemoteContext()
        try:
            print("Initializing Bluetooth connection")
            self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.sock.connect(("20:16:03:30:80:85", 1))
            self.updateLoop = threading.Thread(target=self.updateContextLoop)
            self.updateLoop.start()
        except:
            print ("Initializing bluetooth failed")
            
    def updateContextLoop(self):
        print ("Start updateContextLoop")
        rec = ""
        while not self.stop:
            try:
                rec += self.sock.recv(1024)
                #time.sleep(1)
            except:
                print ("error reading bluetooth")
                break

            rec_end = rec.find('\n')

            if (rec_end != -1):
                data = rec[:rec_end]
                
            # Read joystick position
            if (data.startswith('J:')):
                xs = data.split(':')[1].split(',')
                x = xs[0]
                y = xs[1]
                z = xs[2]
                self.Context.jX = x
                self.Context.jY = y
                self.Context.jZ = z
                #print "Joystick = X: " + x + ", Y: " + y + ", Z: " + z
            #elif (data.startswith("A:")):
            #    xs = data.split(':')[1].split(',')
            #    x = xs[0]
            #    y = xs[1]
            #    z = xs[2]
                #print "Accl = X: " + x + ", Y: " + y + ", Z: " + z

            rec = rec[rec_end+1:]
            continue

        print ("Closing socket")
        sock.close()

