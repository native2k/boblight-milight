#!/usr/bin
from controller import milightController
import logging
import os

DEVICE = "/tmp/pts_out"

CONTROLLER_HOST = "192.168.111.201"
CONTROLLER_PORT = 8899

BRIGHTNESS = 100
GROUP = 1
#CONTROLLER_TYPE = 'lib'  # 'sock'
CONTROLLER_TYPE = 'sock'
CONTROLLER_TYPE = 'self'

from time import time 

HEADER = [0xff]
GROUPS = [1]
COUNT_COLOR = 3

logger = logging.getLogger('milightRun')

AMOUNT = -1  # no performance checking 
# AMOUNT = 1000


class FifoBuffer:
    def __init__(self, size):
        #self.size = size
        self._data = [0] * size

    def add(self, value):
        self._data.pop(0)
        self._data.append(value)
        #while len(self._data) > self.size:
        #    self._data.pop(0)

    @property
    def data(self):
        return self._data

    @property
    def sum(self):
        return sum(self._data)

    @property
    def len(self):
        return len(self._data)

    @property
    def avg(self):
        return self.sum / self.len


class smootherMovingAverage:
    def __init__(self, size=100):
        self._data = FifoBuffer(size)

    def calc(self, value):
        self._data.add(value)
        return self._data.avg

class smootherNone:
    def __init__(self, *args):
        pass

    def calc(self, value):
        return value

class boblightMilightConnector:
  def __init__(self):
    self.controller = milightController(CONTROLLER_HOST, CONTROLLER_PORT, group=GROUP, kind=CONTROLLER_TYPE)
    logging.info("Starting .. with %s" % (self.controller, ))
    # self.readInputStream()
    self.smoothers = {}
    for group in GROUPS:
        smoother = smootherMovingAverage(500)
        # smoother = smootherNone()
        self.smoothers[group] = smoother

  @classmethod
  def getData(cls, data, length, pos=0):
      return [ord(n) for n in data[pos:(pos + length)]]

  def readInputStream(self):
    logger.info('start reading %s ' % (DEVICE, ))
    headerLen = len(HEADER)
    dataLen = len(GROUPS)
    groups = [(n, headerLen + ((i + 1) * COUNT_COLOR)) for i, n in enumerate(GROUPS)]
    logger.debug('Groups: %s' % (groups, ))

    # open device
    dev = os.open(DEVICE, os.O_RDWR)

    # do some performance checking 
    if AMOUNT > 0:
        start = time()
    countn = AMOUNT

    while True:
      data = os.read(dev, headerLen + (dataLen + 1) * 3)
      if logger.isEnabledFor(logging.debug):
          logger.debug('MSG: %s' % ( self.getData(data, len(data)), ))
      
      if countn > 0:
          countn -= 1
      elif countn == 0:
          print "%d loop took  %.3fsek" % (AMOUNT, time() - start)
          countn = AMOUNT
          start = time()
      # first is header
      # Data: 0xff, 0x1d, 0x18, 0xfd
      header = self.getData(data, headerLen)
      if header != HEADER:
          logger.info('Header (%s) missing in data %s - ignore' % (HEADER, ))
          continue
      
      for group, dStart  in groups:
        color = self.getData(data, COUNT_COLOR, dStart)
        logger.debug("Color(group: %s): %s pos: %s" % (group, color, dStart)) 
        
        # if it is 000000 .. ignore
        if color == [0] * COUNT_COLOR:
            logger.debug('.. is black .. ignore')
        else:
            self.controller.setColor(color, group, self.smoothers[group])

if __name__ == '__main__':

    logging.basicConfig(format='%(message)s')
    #logger.setLevel(10)
    
    mc = boblightMilightConnector()
    mc.readInputStream()
