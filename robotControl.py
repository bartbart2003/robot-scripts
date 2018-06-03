import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)

def setupGPIOs():
	GPIO.setmode(GPIO.BOARD)
	GPIO.setup(18, GPIO.OUT)
	GPIO.setup(11, GPIO.OUT)
	GPIO.output(18, GPIO.LOW)
	GPIO.output(11, GPIO.LOW)
	GPIO.setup(13, GPIO.OUT)
	GPIO.setup(15, GPIO.OUT)
	GPIO.output(13, GPIO.LOW)
	GPIO.output(15, GPIO.LOW)

def cleanupGPIOs():
	GPIO.cleanup()

def stopAll():
	GPIO.output(18, GPIO.LOW)
	GPIO.output(11, GPIO.LOW)
	GPIO.output(13, GPIO.LOW)
	GPIO.output(15, GPIO.LOW)

def driveBackward():
    stopAll()
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(13, GPIO.HIGH)

def driveForward():
    stopAll()
    GPIO.output(11, GPIO.HIGH)
    GPIO.output(15, GPIO.HIGH)

def driveForwardLeft():
    stopAll()
    GPIO.output(15, GPIO.HIGH)

def driveCircleLeft():
    stopAll()
    GPIO.output(18, GPIO.HIGH)
    GPIO.output(15, GPIO.HIGH)

def driveBackLeft():
    stopAll()
    GPIO.output(13, GPIO.HIGH)

def driveCircleRight():
    stopAll()
    GPIO.output(11, GPIO.HIGH)
    GPIO.output(13, GPIO.HIGH)

def driveForwardRight():
    stopAll()
    GPIO.output(11, GPIO.HIGH)

def driveBackRight():
	stopAll()
	GPIO.output(18, GPIO.HIGH)
