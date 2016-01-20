#!/usr/bin
from controller import milightController
import logging
import os

DEVICE = "/tmp/pts_out"

CONTROLLER_HOST = "192.168.111.201"
CONTROLLER_PORT = 8899

BRIGHTNESS = 100
GROUP = 1
CONTROLLER_TYPE = 'sock'

HEADER = [0xff]
GROUPS = [1]
COUNT_COLOR = 3

logger = logging.getLogger('milightRun')

class boblightMilightConnector:
  def __init__(self):
    self.controller = milightController(CONTROLLER_HOST, CONTROLLER_PORT, group=GROUP, kind=CONTROLLER_TYPE)
    logging.info("Starting .. with %s" % (self.controller, ))
    #self.readInputStream()
    
  @classmethod
  def getData(cls, data, length, pos=0):
      return [ord(n) for n in data[pos:pos + length]]

  def readInputStream(self):
    logger.info('start reading %s ' % (DEVICE, ))
    headerLen = len(HEADER)
    dataLen = len(GROUPS)
    groups = [(n, headerLen + COUNT_COLOR + n * COUNT_COLOR) for n in GROUPS]
    
    # open device
    dev = os.open(DEVICE, os.O_RDWR)
    while True:
      data = os.read(dev, headerLen + (dataLen + 1) * 3)
      # first is header
      # Data: 0xff, 0x1d, 0x18, 0xfd
      header = self.getData(data, headerLen)
      if header != HEADER:
          logger.info('Header (%s) missing in data %s - ignore' % (HEADER, ))
          continue
      
      for group, dStart  in groups:
        color = self.getData(data, dStart, COUNT_COLOR)
        loger.debug("Color :%s " % (color, )) 
        
        # if it is 000000 .. ignore
        if color == [0] * COUNT_COLOR:
            logger.debug('.. is black .. ignore')
        else:
            self.controller.setColor(color, group)

if __name__ == '__main__':

    logging.basicConfig(format='%(message)s')
    logger.setLevel(10)
    
    mc = boblightMilightConnector()
    mc.readInputStream()
