import colorsys
import socket
import milight
import argparse
import logging
from pprint import pformat

logger = logging.getLogger('testmilight')


CONTROLLER_HOST = "192.68.111.201"
CONTROLLER_PORT = 8899

BRIGHTNESS = 10
GROUP = 1


class MilightControllerLib:

    def __init__(self, host, port, group=1, lightType='rgb', initColor=None, brightness=100):
        self.controller = milight.MiLight({'host': host, 'port': port}, wait_duration=0)
        self.light = milight.LightBulb([lightType])
        self.group = group
        logger.info('Controller: %s Light: %s Group: %s' % (self.controller, self.light, self.group))
        self.initColor(initColor, brightness)

    def initColor(self, color=None, brightness=100):
        """ turns light on etc """
        r = self.controller.send(self.light.on(self.group))
        logger.debug('Turned on lights (group: %s): %s' % (self.group, r))
        r = self.controller.send(self.light.brightness(brightness, self.group))
        logger.debug('Set brightness to %s (group: %s): %s' % (brightness, self.group, r))
        if color:
            self.setColor(color)

    def setColor(self, color):
        """ sets the color tuple """
        r = self.controller.send(self.light.color(milight.color_from_rgb(*color), self.group))
        logger.debug('Set color to %s (group: %s): %s' % (color, self.group, r))


class MilightControllerSock:
    ip = None
    port = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    GROUP_PREFIX = ["\xC2", "\xC5", "\xC7", "\xC9", "\xCB"]

    def __init__(self, host, port, group=1, lightType='rgb', initColor=None, brightness=100):
        self.ip = host
        self.port = port
        self.group = group
        if initColor:
            self.setColor(initColor)

    def setColor(self, color):
        return self.setRGB(*[float(d) / 255 for d in color])

    def setRGB(self, r, g, b):
        logger.debug('R: %.3f G: %.3f B: %3.f' % (r, g, b))
        h, s, v = colorsys.rgb_to_hsv(float(r), float(g), float(b))
        logger.debug("H: " + str(h) + " S: " + str(s) + " v: " + str(v))
        if(s < 0.02):
            # Alle Lampen in den Weissen Modus versetzen (C2 Alle, C5 Group1, C7 Group2, C9 Group3, CB Group4)
            # MESSAGE1 = "\xC5\x00"
            MESSAGE1 = self.GROUP_PREFIX[self.group] + "\x00"
            if(h > 0.3333):
                htmp = h - 0.3333
                logger.debug("Vk1: " + str(htmp))
                vtmp = htmp / 0.6666
                logger.debug("Vk2: " + str(vtmp))
                vtmp = (2 * vtmp)
                logger.debug("Vk3: " + str(vtmp))
                v = v / vtmp
                logger.debug("Vk4: " + str(v))
        else:
            # Korrektur Gelb
            if (h < 0.33333):
                h = h * 0.5
            # Korrektur Cyan
            if (h > 0.33333 and h < 0.5):
                h = h * 0.9
            if(h > 0.3333):
                htmp = h - 0.3333
                logger.debug("Vk1: " + str(htmp))
                vtmp = htmp / 0.6666
                logger.debug("Vk2: " + str(vtmp))
                vtmp = (2 * vtmp)
                logger.debug("Vk3: " + str(vtmp))
                v = v / vtmp
                logger.debug("Vk4: " + str(v))
            h = int((h) * 256)
            # Korrektur Farbverschiebung
            h = h + 85
            if(h > 256):
                h = 256 - (h % 256)
            else:
                h = abs(h - 256)
            h = int(h)
            # Wechseln der Farbe x40 zu Wert (h)
            MESSAGE1 = "\x40" + chr(h)
        if (v >= 0.75):
            v = 0.75
        v = v * 25
        v = int(round(v))
        v = v + 2
        v = min(27, v)
        v = max(2, v)
        # Helligkeit des Weissen Modus im Standby
        MESSAGE2 = "\x4E" + chr(v)
        logger.debug("H2: " + str(h) + " S2: " + str(s) + " v2: " + str(v))
        r1 = self.sock.sendto(MESSAGE1, (self.ip, self.port))
        r2 = self.sock.sendto(MESSAGE2, (self.ip, self.port))
        logger.debug("response: %s %s" % (r1, r2))


def milightController(*args, **kwargs):
    kind = 'sock'
    if 'kind' in kwargs:
        kind = kwargs.get('kind', 'sock').lower()
        del(kwargs['kind'])

    controller = (kind == 'sock') and MilightControllerSock or MilightControllerLib
    logger.debug('Build Controller: %s' % controller)
    return controller(*args, **kwargs)


def main():
    logging.basicConfig(format='%(message)s')

    parser = argparse.ArgumentParser(description='send some commands to the milight bridge')
    parser.add_argument('color', metavar='COLOR', type=str, help='the color in hex (exp: 00FFA1)')
    parser.add_argument(
        '--host', dest='host',
        default=CONTROLLER_HOST,
        help='host of the controller (default: %s)' % (CONTROLLER_HOST,))
    parser.add_argument(
        '--port', dest='port',
        default=CONTROLLER_PORT,
        help='port of the controller (default: %d)' % (CONTROLLER_PORT, ))
    parser.add_argument(
        '--brightness', '-b', dest='brightness',
        default=BRIGHTNESS,
        help='brightness (default: %d)' % (BRIGHTNESS, ))
    parser.add_argument(
        '--group', '-g', dest='group',
        default=GROUP,
        help='group - 0 for all  (default: %d)' % (GROUP, ))
    parser.add_argument(
        '--debug', '-d', dest='debug', action='store_true',
        help='enable debug ')
    parser.add_argument(
        '--lib', '-l', dest='lib', action='store_true',
        help='use lib milight instead of self build')

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(10)

    logger.info('Arguments: %s' % (pformat(args), ))
    # parse color
    try:
        color = [int(args.color[n * 2:(n * 2) + 2], 16) for n in range(3)]
    except Exception, e:
        logger.error('Unable to parse colorstring %s : %s' % (args.color, e))

    kind = args.lib and 'lib' or 'sock'

    milightController(args.host, args.port, args.group, initColor=color, brightness=args.brightness, kind=kind)

if __name__ == '__main__':
    main()
