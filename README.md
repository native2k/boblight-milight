# boblight-milight

## DESCRIPTION

I use some miligt devices (mostly rgb strips) to have same ambiend light in my living room and also use an DIY ambilight on my tv (100 RGB LED) thanks to boblightd. 
I specifically choose to use the milight controller because the have an open API and thanks to 
[http://www.kodinerds.net](http://www.kodinerds.net/index.php/Thread/45134-Milight-mit-Boblight-und-XBMC-Kodi-erste-Versuche/#codeLine_3_105c23) I got inspired to connect them also to my existing ambilight sollution as second device.

I had to changed his implentation a bit because the pipe solution worked good when it was the only device but in combination with my existing 100 light of the momo device it was not very stable. 

Now I have boblightd write to a linux device, just as it where a momo device (because this is such a simple format) and the a python script reads this data decodes it and send it to an milight bridge.
To setup, you also need to install `socat` which should be available in all linux distributions.

On my client (which is oblight-v4l on an old cubieboard) it seems like the first light always gets only 0,0,0 values. So I configured the first light also send to the pts and just ignore it in the python script.

The milight API is quite simple and documentation is available at [http://www.limitlessled.com/dev/](http://www.limitlessled.com/dev/). Problem is when you change the color you schould send an ON command for the specific group
first and shortly after the collor value but because the ON command is also used for pairing (in first 2sek when you turn on the controller/light) and we are sending colors quite often any devices in the house just connected to 
power would probably be paired to our wlan bridge. So I don't send the ON command everytime, which is no problem as long as you have not any other light binded to the same bridge and turned on this devices manully. Then you will have the collor changing on this device because the bridge just gets the set color command. 

So I would advice to use one seperate bridge only for devices related to ambilight.

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

# this one always gets only zeros as color value .. I have no idea why
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

