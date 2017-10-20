import RPi.GPIO as GPIO
from time import sleep
from firebase import firebase
import pyrebase

config = {
  "apiKey": "AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA",
  "authDomain": "soatp-2dfc9.firebaseapp.com",
  "databaseURL": "https://soatp-2dfc9.firebaseio.com",
  "storageBucket": "soatp-2dfc9.appspot.com"
}

firebase = pyrebase.initialize_app(config)

db = firebase.database()

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24, GPIO.IN)
GPIO.setup(23, GPIO.OUT)


while True:
    sensor = GPIO.input(24) #LEO EL SENSOR INFLARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
    print sensor

    if sensor==0:   
        print "ok"
        salidaLed = db.child("baseDatosSoa/puertas/Puerta Jorge/led/estado").get() #TRAIGO EL VALOR DEL LED DEL FIREBASE
        if salidaLed.val() == "False":
            GPIO.output(23, True) # PRENDO EL LED
        else:
            GPIO.output(23, True)
        sleep(3)
        
    elif sensor==1:
        print "mal"
        salidaLed = db.child("baseDatosSoa/puertas/Puerta Jorge/led/estado").get()
        if salidaLed.val() == "True":
            GPIO.output(23, False)
        else:
            GPIO.output(23, False) 
        sleep(3)
GPIO.cleanup()