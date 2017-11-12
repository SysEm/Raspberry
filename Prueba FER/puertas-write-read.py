import datetime
from time import sleep

import json
from firebase import jsonutil
from firebase.firebase import FirebaseApplication, FirebaseAuthentication
import os


###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	print('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

base_dir = os.path.dirname(os.path.abspath(__file__)) #<-- absolute dir del script
def abs_path(rel_path):
    return os.path.join(base_dir, rel_path)

# Lee en forma segura un archivo (comprueba si no existe el archivo)
# return: objeto 'dict' con el json del archivo, None en otro caso
def leer(path):
    if os.path.exists(path):
        arch=open(path,"r+")
        arch=arch.read()
        if arch!="":
            return json.loads(arch)
    return None

# Guarda un objeto serializable en un archivo (crea si no existe, pisa contenido)
# return: string de objeto serializado guardado en archivo, None en otro caso
def escribir(path,json_obj):
    try:
        jobj=json.dumps(json_obj, cls=jsonutil.JSONEncoder)
    except TypeError:
        jobj=None
    if jobj!="" and jobj!=None:
        with open(path,"w+") as arch:
            arch.write(jobj)
    return jobj

# CONFIGURACION #
puertaDesdeRaspi="PuertaLecAppEscRas"
puertaHaciaRaspi="PuertaEscAppLecRas"
DSN = 'https://soatp-2dfc9.firebaseio.com'

##objeto=None
##objeto=json.loads('{"name" : "fernando", "age":28}')

archDesdeRaspi=abs_path(puertaDesdeRaspi+".json")
archHaciaRaspi=abs_path(puertaHaciaRaspi+".json")
firebase = FirebaseApplication(DSN, None)

while True:
    print(datetime.datetime.now())

    intentos=0
    while intentos<10:
        intentos+=1
        #objeto["age"]=intentos

        # Grabar en archivo puertaHaciaRaspi: PuertaLecAppEscRas #
        puerta = firebase.get('/baseDatosSoa', puertaHaciaRaspi,
                              params={'print': 'pretty'},
                              headers={'X_FANCY_HEADER': 'very fancy'})
        if puerta!=None:
            print("puerta app: ",puerta["Presencia"]["estado"])
            #print("puerta app:\n",json.dumps(puerta, cls=jsonutil.JSONEncoder))
            puerta=escribir(archHaciaRaspi,puerta)
            if puerta!=None:
                print("Grabado en archivo: archHaciaRaspi")
                #print("Grabado en archivo:",archHaciaRaspi," Puerta:",puerta)
            else:
                print("Archivo no Grabado: archHaciaRaspi")
                #print("Archivo no Grabado:",archHaciaRaspi," Puerta:",puerta)
        else:
            print("no vino puerta app")

        # Leer de archivo puertaDesdeRaspi: PuertaEscAppLecRas #
        puerta=leer(archDesdeRaspi)
        if puerta!=None and puerta!="":
            print("Leido en Archivo: archDesdeRaspi")
            #print("Leido en Archivo:",archDesdeRaspi,json.dumps(puerta, cls=jsonutil.JSONEncoder))
            puerta = firebase.put('/baseDatosSoa', puertaDesdeRaspi, puerta)    #actualiza/graba puerta
            if puerta==None:
                print("no va puerta Raspi")
        else:
            print("Archivo no Leido: archDesdeRaspi")
#       sleep(5)
        
        print(datetime.datetime.now())
