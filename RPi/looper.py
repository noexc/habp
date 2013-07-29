#!/usr/bin/env python
# This is the main script that takes care of running things on the RPi.
# It interacts closely with the CodeBlock/helium library.
# (c) 2013 Ricky Elrod
# MIT Licensed.

from datetime import datetime
import gps
from sstvcam import sstvcam
from threading import Thread

log = file('/root/looper.log', 'w')
g = None

class GPSObtainer(Thread):
    def __init__(self):
        Thread.__init__(self)
        global g
        g = gps.gps(mode=gps.WATCH_ENABLE)

    def run(self):
        global g
        while True:
            g.next()

thread = GPSObtainer()
thread.start()

while True:
    try:
        sstvcam.take_picture()
        sstvcam.convert_picture_to_ppm()
        sstvcam.overlay_text('W8UPD | %f, %f' % (g.fix.latitude, g.fix.longitude), 'top')
        sstvcam.overlay_text('%0.3fm | %0.3fm/s | Hello!' % (g.fix.altitude, g.fix.speed), 'bottom')
        sstvcam.make_sstv()
        sstvcam.play_sstv()
    except Exception as e:
        log.write('[EXCEPTION] [%s] %s\n' % (str(datetime.now()), str(e)))
        log.flush()
