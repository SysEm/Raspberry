import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)
GPIO.setup(18, GPIO.OUT)


while True:
    
    sensor=GPIO.input(25)
    
    if sensor==0:
        GPIO.output(18, GPIO.HIGH)
        print("DETECTADO")
        sleep(0.5)

    elif sensor==1:
        GPIO.output(18, GPIO.LOW)
        print("NADA")
    #sleep(0.1)
