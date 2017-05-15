#!/usr/bin/python
import RPi.GPIO as GPIO
import sys, os, glob, time
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import time
from threading import Timer

pin = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
speed = 10
i=0
AWS_ACCESS = 'AKIAIBULVVA4U4G2MKGA'
AWS_SECRET = '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'

conn = S3Connection(AWS_ACCESS,AWS_SECRET)
bucket = conn.get_bucket('hackcu-rever')
directory = '/home/pi/Desktop/receive/'

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def getFiles(dir):
    global speed
    if speed == 0:
        os.system("raspistill -q 25 -o /home/pi/Desktop/receive/12345.jpg")
        speed = 1000
        return [os.path.basename(x) for x in glob.glob(str(dir) + '*.jpg')]
    else:
        return None
def setPinHigh():
    GPIO.output(7, GPIO.HIGH)	

def setPinLow():
    GPIO.output(7, GPIO.LOW)

def upload_S3(dir, file):
    k = Key(bucket)
    k.key = f
    setPinHigh()
    k.set_contents_from_filename(dir + f, cb=percent_cb, num_cb=10)
    setPinLow()
        

def removeLocal(dir, file):
    os.remove(dir + file)


#t= Timer(100*60,speed_simulate)
#t.start()


while 1:
    print 'entering next loop'
    filenames = getFiles(directory)
    #print filenames
    if speed > 0 :
        speed = speed - 1
    if filenames is not None:    
        for f in filenames:
            print 'Uploading %s to Amazon S3 bucket %s' % (f, bucket)
            upload_S3(directory, f)
            removeLocal(directory, f)
