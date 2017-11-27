import datetime
from time import sleep


import json
from collections import OrderedDict
import collections
from firebase import jsonutil
#from firebase.firebase import FirebaseApplication, FirebaseAuthentication
import pyrebase

import puertasfunciones as fn


#libreria Pyrebase= https://github.com/ozgur/python-firebase
#libreria Python-Firebase= https://soatp-2dfc9.firebaseio.com/baseDatosSoa/puertas/Puerta 

########### VARIABLES GLOBALES ############


###########  CONFIGURACIONES   ############
# Info Base de Datos Firebase
puertaDesdeRaspi="PuertaLecAppEscRas"
puertaHaciaRaspi="PuertaEscAppLecRas"
DSN = 'https://soatp-2dfc9.firebaseio.com'
archDesdeRaspi=fn.abs_path(puertaDesdeRaspi+".json")
archHaciaRaspi=fn.abs_path(puertaHaciaRaspi+".json")
#fbase = FirebaseApplication(DSN, None)

'''
def firebase_(puerta_, estado_): 
    if (estado_ == "False"):
        db.child("baseDatosSoa/"+puertaHaciaRaspi+"/led").update({"estado": ("True" if estado_=="False" else "True")})
    elif (estado_ == "True"):
        db.child("baseDatosSoa/"+puertaDesdeRaspi+"/led").update({"estado": ("False" if estado_=="True" else "False")}) 
config = {
  "apiKey": "AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA",
  "authDomain": "soatp-2dfc9.firebaseapp.com",
  "databaseURL": "https://soatp-2dfc9.firebaseio.com",
  "storageBucket": "soatp-2dfc9.appspot.com"
}
'''
config = {
  "apiKey": "AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA",
  "authDomain": "soatp-2dfc9.firebaseapp.com",
  "databaseURL": "https://soatp-2dfc9.firebaseio.com",
  "storageBucket": "soatp-2dfc9.appspot.com"
}
# Valores usados en BBDD (Firebase)
P_LED_EST_ON = "on"
P_LED_EST_OFF = "off"
P_PRES_EST_ON = "on"
P_PRES_EST_OFF = "off"
P_SERV_ANG_ABIERTO = 1
P_SERV_ANG_CERRADO = 0
P_SERV_ESFUERZO_SI = 1
P_SERV_ESFUERZO_NO = 0

PuertaRaspi = {"Led": {"estado": P_LED_EST_OFF}, "Presencia": {"estado": P_PRES_EST_OFF}, "Servo": {"angulo": P_SERV_ANG_CERRADO, "esfuerzo": P_SERV_ESFUERZO_NO}}
PuertaBBDD = {"Led": {"estado": P_LED_EST_OFF}, "Presencia": {"estado": P_PRES_EST_OFF}, "Servo": {"angulo": P_SERV_ANG_CERRADO, "esfuerzo": P_SERV_ESFUERZO_NO}}

pybase = pyrebase.initialize_app(config)
db = pybase.database()
fn.log.debug("Conecto Pyrebase")

###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	print('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

#Recupera/consulta puerta en Firebase
def obtenerPuerta(idpuerta):
	dbpuerta = db.child("baseDatosSoa").child(idpuerta).get()
	return dbpuerta.val()
	#return fbase.get('/baseDatosSoa', idpuerta,params={'print': 'pretty'},headers={'X_FANCY_HEADER': 'very fancy'})

#Actualiza/graba puerta en Firebase
def impactarPuerta(idpuerta,dato):
	return db.child("baseDatosSoa/"+idpuerta).update(dato)
	#return fbase.put('/baseDatosSoa', idpuerta, dato)


def escribirCambiosPuertaApp(puertaNueva):
        global PuertaBBDD

        if not(puertaNueva["Led"]["estado"] == PuertaBBDD["Led"]["estado"] and
		puertaNueva["Servo"]["angulo"] == PuertaBBDD["Servo"]["angulo"]):
		PuertaBBDD["Led"]["estado"] = puertaNueva["Led"]["estado"]
		PuertaBBDD["Servo"]["angulo"] = puertaNueva["Servo"]["angulo"]
                fn.escribir(archHaciaRaspi, PuertaBBDD)
		fn.log.debug("Grabado en archivo: archHaciaRaspi")
	else:
		fn.log.debug("Archivo no Grabado: archHaciaRaspi")

