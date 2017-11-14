import RPi.GPIO as GPIO
import time
import serial
import signal
import sys
#import os

import puertasfunciones as fn
###########  CONFIGURACIONES   ############
#Patas GPIO usadas
GPIO_LED_ROJO = 16
GPIO_LED_VERDE = 20
GPIO_MICROFONO = 25
GPIO_LED_AMARILLO = 21
GPIO_LED_BLANCO = 6
GPIO_LED_PRESENCIA = GPIO_LED_BLANCO
GPIO_INFRARROJO = 26
GPIO_PULSADOR = 24


########### VARIABLES GLOBALES ############
#listas, contiene el password por default de golpes inicial y el que ingreses al intentar abrir la puerta
password = [1,1,1,1,1] #hardcodeada (siempre comenzar en 1)
ingresado = []
cantGolpes = 5 #seteo de numeros de golpes/silencios que se ingresaran como password
cantSegm = 0
count = 0
# Archivos comunicacion a BBDD
puertaDesdeRaspi="PuertaLecAppEscRas"
puertaHaciaRaspi="PuertaEscAppLecRas"
archDesdeRaspi=fn.abs_path(puertaDesdeRaspi+".json")
archHaciaRaspi=fn.abs_path(puertaHaciaRaspi+".json")

# Estados Arduino
estArduino = ""
ARD_FORZADO = "FORZADO"
ARD_ESTACIONARIO = "ESTACIONARIO"

# Estados Puerta
PU_CERR_BLOQUEADA = 1
PU_CERR_DESBLOQUEANDO = 2
PU_MOV_ABRIENDO = 11
PU_ABRT_ABIERTA = 12
PU_ABRT_SINPRESENCIA = 13
PU_MOV_CERRANDO = 14
estPuerta = PU_CERR_BLOQUEADA

# Estados Infrarrojo
IR_NOPRESENCIA = 0
IR_SENSANDO = 1
IR_HAYPRESENCIA = 2
estInfra = IR_NOPRESENCIA
IR_SEN_SI = 0
IR_SEN_NO = 1

# Estados Forzado
FZ_NOFORZADO = 0
FZ_DETECTANDO = 1
FZ_FORZADO = 2
estForzado = FZ_NOFORZADO

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

# ID LUCES
LUZ_BLANCA = 0
LUZ_ROJA = 1
LUZ_VERDE = 2
LUZ_AMARILLA = 3

estLuz = [False,False,False,False] #Estado actual de cada Luz

# Tiempos y Deadlines: Usados para corte de control
tieLuzOn = [1,1,1,1] #Tiempo final de cada luz encendida
dlLedPuertaAbierta = 1 #Deadline Led - Reflector con puerta abierta - queda On al cerrar
dlLedPresencia = 2 #Deadline Led - Reflector con presencia - queda On al perder presencia
dlLedGolpeSensado = 0.2 #Deadline Led - Verde al sensar Golpe / Silencio en Segmento de Tiempo
dlLedPassMal = 2 #Deadline Led - Rojo al ingresar contrasena incorrecta
dlLedPassOk = 1 #Deadline Led - Verde al ingresar contrasena correcta

dlLedApp = 10 #Deadline Led - Reflector con Orden de App

ya = time.time()
tieMicroSegm = ya
dlMicroSegm = 1.5 #tiempo de escucha por cada golpe para detectar un golpe o no
tiePuerta2 = ya
tiePuerta3 = ya
tiePuerta12 = ya
tiePulsador = ya
tieLeerBBDD = ya
dlLeerBBDD = 0.6
dlPulsadorDEBOUNCE = 0.3
dlPuertaMovimiento = 0.02
dlPuertaAbierta = 4
dlPresencia = 1.2
dlDesbloqueo = 6

