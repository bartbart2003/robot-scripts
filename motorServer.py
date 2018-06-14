import time
import BaseHTTPServer
import os
import robotControl as cc
import multiprocessing
import RPi.GPIO as GPIO

cc.setupGPIOs()

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 80

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO_TRIGGER = 32
GPIO_ECHO = 31
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# distance() based on https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/
def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    return distance

def lineFollower():
	cc.driveForward()
	while True:
		if GPIO.input(16) == GPIO.LOW:
			cc.driveForwardRight()
			while True:
				if GPIO.input(16) == GPIO.HIGH:
					break
			cc.driveForward()
		if GPIO.input(22) == GPIO.LOW:
			cc.driveForwardLeft()
			while True:
				if GPIO.input(22) == GPIO.HIGH:
					break
			cc.driveForward()


def distanceStop():
	alreadyStopped = False
	while True:
		dist = distance()
		if dist < 25:
			if alreadyStopped == False:
				cc.stopAll()
				alreadyStopped = True
		elif dist > 30:
			alreadyStopped = False
		time.sleep(0.15)

class requestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    lineFollowerEnabled = False
    distanceStopEnabled = False
    def do_HEAD(s):
        s.send_response(200)
#        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        s.send_response(200)
#        s.send_header("Content-type", "text/html")
        s.end_headers()
	if requestHandler.lineFollowerEnabled:
		if s.path == "/mc":
			requestHandler.lineFollowerEnabled = False
			requestHandler.p.terminate()
			cc.stopAll()
	else:
		if s.path == "/fw":
			cc.driveForward()
		if s.path == "/bw":
			cc.driveBackward()
		if s.path == "/fl":
			cc.driveForwardLeft()
		if s.path == "/cl":
			cc.driveCircleLeft()
		if s.path == "/fr":
			cc.driveForwardRight()
		if s.path == "/cr":
			cc.driveCircleRight()
		if s.path == "/bl":
			cc.driveBackLeft()
		if s.path == "/br":
			cc.driveBackRight()
		if s.path == "/sa":
			cc.stopAll()
		if s.path == "/lf":
			cc.stopAll()
			if requestHandler.distanceStopEnabled:
				requestHandler.distanceStopEnabled = False
				requestHandler.p2.terminate()
			requestHandler.lineFollowerEnabled = True
			requestHandler.p = multiprocessing.Process(target=lineFollower)
			requestHandler.p.daemon = True
			requestHandler.p.start()
		if s.path == "/de":
			if requestHandler.distanceStopEnabled == False:
				requestHandler.distanceStopEnabled = True
				requestHandler.p2 = multiprocessing.Process(target=distanceStop)
				requestHandler.p2.daemon = True
				requestHandler.p2.start()
		if s.path =="/dd":
			if requestHandler.distanceStopEnabled:
				requestHandler.distanceStopEnabled = False
				requestHandler.p2.terminate()
	if s.path == "/sd":
			cc.cleanupGPIOs()
			os.system("shutdown -h now")
	if s.path == "/rb":
			cc.cleanupGPIOs()
			os.system("reboot -f now")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), requestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print "interrupted"
    cc.cleanupGPIOs()
