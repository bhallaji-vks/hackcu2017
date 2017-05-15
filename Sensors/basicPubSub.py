'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import RPi.GPIO as GPIO
# Import SPI library (for hardware SPI) and MCP3008 library.
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
#import MFRC522
import signal
import sys, os, glob, time
from boto.s3.connection import S3Connection
from boto.s3.key import Key

continue_reading = True

# Software SPI configuration:
#CLK  = 18
#MISO = 23
#MOSI = 24
#CS   = 25
#mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)




print('Reading MCP3008 values, press Ctrl-C to quit...')
# Print nice channel column headers.
print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*range(8)))
print('-' * 57)
# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print "Ctrl+C captured, ending read."
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
#MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

pin = 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin, GPIO.OUT)
speed = 100
i=0
AWS_ACCESS = 'AKIAIBULVVA4U4G2MKGA'
AWS_SECRET = 'BV4/DApjO3CeOUG4qWjSLM91PgJqrOycefEygEds'

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



# Custom MQTT message callback
def customCallback(client, userdata, message):
	print("Received a new message: ")
	print(message.payload)
	print("from topic: ")
	print(message.topic)
	print("--------------\n\n")

# Usage
usageInfo = """Usage:

Use certificate based mutual authentication:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

Use MQTT over WebSocket:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -w

Type "python basicPubSub.py -h" for available options.
"""
# Help info
helpInfo = """-e, --endpoint
	Your AWS IoT custom endpoint
-r, --rootCA
	Root CA file path
-c, --cert
	Certificate file path
-k, --key
	Private key file path
-w, --websocket
	Use MQTT over WebSocket
-h, --help
	Help information


"""

# Read in command-line parameters
useWebsocket = False
host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
try:
	opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA=", "websocket"])
	if len(opts) == 0:
		raise getopt.GetoptError("No input parameters!")
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpInfo)
			exit(0)
		if opt in ("-e", "--endpoint"):
			host = arg
		if opt in ("-r", "--rootCA"):
			rootCAPath = arg
		if opt in ("-c", "--cert"):
			certificatePath = arg
		if opt in ("-k", "--key"):
			privateKeyPath = arg
		if opt in ("-w", "--websocket"):
			useWebsocket = True
except getopt.GetoptError:
	print(usageInfo)
	exit(1)

# Missing configuration notification
missingConfiguration = False
if not host:
	print("Missing '-e' or '--endpoint'")
	missingConfiguration = True
if not rootCAPath:
	print("Missing '-r' or '--rootCA'")
	missingConfiguration = True
if not useWebsocket:
	if not certificatePath:
		print("Missing '-c' or '--cert'")
		missingConfiguration = True
	if not privateKeyPath:
		print("Missing '-k' or '--key'")
		missingConfiguration = True
if missingConfiguration:
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
#myAWSIoTMQTTClient.subscribe("sdk/test/Python", 1, customCallback)
#time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
#while continue_reading:
    
    # Scan for cards    
#    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
#    if status == MIFAREReader.MI_OK:
#        print "Card detected"
    
    # Get the UID of the card
#    (status,uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
#    if status == MIFAREReader.MI_OK:

        # Print UID
#        print "Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
#	myAWSIoTMQTTClient.publish("sdk/test/Python", "RFID "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3]), 1)
#	time.sleep(1)
			#"Card read UID: "+str(uid[0])+","+str(uid[1])+","+str(uid[2])+","+str(uid[3])
            #print "welcome hari"
        # This is the default key for authentication
#        key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
        # Select the scanned tag 
#        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
#        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
#        if status == MIFAREReader.MI_OK:
#            MIFAREReader.MFRC522_Read(8)
#            MIFAREReader.MFRC522_StopCrypto1()
#        else:
#            print "Authentication error"
conn = S3Connection(AWS_ACCESS,AWS_SECRET)
bucket = conn.get_bucket('hackcu-rever')
while True:    
    # Hardware SPI configuration:
    SPI_PORT   = 0
    SPI_DEVICE = 0
    mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
    values = [0]*8
    for i in range(8):
    # The read_adc function will get the value of the specified channel (0-7).
        values[i] = mcp.read_adc(i)
    # Print the ADC values.
    print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    time.sleep(0.5)
    
    #values = [0]*8
    #for i in range(8):
        # The read_adc function will get the value of the specified channel (0-7).
     #    values[i] = mcp.read_adc(i)
    # Print the ADC values.
   # print('| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |'.format(*values))
    # Pause for half a second.
    #time.sleep(0.5)
    #myAWSIoTMQTTClient.publish("sdk/test/Python", "| {0:>4} | {1:>4} | {2:>4} | {3:>4} | {4:>4} | {5:>4} | {6:>4} | {7:>4} |".format(*values), 1)
    myAWSIoTMQTTClient.publish("sdk/test/Python", "| 1234 |"+str(values[1]), 1)
    # myAWSIoTMQTTClient.publish("sdk/test/Python", "RFID " + str(loopCount), 1)
    # loopCount += 1
    # time.sleep(1)





	