###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	global arduino
	fn.log.warning('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

def playDingDong(): #Reproduce audio "ding-dong.mp3" en el mismo path
	os.system('mpg321 -q ding-dong.mp3 &')

def pinIdLuz(idluz):
	if idluz == LUZ_BLANCA: return GPIO_LED_BLANCO
	elif idluz == LUZ_ROJA: return GPIO_LED_ROJO
	elif idluz == LUZ_VERDE: return GPIO_LED_VERDE
	elif idluz == LUZ_AMARILLA: return GPIO_LED_AMARILLO

def encenderLuz(idluz,tiempo):
	global ya,estLuz,tieLuzOn
	if estLuz[idluz] == False:
		estLuz[idluz] = True
		GPIO.output(pinIdLuz(idluz),True)
        # solo pisar tiempo si supera al actual, sino, mantener el mayor
	if tieLuzOn[idluz] < (ya + tiempo):
		tieLuzOn[idluz] = ya + tiempo

def apagarLuz(idluz):
	global estLuz
	estLuz[idluz] = False
	GPIO.output(pinIdLuz(idluz),False)

def mantenerLuz(idluz):
	global ya,estLuz,tieLuzOn
	if estLuz[idluz] == True and ya > tieLuzOn[idluz]:
		estLuz[idluz] = False
		GPIO.output(pinIdLuz(idluz),False)

def abrirPuerta():
	global arduino,estPuerta
	arduino.write('A')	#Abrir puerta
	estPuerta = PU_MOV_ABRIENDO #Puerta abriendo

def cerrarPuerta():
	global arduino,estPuerta,tiePuerta14
	arduino.write('A')	#Cerrar puerta
	estPuerta = PU_MOV_CERRANDO #Puerta cerrando
	tiePuerta14 = ya

def impactarCambiosPuerta(obligado,luz,presencia,puerta,forzado):
	global PuertaRaspi
	fbLuz = (P_LED_EST_ON if luz else P_LED_EST_OFF)
	fbPresencia = (P_PRES_EST_ON if presencia else P_PRES_EST_OFF)
	fbPuerta = (P_SERV_ANG_ABIERTO if puerta else P_SERV_ANG_CERRADO)
	fbForzado = (P_SERV_ESFUERZO_SI if forzado else P_SERV_ESFUERZO_NO)

	if not(fbLuz == PuertaRaspi["Led"]["estado"] and
			fbPresencia == PuertaRaspi["Presencia"]["estado"] and
			fbPuerta == PuertaRaspi["Servo"]["angulo"] and
			fbForzado == PuertaRaspi["Servo"]["esfuerzo"]):
		PuertaRaspi["Led"]["estado"] = fbLuz
		PuertaRaspi["Presencia"]["estado"] = fbPresencia
		PuertaRaspi["Servo"]["angulo"] = fbPuerta
		PuertaRaspi["Servo"]["esfuerzo"] = fbForzado
		fn.escribir(archDesdeRaspi, PuertaRaspi)
	elif obligado:
		fn.escribir(archDesdeRaspi, PuertaRaspi)

def leerPuertaBBDD():
	global PuertaBBDD,tieLeerBBDD,estPuerta,arduino
	tieLeerBBDD = ya
	PuertaBBDD = fn.leer(archHaciaRaspi)

	if PuertaBBDD!=None and PuertaBBDD!="":
		fn.log.debug("Leido en Archivo: archHaciaRaspi")
		#fn.log.debug("Leido en Archivo:"+archHaciaRaspi+json.dumps(puerta, cls=jsonutil.JSONEncoder))
		#Encendido de Luz : Mandatorio
		fn.log.debug("APP : Led : " + PuertaBBDD["Led"]["estado"])
		if PuertaBBDD["Led"]["estado"] == P_LED_EST_ON:
			encenderLuz(LUZ_BLANCA,dlLedApp)
		elif PuertaBBDD["Led"]["estado"] == P_LED_EST_OFF:
			apagarLuz(LUZ_BLANCA)
		#Apertura de Puerta : Segun estPuerta
		fn.log.debug("APP : Puerta : " + PuertaBBDD["Servo"]["angulo"])
		if PuertaBBDD["Servo"]["angulo"] == P_SERV_ANG_ABIERTO and estPuerta in [PU_ABRT_ABIERTA,PU_ABRT_SINPRESENCIA]:
			cerrarPuerta()
		elif PuertaBBDD["Servo"]["angulo"] == P_SERV_ANG_CERRADO and estPuerta < PU_MOV_ABRIENDO:
			abrirPuerta()
	else:
		fn.log.warning("Archivo no Leido: archDesdeRaspi")


try:
	# Setup / Configuracion de GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(GPIO_INFRARROJO, GPIO.IN) ## entrada
	GPIO.setup(GPIO_LED_PRESENCIA, GPIO.OUT) ## salida
	GPIO.setup(GPIO_MICROFONO, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## entrada
	GPIO.setup(GPIO_LED_ROJO, GPIO.OUT) ## salida
	GPIO.setup(GPIO_LED_VERDE, GPIO.OUT) ## salida
	GPIO.setup(GPIO_LED_AMARILLO, GPIO.OUT) ## salida
	GPIO.setup(GPIO_LED_BLANCO, GPIO.OUT) ## salida
	GPIO.setup(GPIO_PULSADOR, GPIO.IN) ## entrada

	#Objeto arduino linkeado al puerto serie
	arduino = serial.Serial('/dev/ttyACM0', 9600)

	#Actualizar BBDD
	impactarCambiosPuerta(True, False,False,False,False)
	fn.log.info("Por favor, setee la secuencia de golpes")
	fn.log.info("La cantidad de golpes son " + str(cantGolpes))
	fn.log.info("Cada vez que se prende el led rojo, se espera o no un golpe")


#GENERACION DE CODIGO DE GOLPES#

#	cantSegm = 0
#	while cantSegm < cantGolpes:
#		senMicroSegm = 0
#		tieMicroSegm = time.time()
#
#		#se prende el led indicando que espera un golpe
#		encenderLuz(LUZ_AMARILLA,dlLedGolpeSensado)
#
#		#bucle de escucha de un golpe.. en el tiempo indicado que dura un golpe
#		while time.time() < tieMicroSegm + dlMicroSegm:
#			if GPIO.input(GPIO_MICROFONO):
#				#prende el led verde indicando que se esucho un golpe
#				encenderLuz(LUZ_VERDE,dlLedGolpeSensado)
#				senMicroSegm = 1
#			else:
#				apagarLuz(LUZ_VERDE)
#		cantSegm = cantSegm + 1
#
#		#se termina de escuchar un golpe, y se guarda el resultado en la lista
#		apagarLuz(LUZ_ROJA)
#		time.sleep(1)
#		fn.log.debug(str(senMicroSegm)+",")
#no guardar password		password.append(senMicroSegm)



#	fn.log.info("Por favor, ingrese la contrasena")
	fn.log.info("La cantidad de golpes/silencios son "+ str(cantGolpes))
	fn.log.info("Cada vez que se prende el led AMARILLO, se espera un golpe/silencio")

	# APAGA TODAS LAS LUCES
	apagarLuz(LUZ_BLANCA)
	apagarLuz(LUZ_ROJA)
	apagarLuz(LUZ_VERDE)
	apagarLuz(LUZ_AMARILLA)

	fn.log.info("Inicializando escucha. Con Ctrl+C sale del programa")
	estArduino = arduino.readline()
	fn.log.debug("Estado de la puerta: " + str(estArduino))


	######### COMIENZA BUCLE INFINITO ##########
	while True:
		ya = time.time()

		# DEFINIR CAMBIOS DE ESTADO DE PUERTA POR DEADLINE
		senInfra = GPIO.input(GPIO_INFRARROJO) #LEO EL SENSOR INFRARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
		senPulsador = GPIO.input(GPIO_PULSADOR)
		if estPuerta == PU_MOV_ABRIENDO and ya > (tiePuerta12 + dlPuertaMovimiento) :
			estPuerta = PU_ABRT_ABIERTA
			tiePuerta12 = ya
		if estPuerta > PU_MOV_ABRIENDO and estPuerta < PU_MOV_CERRANDO:
			encenderLuz(LUZ_BLANCA, dlLedPuertaAbierta) # encender luz mientras este abierta
			if estInfra == IR_HAYPRESENCIA:
				tiePuerta12 = ya
				estPuerta = PU_ABRT_ABIERTA #abierta con presencia
			elif ya < (tiePuerta12 + dlPuertaAbierta):
				estPuerta = PU_ABRT_SINPRESENCIA #abierta sin presencia
			elif ya < (tiePuerta12 + dlPuertaAbierta + dlPuertaMovimiento):
				cerrarPuerta()
				#estPuerta = PU_MOV_CERRANDO #cerrando
				#tiePuerta14 = ya
				#arduino.write('A')	#Abrir puerta
		elif estPuerta == PU_MOV_CERRANDO and ya > (tiePuerta14 + dlPuertaMovimiento):
				estPuerta = PU_CERR_BLOQUEADA #cerrada y bloqueada
		elif estPuerta < PU_MOV_ABRIENDO:
			if estPuerta == PU_CERR_DESBLOQUEANDO and(ya > tiePuerta2 + dlDesbloqueo): #desbloqueando Y tiempo de debloqueo excedido
				estPuerta = PU_CERR_BLOQUEADA

		fn.log.debug("estPuerta:"+str(estPuerta)+" - estInfra:"+str(estInfra)+" - estForzado:"+str(estForzado) )
		## Encendido de Leds
		if ya > tieLeerBBDD + dlLeerBBDD:	#Lee archivo cada dlLeerBBDD TIEMPO
			leerPuertaBBDD()
		if estPuerta == PU_CERR_BLOQUEADA: encenderLuz(LUZ_AMARILLA, GPIO_LED_AMARILLO)
		mantenerLuz(LUZ_BLANCA)
		mantenerLuz(LUZ_ROJA)
		mantenerLuz(LUZ_VERDE)
		mantenerLuz(LUZ_AMARILLA)

		######## Sensado de INFRARROJO / PRESENCIA #######
		if senInfra == IR_SEN_SI:
			if estInfra == IR_NOPRESENCIA:
				fn.log.debug("Se comenzo a detectar algo")
				estInfra = IR_SENSANDO
				tieInfra1 = ya
			elif estInfra == IR_SENSANDO and (ya > tieInfra1 + dlPresencia): # HAY ALGO
				estInfra = IR_HAYPRESENCIA
				fn.log.debug("Hay algo")
				encenderLuz(LUZ_BLANCA, dlLedPresencia)

				#fn.log.debug("Detect: ON - LED EN BDD EN FIREBASE: ON ")
				#if (salidaLed.val() == "False"):
				#	firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE
		elif senInfra == IR_SEN_NO:
			if estInfra == IR_SENSANDO:
				estInfra == IR_NOPRESENCIA #Falsa Presencia
				fn.log.debug("Falsa presencia")
			elif estInfra == IR_HAYPRESENCIA:
				estInfra = IR_NOPRESENCIA
				fn.log.debug("Detectada No presencia")

		######## Sensado de GOLPES #######
		if estPuerta in [PU_CERR_BLOQUEADA,PU_CERR_DESBLOQUEANDO] and estInfra == IR_HAYPRESENCIA: #Puerta cerrada Y Presencia Detectada
			if estPuerta == PU_CERR_BLOQUEADA or (ya < tieMicroSegm + dlMicroSegm and senMicroSegm == 0):	#sensando si hay GOLPE/NO-GOLPE en 1 Vez
				senMicro = GPIO.input(GPIO_MICROFONO)
				fn.log.debug("Micro:"+str(senMicro))
				if senMicro == 1:
					# PRIMER GOLPE SENSADO
					if estPuerta == PU_CERR_BLOQUEADA:
						tiePuerta2 = ya
						estPuerta = PU_CERR_DESBLOQUEANDO # Puerta cerrada Desbloqueando
						apagarLuz(LUZ_AMARILLA)
						golpes = 0
						del ingresado[:]
					encenderLuz(LUZ_VERDE,dlLedGolpeSensado)
					senMicroSegm = 1
					cantSegm += 1
					golpes += 1
					ingresado.append(senMicroSegm)
			elif estPuerta == PU_CERR_DESBLOQUEANDO:
				cantSegm += 1
				ingresado.append(senMicroSegm)
				# Prepara proximo segmento
				tieMicroSegm = ya
				senMicroSegm = 0
				#se prende el led indicando que espera un golpe
				encenderLuz(LUZ_AMARILLA,dlLedGolpeSensado)
				fn.log.debug(str(senMicroSegm)+",")

			if cantSegm == cantGolpes:
				#una vez que tiene los golpes ingresados para abrir la puerta, la compara con el pass seteado al principio    
				coincide = 1
				#si no coinciden , cambia la marca de coinciden a 0 y advierte de secuencia incorrecta con el led rojo, de lo contrario con el verde
				for i in range(cantGolpes - 1):
					fn.log.debug(str(cantGolpes) + " ... i:" + str(i))
					if (password[i] != ingresado[i]):
						coincide = 0
						break
					else:
						fn.log.debug("el elemento "+str(i)+" coinciden")

				if(coincide == 0):
					estPuerta = PU_CERR_BLOQUEADA #Puerta Bloqueada
					GPIO.output(GPIO_LED_ROJO,True)
					encenderLuz(LUZ_ROJA,dlLedPassMal)
					fn.log.warning("Secuencia incorrecta!!! alerta policia")
				else:
					abrirPuerta()
					#estPuerta = PU_MOV_ABRIENDO #Puerta abriendo
					#arduino.write('A')	#Abrir puerta
					encenderLuz(LUZ_VERDE,dlLedPassOk)
					fn.log.info("Puerta desbloqueada, por favor, ingrese")
					fn.log.debug("Enviada orden a Arduino")
				cantSegm = 0

		####### Sensado de PULSADOR #######
		if senPulsador == True and ya > tiePulsador + dlPulsadorDEBOUNCE:
			fn.log.debug("Pulsador TRUE:"+str(estPuerta))
			tiePulsador = ya
			if estPuerta in [PU_ABRT_ABIERTA,PU_ABRT_SINPRESENCIA]:
				cerrarPuerta()
				#arduino.write('A')	#Cerrar puerta
				#estPuerta = PU_MOV_CERRANDO #Puerta cerrando
				#tiePuerta14 = ya
			elif estPuerta < PU_MOV_ABRIENDO:
				abrirPuerta()
				#arduino.write('A')
				#estPuerta = PU_MOV_ABRIENDO #Puerta abriendo

				count = count + 1
				fn.log.debug("Boton presionado " + str(count) + " veces.")
				##estArduino = arduino.readline()
				##time.sleep(.02) #PERIODO DE ACCION DEL SERVO: 20 ms.

		####### Sensado de SERVO / FORZADO ########
		estArduino = arduino.readline()
		#fn.log.debug(estArduino)
		if estPuerta in [PU_CERR_BLOQUEADA,PU_CERR_DESBLOQUEANDO,PU_ABRT_ABIERTA,PU_ABRT_SINPRESENCIA]:
			fn.log.debug("Arduino:"+str(estArduino))
			if estArduino == "FORZADO":
				if estPuerta in [PU_CERR_BLOQUEADA,PU_CERR_DESBLOQUEANDO]: #ATENCION: Alertaria durante los golpes
					if estForzado == FZ_NOFORZADO:
						estForzado = FZ_DETECTANDO
						tieForzado = ya
					elif estForzado == FZ_DETECTANDO and ya > tieForzado + dlForzado:
						estForzado = FZ_FORZADO
						fn.log.warning("PUERTA FORZADA")
						#NOTIFICAR A BBDD
			elif estForzado == FZ_DETECTANDO and ya > tieForzado + dlForzado:
				#Para volver a NO FORZADO, espera que pase el tieForzado+dlForzado, ya que durante el mismo
				#puede llegar la senal ESTACIONARIO pero siendo simplemente un ruido. Puede fallar? dificil
				estForzado = FZ_NOFORZADO 

		####### Comprobacion Cambios en PUERTA #######
		impactarCambiosPuerta(False,
							(estLuz[LUZ_BLANCA]),
							(estInfra == IR_HAYPRESENCIA),
							(estPuerta in [PU_ABRT_ABIERTA,PU_ABRT_SINPRESENCIA]),
							(estPuerta in [PU_CERR_DESBLOQUEANDO,PU_CERR_BLOQUEADA] and estForzado == FZ_FORZADO))


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
	arduino.close()
	time.sleep(2) # permitir visibilidad de ultimo estado de leds antes de Cleanup
	GPIO.cleanup()
	sys.exit(0)
