import colorsys
import sys
import os
import socket
import milight
logger=None

CONTROLLER_HOST = "192.68.111.201"
CONTROLLER_PORT = 8899
DEVICE = '/tmp/pts_out'

# Command:
# socat -d -d pty,raw,echo=0 pty,raw,echo=0

# Example conf:
#[device]
#name        WifiLed
#output      /dev/pts/5
#channels    3
#type   momo
#prefix FF
#rate 19200


class Logger:
  logfile=None
  def __init__(self,activateLogging,path):
    if(activateLogging):
      self.logfile = file(path, "wb")

  def writeLine(self,msg):
    if(self.logfile!=None):
      self.logfile.write(str(msg) +"\n")
      self.logfile.flush()

class boblightMilightConnector:
  def __init__(self):
    self.readInputStream()

  def readInputStream(self):
    #IP und Port des Controller (Bridge) oder ggf. auch ein LD382 (Magic UFO)
    #milight=milightController(CONTROLLER_HOST, CONTROLLER_PORT)
    controller = milight.MiLight({'host': '192.168.111.201', 'port': 8899}, wait_duration=0)
    light = milight.LightBulb(['rgb'])
    controller.send(light.on(1))
    controller.send(light.color(milight.color_from_rgb(0xff, 0xff, 0), 1)) 

    dev = os.open(DEVICE, os.O_RDWR)
    while True:
      data = os.read(dev,10)
      # first ff is header
      # Data: 0xff, 0x1d, 0x18, 0xfd
      res = [ord(n) for n in data]
      if res[0] != 0xff:
          logger.writeLine('Header (ff) missing in data %s - ignore' % (res, ))
          continue
      #input = sys.stdin.readline()
      logger.writeLine("Input: %s" %  (res, ))
      if res == [0xff, 0, 0, 0]:
          # all whit .. do nothing
          pass
      else:
        r = (res[0]) #/ 255
        g = (res[1]) #/ 255
        b = (res[2]) #/ 255
        #milight.setRGB(r,g,b)
        controller.send(light.color(milight.color_from_rgb(r, g, b), 1))
 
class milightController:
  ip=None
  port=None
  sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
  def __init__(self,IP,Port):
    self.ip=IP
    self.port=Port
  def setRGB(self,r,g,b):
    h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
    logger.writeLine("H: "+str(h)+" S: "+str(s)+" v: "+str(v))
    if(s<0.02):
      #Alle Lampen in den Weissen Modus versetzen (C2 Alle, C5 Group1, C7 Group2, C9 Group3, CB Group4)
      MESSAGE1 = "\xC5\x00"
      if(h>0.3333):
        htmp=h-0.3333
        logger.writeLine("Vk1: "+str(htmp))
        vtmp=htmp/0.6666
        logger.writeLine("Vk2: "+str(vtmp))
        vtmp=(2*vtmp)
        logger.writeLine("Vk3: "+str(vtmp))
        v=v/vtmp
        logger.writeLine("Vk4: "+str(v))
    else:
      #Korrektur Gelb
      if (h < 0.33333):
        h= h *0.5
      #Korrektur Cyan
      if (h > 0.33333 and h < 0.5):
        h= h*0.9
      if(h>0.3333):
        htmp=h-0.3333
        logger.writeLine("Vk1: "+str(htmp))
        vtmp=htmp/0.6666
        logger.writeLine("Vk2: "+str(vtmp))
        vtmp=(2*vtmp)
        logger.writeLine("Vk3: "+str(vtmp))
        v=v/vtmp
        logger.writeLine("Vk4: "+str(v))
      h = int((h) * 256)
      #Korrektur Farbverschiebung
      h=h+85
      if(h>256):
        h=256-(h%256)
      else:
        h=abs(h-256)
      h=int(h)
      #Wechseln der Farbe x40 zu Wert (h)
      MESSAGE1 = "\x40" + chr(h)
    if (v>=0.75):
      v=0.75
    v=v*25
    v=int(round(v))
    v=v+2
    v=min(27,v)
    v = max(2,v)
    #Helligkeit des Weissen Modus im Standby
    MESSAGE2 = "\x4E" + chr(v)
    logger.writeLine("H2: "+str(h)+" S2: "+str(s)+" v2: "+str(v))
    self.sock.sendto(MESSAGE1, (self.ip, self.port))
    self.sock.sendto(MESSAGE2, (self.ip, self.port))
    
logger=Logger(True,"/tmp/milight.log")
boblightMilightConnector()
