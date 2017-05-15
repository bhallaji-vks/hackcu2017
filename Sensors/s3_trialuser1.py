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
speed = 100
i=0
AWS_ACCESS = 'AKIAIBULVVA4U4G2MKGA'
AWS_SECRET = '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'

conn = S3Connection(AWS_ACCESS,AWS_SECRET)
bucket = conn.get_bucket('hackcu-rever')
directory = '/home/pi/aws-iot-device-sdk-python/samples/basicPubSub/Adafruit_Python_MCP3008/examples/'

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()

def getFiles(dir1):
    global speed
    if speed == 0:
        print 'Taking Pic'
        os.system("raspistill -o /home/pi/aws-iot-device-sdk-python/samples/basicPubSub/Adafruit_Python_MCP3008/examples/USER1.jpg")
        speed = 1000
        print dir1
        dx = [x for x in glob.glob(str(dir1) + '*.jpg')]
        print len(dx)
        data = [os.path.basename(x) for x in glob.glob(str(dir1) + '*.jpg')]
        #print data
        return(data)
        #return [os.path.basename(x) for x in glob.glob(str(dir) + '*.jpg')]
    else:
        return None
def setPinHigh():
    GPIO.output(7, GPIO.HIGH)	

def setPinLow():
    GPIO.output(7, GPIO.LOW)

def upload_S3(dir1, file):
    k = Key(bucket)
    k.key = f
    setPinHigh()
    k.set_contents_from_filename(dir1 + f, cb=percent_cb, num_cb=10)
    setPinLow()
        

def removeLocal(dir1, file):
    os.remove(dir1 + file)


#t= Timer(100*60,speed_simulate)
#t.start()


while 1:
    filenames = getFiles(directory)
    if filenames is not None:
        print len(filenames)
    if speed > 0 :
        speed = speed - 1
    if filenames is not None:
        print len(filenames)
        for f in filenames:
            print 'Uploading %s to Amazon S3 bucket %s' % (f, bucket)
            upload_S3(directory, f)
            removeLocal(directory, f)
