#import RPi.GPIO as GPIO
from time import sleep
#from firebase import firebase
#import firebase ##
import pyrebase

#libreria Pyrebase= https://github.com/thisbejim/Pyrebase
#Firebase /Puerta Fer= https://soatp-2dfc9.firebaseio.com/baseDatosSoa/puertas/Puerta Fer

config = {
  "apiKey": "AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA",
  "authDomain": "soatp-2dfc9.firebaseapp.com",
  "databaseURL": "https://soatp-2dfc9.firebaseio.com",
  "storageBucket": "soatp-2dfc9.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#GPIO.setmode(GPIO.BCM)
#GPIO.setwarnings(False)
#GPIO.setup(24, GPIO.IN)
#GPIO.setup(23, GPIO.OUT)

puerta = "Puerta Fer"
print(puerta) #
simulador = 0 ##

#while True:
while simulador<10: ##
    #sensor = GPIO.input(24) #LEO EL SENSOR INFLARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
    sensor = simulador%2
    
    salidaLed = db.child("baseDatosSoa/puertas").child(puerta).child("led/estado").get() ## #TRAIGO EL VALOR DEL LED DEL FIREBASE
    #print("Sensor=", sensor, " BD Led:", salidaLed.val())
    #db.child("baseDatosSoa/puertas/"+puerta+"/led").update({"estado": sensor}) # Prueba de modificacion
    
    if sensor==0:   
        #print("ok")
        #salidaLed = db.child("baseDatosSoa/puertas/Puerta Fer/led/estado").get() #TRAIGO EL VALOR DEL LED DEL FIREBASE
        if salidaLed.val() == "False":
            #GPIO.output(23, True) # PRENDO EL LED
            print("sensor: 0 / bd led: ", salidaLed.val(), " / Led => ON") ##
        else:
            #GPIO.output(23, True) #False???
            print("sensor: 0 / bd led: ", salidaLed.val(), " / Led => OFF") ##
        #sleep(3)
        
    elif sensor==1:
        #print("mal")
        #salidaLed = db.child("baseDatosSoa/puertas/Puerta Fer/led/estado").get()
        #if salidaLed.val() == "True":
        #    GPIO.output(23, False)
        #else:
        #    GPIO.output(23, False) 
        print("sensor: 1 / bd led: ", salidaLed.val(), " / Led MAL => OFF") ##
        #sleep(3)

        # alterna valor en bd solo en SENSOR = 1
        db.child("baseDatosSoa/puertas/"+puerta+"/led").update({"estado": ("True" if salidaLed.val()=="False" else "False")}) # Prueba de modificacion
    
    
    sleep(5) ##
    simulador = simulador + 1 ##
    
#GPIO.cleanup()