def impactarCambiosPuertaRasp(puertaNueva):
	global PuertaRaspi,PuertaBBDD,puertaDesdeRaspi,puertaHaciaRaspi
        if not(PuertaRaspi["Led"]["estado"] == puertaNueva["Led"]["estado"] and
               PuertaRaspi["Presencia"]["estado"] == puertaNueva["Presencia"]["estado"] and
               PuertaRaspi["Servo"]["angulo"] == puertaNueva["Servo"]["angulo"] and
               PuertaRaspi["Servo"]["esfuerzo"] == puertaNueva["Servo"]["esfuerzo"]):
		puerta = impactarPuerta(puertaDesdeRaspi, puertaNueva)    #actualiza/graba puerta Raspi
		if puerta==None:
			fn.log.warning("No va puerta Raspi")
		else:
			PuertaRaspi["Led"]["estado"] = puertaNueva["Led"]["estado"]
                	PuertaRaspi["Presencia"]["estado"] = puertaNueva["Presencia"]["estado"]
        	        PuertaRaspi["Servo"]["angulo"] = puertaNueva["Servo"]["angulo"]
	                PuertaRaspi["Servo"]["esfuerzo"] = puertaNueva["Servo"]["esfuerzo"]

			puerta = impactarPuerta(puertaHaciaRaspi, puertaNueva)    #actualiza/graba puerta App
			if puerta==None:
				fn.log.warning("No va puerta App")
#			else:
#                		PuertaBBDD["Led"]["estado"] = puertaNueva["Led"]["estado"]
#		         	PuertaBBDD["Presencia"]["estado"] = puertaNueva["Presencia"]["estado"]
#	        	        PuertaBBDD["Servo"]["angulo"] = puertaNueva["Servo"]["angulo"]
#		                PuertaBBDD["Servo"]["esfuerzo"] = puertaNueva["Servo"]["esfuerzo"]


##objeto=None
##objeto=json.loads('{"name" : "fernando", "age":28}')


try:
	while True:
		#fn.log.debug(datetime.datetime.now())

		#intentos=0
		#while intentos<10:
		#	intentos+=1
			#objeto["age"]=intentos

		# Grabar en archivo puertaHaciaRaspi: PuertaLecAppEscRas #
		puerta = obtenerPuerta(puertaHaciaRaspi)
		if puerta!=None:
			#fn.log.debug("puerta app: "+puerta["Presencia"]["estado"])
			#fn.log.debug("puerta app:\n"+json.dumps(puerta, cls=jsonutil.JSONEncoder))
			escribirCambiosPuertaApp(puerta)
		else:
			fn.log.warning("no vino puerta app")

		# Leer de archivo puertaDesdeRaspi: PuertaEscAppLecRas #
		puerta = fn.leer(archDesdeRaspi)
		if puerta!=None and puerta!="":
			impactarCambiosPuertaRasp(puerta)
			#fn.log.debug("Leido en Archivo: archDesdeRaspi")
			#fn.log.debug("Leido en Archivo:",archDesdeRaspi,json.dumps(puerta, cls=jsonutil.JSONEncoder))
		else:
			fn.log.warning("Archivo no Leido: archDesdeRaspi")
	#       sleep(5)
			
		#	fn.log.debug(datetime.datetime.now())
except (KeyboardInterrupt, SystemExit):
	fn.log.warning('Programa detenido')
	fn.log.info('Ha Presionado Ctrl+C, saliendo')
except Exception as e:
	if hasattr(e, 'message'):
		fn.log.error(e.message)
	else:
		fn.log.error(e)
	# otro error
else:
	fn.log.debug('Sin error')
	# sin error
finally:
	fn.log.info('...............')
