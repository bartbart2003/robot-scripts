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
GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(32, GPIO.OUT)
GPIO.setup(31, GPIO.IN)

GPIO_TRIGGER = 32
GPIO_ECHO = 31

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


# |16|22|29|
def lineFollower():
	flPWM = GPIO.PWM(15, 60)
	blPWM = GPIO.PWM(13, 60)
	brPWM = GPIO.PWM(18, 60)
	frPWM = GPIO.PWM(11, 60)
	currentState = 6
#	flPWM.start(80)
#	time.sleep(2)
#	flPWM.stop()
#	frPWM.start(80)
#	time.sleep(2)
#	frPWM.stop()
#	blPWM.start(80)
#	time.sleep(2)
#	blPWM.stop()
#	brPWM.start(80)
#	time.sleep(2)
#	brPWM.stop()
	while True:
		if GPIO.input(16) == GPIO.LOW and GPIO.input(22) == GPIO.HIGH and GPIO.input(29) == GPIO.LOW:
			if currentState != 0:
                                flPWM.stop()
                                brPWM.stop()
                                blPWM.stop()
                                frPWM.stop()
				flPWM.start(70)
				frPWM.start(70)
				currentState = 0
		elif GPIO.input(16) == GPIO.HIGH and GPIO.input(22) == GPIO.LOW and GPIO.input(29) == GPIO.LOW:
			if currentState != 1:
				flPWM.stop()
				brPWM.stop()
				blPWM.stop()
				frPWM.stop()
				flPWM.start(70)
				currentState = 1
                elif GPIO.input(16) == GPIO.LOW and GPIO.input(22) == GPIO.LOW and GPIO.input(29) == GPIO.HIGH:
                        if currentState != 2:
                                flPWM.stop()
                                brPWM.stop()
                                blPWM.stop()
                                frPWM.stop()
                                frPWM.start(70)
                                currentState = 2
                elif GPIO.input(16) == GPIO.HIGH and GPIO.input(22) == GPIO.HIGH and GPIO.input(29) == GPIO.LOW:
                        if currentState != 3:
                                flPWM.stop()
                                brPWM.stop()
                                blPWM.stop()
                                frPWM.stop()
                                flPWM.start(70)
				brPWM.start(70)
                                currentState = 3
                elif GPIO.input(16) == GPIO.LOW and GPIO.input(22) == GPIO.HIGH and GPIO.input(29) == GPIO.HIGH:
                        if currentState != 4:
                                flPWM.stop()
                                brPWM.stop()
                                blPWM.stop()
                                frPWM.stop()
                                frPWM.start(70)
				blPWM.start(70)
                                currentState = 4
		else:
			currentState = 5
			cc.stopAll()

def distanceStop():
	alreadyStopped = False
	while True:
		dist = distance()
		if dist < 22:
			if alreadyStopped == False:
				cc.stopAll()
				alreadyStopped = True
		elif dist > 28:
			alreadyStopped = False
		time.sleep(0.15)

class requestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    lineFollowerEnabled = False
    distanceStopEnabled = False
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
	if requestHandler.lineFollowerEnabled:
		if s.path == "/mc":
			requestHandler.lineFollowerEnabled = False
			requestHandler.p.terminate()
			cc.cleanupGPIOs()
			cc.setupGPIOs()
			cc.stopAll()
			GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(29, GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.setup(32, GPIO.OUT)
			GPIO.setup(31, GPIO.IN)
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

