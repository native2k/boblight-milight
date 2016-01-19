import colorsys
import sys
import os
import socket
import milight

logger=None

CONTROLLER_HOST = "192.68.111.201"
CONTROLLER_PORT = 8899
READ_DEV = '/dev/pts/4'
WRITE_DEV = ''

HEADER = [0xff]
COUNT_LED = 100
COUNT_COLOR = 3


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
      self.logfile.write(str(msg) + "\n")
      self.logfile.flush()

def Proxy:
    def __init__(self, host, port, readDevice, writeDevice, group=1, lightType='rgb', initColor=None, brightness=100):
        self.milight = milight.MiLight({'host': host, 'port': port})
        self.light = milight.LightBulb([lightType])
        self.group = group
        self.initColor(initColor, brightness)
        self.readDevice = readDevice
        self.writeDevice = writeDevice


    def initColor(self, color=None, brightness=100):
        """ turns light on etc """
        self.controller.send(self.light.on(self.group))
        self.controller.send(self.light.brightness(brightness, self.group))
        if color:
            self.setColor(color)

    def setColor(self, color):
        """ sets the color tuple """
        self.controller.send(self.loght.color(milight.color_from_rgb(*color), self.group))
    
    def readInputStream(self):
        headerLen = len(HEADER)
        msgLen = headerLen + COUNT_LED * COUNT_COLOR

        readDev = os.open(self.readDevice, os.O_RD)
        writeDev = os.open(self.writeDevice, os.O_WR)
        while True:
            data = os.read(readDev, msgLen + 3)
            # logger.writeLine('DATA: %s' % ([ord(n) for n in data], ))
            # forward to write Dev
            os.write(data[:-3])

            # first is header - check to be sure
            res = [ord(n) for n in data[:headerLen]]
            if res != HEADER:
                loggger.writeline('Header (%s) missing in data %s - ignore' % (HEADER, res))
                continue
 
            myColor = [ord(n) for n in data[-3:]]  # only last bytes are our color
            logger.writeLine("Input: %s" %  (res, ))

            if myColor == [0, 0, 0]:
                # all whit .. do nothing
                logger.writeline('received Color white .. do nothing')
                pass
            else:
                # set the color
                self.setColor(*myColor)



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
    
logger=Logger(True,"/tmp/proxy.log")
p = Proxy(CONTROLLER_HOST, CONTROLLER_PORT, READ_DEV, WRITE_DEV, initColor=(0xFF,0 , 0))
