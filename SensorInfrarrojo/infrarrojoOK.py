import RPi.GPIO as GPIO
from time import sleep
import pyrebase

#libreria Pyrebase= https://github.com/ozgur/python-firebase
#Firebase /Puerta Fer= https://soatp-2dfc9.firebaseio.com/baseDatosSoa/puertas/Puerta 

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
GPIO.setup(24, GPIO.IN) # SETEO PUERTO COMO ENTRADA DIGITAL DEL SENSOR
GPIO.setup(23, GPIO.OUT) # SETEO PUERTO COMO SALIDA DIGITAL DEL SENSOR

puerta = "Puerta Fer"
print(puerta) 

while True:
    sensor = GPIO.input(24) #LEO EL SENSOR INFLARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
    salidaLed = db.child("baseDatosSoa/puertas").child(puerta).child("led/estado").get() ## TRAIGO EL VALOR DEL ESTADO DEL LED EN FIREBASE
    
    if (salidaLed.val() == "True"):
        print("Estado actual: True")
    elif (salidaLed.val() == "False"):
        print("Estado actual: False")

    print("------------------------------")

    if sensor==0:   
        print("Se detecto algo")
        GPIO.output(23, True) # PRENDO EL LED
        if (salidaLed.val() == "False"):
            print("Detect: ON - LED EN BDD EN FIREBASE: ON ")
            #Actualizo Firebase con el estado actual de la puerta
            db.child("baseDatosSoa/puertas/"+puerta+"/led").update({"estado": ("True" if salidaLed.val()=="False" else "True")})
        else:
            print("Detect: ON - LED EN BDD EN FIREBASE: ON ")
    
    elif sensor==1:
        print("No se detecta nada")
        GPIO.output(23, False)
        print("Detect: OFF - LED EN BDD EN FIREBASE: OFF ")
        #Actualizo Firebase con el estado actual de la puerta
        db.child("baseDatosSoa/puertas/"+puerta+"/led").update({"estado": ("False" if salidaLed.val()=="True" else "False")}) 
    sleep(5) 
GPIO.cleanup()
