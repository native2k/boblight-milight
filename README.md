# boblight-milight

## DESCRIPTION

I use some miligt devices (mostly rgb strips) to have same ambiend light in my living room and also use an DIY ambilight on my tv (100 RGB LED) thanks to boblightd. 
I specifically choose to use the milight controller because the have an open API and thanks to 
[http://www.kodinerds.net](http://www.kodinerds.net/index.php/Thread/45134-Milight-mit-Boblight-und-XBMC-Kodi-erste-Versuche/#codeLine_3_105c23) it
is possible to also connect them to boblight.

I changed his implentation a bit because the pipe solution worked good when it was the only device but in combination with my momo devices it was not that stable. 

Now it can read the momo format too from an linux device. So you also need socat the setup the devices than let boblight write into this device and currently a 
python script (run.py) to read from this device and send the data to the milight controller.

On my client (which is running boblight-v4l on an old cubieboard) it seems like the first light always gets only 0,0,0 values. So I configured the first light also send to the pts and just ignore in the python script.

## INSTALL

You need socat to map the devices:

```
# socat -d -d pty,raw,echo=0,link=/tmp/pts_out pty,raw,echo=0,link=/tmp/pts_in
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
output      /dev/pts_in
channels    6
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

[light]
name        WI2
color        WIFIred     WifiLed 4
color        WIFIgreen     WifiLed 5
color        WIFIblue     WifiLed 6
hscan        0 100
vscan        0 100
```

Now set the input device in run.py and run it.

You can find 3 different implementation for the communication with milight. 

  - `MilightControllerSock` taken from [http://www.kodinerds.net](http://www.kodinerds.net/index.php/Thread/45134-Milight-mit-Boblight-und-XBMC-Kodi-erste-Versuche/#codeLine_3_105c23) - worked fine but it also uses dynamic brightness which resulted in quite a dark room 
  - `MilightControllerLib` just uses the milight (pip install milight) library but is too slow 
  - `MilightControllerSelf` this is like a mixture of the above .. uses the color calculation of the milight lib and does not change the brightness but uses socket to talk to the device 

```
python run.py
```

