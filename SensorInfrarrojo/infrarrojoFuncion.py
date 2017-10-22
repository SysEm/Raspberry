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
GPIO.setup(24, GPIO.IN) #SETEO PUERTO COMO ENTRADA DIGITAL DEL SENSOR
GPIO.setup(23, GPIO.OUT) # SETEO PUERTO COMO SALIDA DIGITAL DEL SENSOR

puerta = "Puerta Jorge"
print(puerta) 

################## FUNCION  ##################

def firebase_(puerta_, estado_): 
    if (estado_ == "False"):
        db.child("baseDatosSoa/puertas/"+puerta_+"/led").update({"estado": ("True" if estado_=="False" else "True")})
    elif (estado_ == "True"):
        db.child("baseDatosSoa/puertas/"+puerta_+"/led").update({"estado": ("False" if estado_=="True" else "False")}) 

################## FIN FUNCION  ##################

while True:
    sensor = GPIO.input(24) #LEO EL SENSOR INFRARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
    salidaLed = db.child("baseDatosSoa/puertas").child(puerta).child("led/estado").get() ## TRAIGO EL VALOR DEL ESTADO DEL LED EN FIREBASE
    
    if (salidaLed.val() == "True"):
        print("Estado actual: True")
    elif (salidaLed.val() == "False"):
        print("Estado actual: False")

    print("------------------------------")

    if sensor==0:   
        print("Se detecto algo")
        GPIO.output(23, True) # PRENDO EL LED
        print("Detect: ON - LED EN BDD EN FIREBASE: ON ")
        if (salidaLed.val() == "False"):
             firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE
    
    elif sensor==1:
        print("No se detecta nada")
        GPIO.output(23, False)
        print("Detect: OFF - LED EN BDD EN FIREBASE: OFF ")
        if (salidaLed.val() == "True"):
            firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE
            
    sleep(3) 
GPIO.cleanup()
