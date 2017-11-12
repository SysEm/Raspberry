import datetime
from time import sleep


#import json
#from firebase import jsonutil
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
import pyrebase

import puertasfunciones as fn


#libreria Pyrebase= https://github.com/ozgur/python-firebase
#libreria Python-Firebase= https://soatp-2dfc9.firebaseio.com/baseDatosSoa/puertas/Puerta 


###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	print('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

#Recupera/consulta puerta en Firebase
def obtenerPuerta(idpuerta):
	return firebase.get('/baseDatosSoa', idpuerta,
				params={'print': 'pretty'},
				headers={'X_FANCY_HEADER': 'very fancy'})

#Actualiza/graba puerta en Firebase
def impactarPuerta(idpuerta,dato):
	return firebase.put('/baseDatosSoa', idpuerta, dato)

########### VARIABLES GLOBALES ############


###########  CONFIGURACIONES   ############
# Info Base de Datos Firebase
puertaDesdeRaspi="PuertaLecAppEscRas"
puertaHaciaRaspi="PuertaEscAppLecRas"
DSN = 'https://soatp-2dfc9.firebaseio.com'
archDesdeRaspi=fn.abs_path(puertaDesdeRaspi+".json")
archHaciaRaspi=fn.abs_path(puertaHaciaRaspi+".json")
firebase = FirebaseApplication(DSN, None)

'''
def firebase_(puerta_, estado_): 
    if (estado_ == "False"):
        db.child("baseDatosSoa/puertas/"+puerta_+"/led").update({"estado": ("True" if estado_=="False" else "True")})
    elif (estado_ == "True"):
        db.child("baseDatosSoa/puertas/"+puerta_+"/led").update({"estado": ("False" if estado_=="True" else "False")}) 

config = {
  "apiKey": "AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA",
  "authDomain": "soatp-2dfc9.firebaseapp.com",
  "databaseURL": "https://soatp-2dfc9.firebaseio.com",
  "storageBucket": "soatp-2dfc9.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
'''

##objeto=None
##objeto=json.loads('{"name" : "fernando", "age":28}')


try:
	while True:
		fn.log.debug(datetime.datetime.now())

		intentos=0
		while intentos<10:
			intentos+=1
			#objeto["age"]=intentos

			# Grabar en archivo puertaHaciaRaspi: PuertaLecAppEscRas #
			puerta = obtenerPuerta(puertaHaciaRaspi)
			if puerta!=None:
				fn.log.debug("puerta app: "+puerta["Presencia"]["estado"])
				#fn.log.debug("puerta app:\n",json.dumps(puerta, cls=jsonutil.JSONEncoder))
				puerta=fn.escribir(archHaciaRaspi,puerta)
				if puerta!=None:
					fn.log.debug("Grabado en archivo: archHaciaRaspi")
					#fn.log.debug("Grabado en archivo:",archHaciaRaspi," Puerta:",puerta)
				else:
					fn.log.debug("Archivo no Grabado: archHaciaRaspi")
					#fn.log.warning("Archivo no Grabado:",archHaciaRaspi," Puerta:",puerta)
			else:
				fn.log.warning("no vino puerta app")

			# Leer de archivo puertaDesdeRaspi: PuertaEscAppLecRas #
			puerta=fn.leer(archDesdeRaspi)
			if puerta!=None and puerta!="":
				fn.log.debug("Leido en Archivo: archDesdeRaspi")
				#fn.log.debug("Leido en Archivo:",archDesdeRaspi,json.dumps(puerta, cls=jsonutil.JSONEncoder))
				puerta = impactarPuerta(puertaDesdeRaspi, puerta)    #actualiza/graba puerta
				if puerta==None:
					fn.log.warning("No va puerta Raspi")
			else:
				fn.log.warning("Archivo no Leido: archDesdeRaspi")
	#       sleep(5)
			
			fn.log.debug(datetime.datetime.now())
except (KeyboardInterrupt, SystemExit):
	fn.log.warning('Programa detenido')
	fn.log.info('Ha Presionado Ctrl+C, saliendo')
except:
	fn.log.error('Error')
	# otro error
else:
	fn.log.debug('Sin error')
	# sin error
finally:
	fn.log.info('...............')