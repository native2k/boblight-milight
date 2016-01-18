# boblight-milight

## DESCRIPTION

I use some miligt devices (mostly rgb strips) to have same ambiend light in my living room and also use an DIY ambilight on my tv (100 RGB LED) thanks to boblightd. 
I specifically choose to use the milight controller because the have an open API and thanks to 
[http://www.kodinerds.net](http://www.kodinerds.net/index.php/Thread/45134-Milight-mit-Boblight-und-XBMC-Kodi-erste-Versuche/#codeLine_3_105c23) it
is possible to also connect them to boblight. 

But because I use boblight-v4l I only get a white light with this approach (boblight only sends zeros to popen devices for boblight-v4l). So I changed it a bit to read vom /dev/pts and behave like a mono device.

## INSTALL

You need socat to map the devices:

```
# socat -d -d pty,raw,echo=0 pty,raw,echo=0
2016/01/18 11:00:32 socat[2864] N PTY is /dev/pts/4
2016/01/18 11:00:32 socat[2864] N PTY is /dev/pts/5
2016/01/18 11:00:32 socat[2864] N starting data transfer loop with FDs [5,5] and [7,7]
```

From the command output read the output(/dev/pts/4) and input(/dev/pts/5) devices.
                                                                                                                                  

Configure /etc/boblight.conf and set the output device:
```
############################### Milight ###############################

[device]
name        WifiLed
output      /dev/pts/5
channels    3
type   momo
prefix FF
rate 19200
interval    100000
debug        off

[color]
name        WIFIred
rgb            FF0000
#gamma        0.94
#adjust        0.45
blacklevel    0.00

[color]
name        WIFIgreen
rgb            00FF00
#gamma        0.98
#adjust        1.0
blacklevel    0.00

[color]
name        WIFIblue
rgb            0000FF
#gamma        1.01
#adjust        0.63
blacklevel    0.00

[light]
name        WI1
color        WIFIred     WifiLed 1
color        WIFIgreen     WifiLed 2
color        WIFIblue     WifiLed 3
hscan        0 100
vscan        0 100
```

Now set the input device in milight.py and run it with 
```
python milight.py
```