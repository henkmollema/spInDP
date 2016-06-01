import bluetooth
import time

bd_addr = "20:16:03:30:80:85"
port = 1
sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((bd_addr, port))

print ("Start reading from address " + bd_addr)

rec = ""
while True:
  try:
    rec += sock.recv(1024)
    #time.sleep(1)
  except:
    print ("error reading bluetooth")
    break
    
  rec_end = rec.find('\n')

  if (rec_end != -1):
    data = rec[:rec_end]
    if (data.startswith('J:')):
      xs = data.split(':')[1].split(',')
      x = xs[0]
      y = xs[1]
      z = xs[2]
      print "Joystick = X: " + x + ", Y: " + y + ", Z: " + z
    elif (data.startswith("A:")):
      xs = data.split(':')[1].split(',')
      x = xs[0]
      y = xs[1]
      z = xs[2]
      print "Accl = X: " + x + ", Y: " + y + ", Z: " + z

  rec = rec[rec_end+1:]

print ("Closing socket")
sock.close()
