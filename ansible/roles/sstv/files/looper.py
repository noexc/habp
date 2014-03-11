#!/usr/bin/env python
# W8UPD HABP2
# BSD-3
# (c) 2014 Ricky Elrod

# NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!!
# NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!!

# This script is intended to ONLY ever be run from some kind of init system
# such as Supervisord or Angel. THE PROGRAM IS INTENDED TO ERROR EARLY so that
# the init system can restart it and get it back into a known state.
# DO NOT RUN THIS SCRIPT IN PRODUCTION WITHOUT STUFFING IT BEHIND AN INIT SYSTEM
# OF SOME SORT.

# NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!!
# NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!! NOTE!!!

from datetime import datetime
import gps
import os
from sh import aplay, convert, fswebcam, kill, robot36_encode
import shutil
from threading import Thread
import time

if not os.path.exists('/var/tmp/img'):
    os.makedirs('/var/tmp/img')

g = None

class GPSObtainer(Thread):
    def __init__(self):
        Thread.__init__(self)
        global g
        g = gps.gps(mode=gps.WATCH_ENABLE)

    def run(self):
        global g, pid
        try:
            print 'GPSObtainer reporting for duty'
            while True:
                g.next()
        except Exception as e:
            print str(e)
            os._exit(1)

class ImageSnapper(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global g, pid
        try:
            while True:
                print 'ImageSnapper reporting for duty'
                path = '/tmp/img/%s.jpg' % str(time.time())
                fswebcam(resolution='1280x720', device="/dev/video1", save=path)
                shutil.copyfile(path, '/tmp/latest.jpg')
                with open('/var/tmp/img/coordinates.txt', 'a') as log:
                    log.write(path + ': ' + '%f, %f\n' % (g.fix.latitude, g.fix.longitude))
                time.sleep(30)
        except Exception as e:
            print str(e)
            os._exit(1)

class Encoder(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global g, pid
        try:
            while True:
                # Wait 5 seconds so that on the initial go, we have an image from
                # ImageSnapper above.
                time.sleep(5)
                print 'Encoder reporting for duty'
                convert(
                    '/tmp/latest.jpg',
                    '-resize', '320x240!',
                    '-pointsize', '35',
                    '-fill', 'black',
                    '-annotate', '+0+37',
                    'W8UPD',
                    '-fill', 'white',
                    '-annotate', '+0+40',
                    'W8UPD',
                    '-fill', 'black',
                    '-annotate', '+0+230',
                    '%f, %f' % (g.fix.latitude, g.fix.longitude),
                    '-fill', 'white',
                    '-annotate', '+0+233',
                    '%f, %f' % (g.fix.latitude, g.fix.longitude),
                    '/tmp/latest.ppm')
                robot36_encode('/tmp/latest.ppm', '/tmp/latest.wav')
                time.sleep(30)
        except Exception as e:
            print str(e)
            os._exit(1)

class Player(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global pid
        try:
            while True:
                time.sleep(10)
                print 'Player reporting for duty'
                aplay('/tmp/latest.wav')
        except Exception as e:
            print str(e)
            os._exit(1)

gps_thread = GPSObtainer()
gps_thread.start()

imagesnapper_thread = ImageSnapper()
imagesnapper_thread.start()

encoder_thread = Encoder()
encoder_thread.start()

player_thread = Player()
player_thread.start()

while True:
    True
