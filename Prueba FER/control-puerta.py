import RPi.GPIO as GPIO
import time
import serial
import signal
import sys
#import os

import puertasfunciones as fn
###########  CONFIGURACIONES   ############
#Mensajes salientes
mout=0
#Patas GPIO usadas
GPIO_LED_ROJO = 16
GPIO_LED_VERDE = 20
GPIO_MICROFONO = 25
GPIO_LED_AMARILLO = 21
GPIO_LED_BLANCO = 6
GPIO_LED_PRESENCIA = GPIO_LED_BLANCO
GPIO_INFRARROJO = 26
GPIO_PULSADOR = 24

cantidadGolpes = 5 #seteo de numeros de golpes que se ingresaran como password

########### VARIABLES GLOBALES ############
#listas, contiene el password por default de golpes inicial y el que ingreses al intentar abrir la puerta
password = [1,1,1,1,1]
ingresado = []
cantSegm = 0
count = 0
# Archivos comunicacion a BBDD
puertaDesdeRaspi="PuertaLecAppEscRas"
puertaHaciaRaspi="PuertaEscAppLecRas"
archDesdeRaspi=fn.abs_path(puertaDesdeRaspi+".json")
archHaciaRaspi=fn.abs_path(puertaHaciaRaspi+".json")



P_LED_EST_ON = "on"
P_LED_EST_OFF = "off"
P_PRES_EST_ON = "on"
P_PRES_EST_OFF = "off"
P_SERV_ANG_ABIERTO = 1
P_SERV_ANG_CERRADO = 0
P_SERV_ESFUERZO_SI = 1
P_SERV_ESFUERZO_NO = 0
PuertaRaspi = {"Led": {"estado": P_LED_EST_OFF}, "Presencia": {"estado": P_PRES_EST_OFF}, "Servo": {"angulo": P_SERV_ANG_CERRADO, "esfuerzo": P_SERV_ESFUERZO_NO}}


LUZ_BLANCA = 0
LUZ_ROJA = 1
LUZ_VERDE = 2
LUZ_AMARILLA = 3
dlLuz = [1,1,1,1]
dlEstadoLuz = [False,False,False,False]
dlLedPuertaAbierta = 5
dlLedPresencia = 2
dlLedGolpeSensado = 0.2
dlLedPassMal = 2
dlLedPassOk = 1
dlLuzPulsadorError = 0.5
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
	global ya,dlEstadoLuz,dlLuz
	if dlEstadoLuz[idluz] == False:
		dlEstadoLuz[idluz] = True
		GPIO.output(pinIdLuz(idluz),True)
	dlLuz[idluz] = ya + tiempo

def apagarLuz(idluz):
        global dlEstadoLuz
	dlEstadoLuz[idluz] = False
	GPIO.output(pinIdLuz(idluz),False)

def mantenerLuz(idluz):
	global ya,dlEstadoLuz,dlLuz
	if dlEstadoLuz[idluz] == True and ya > dlLuz[idluz]:
		dlEstadoLuz[idluz] = False
		GPIO.output(pinIdLuz(idluz),False)

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
	global PuertaBBDD
	PuertaBBDD = fn.leer(archHaciaRaspi)
	# fbLuz = (P_LED_EST_ON if luz else P_LED_EST_OFF)
	# fbPresencia = (P_PRES_EST_ON if presencia else P_PRES_EST_OFF)
	# fbPuerta = (P_SERV_ANG_ABIERTO if puerta else P_SERV_ANG_CERRADO)
	# fbForzado = (P_SERV_ESFUERZO_SI if forzado else P_SERV_ESFUERZO_NO)

	# if not(fbLuz == PuertaRaspi["Led"]["estado"] and 
			# fbPresencia == PuertaRaspi["Presencia"]["estado"] and
			# fbPuerta == PuertaRaspi["Servo"]["angulo"] and
			# fbForzado == PuertaRaspi["Servo"]["esfuerzo"]):
		# PuertaBBDD["Led"]["estado"] = fbLuz
		# PuertaBBDD["Presencia"]["estado"] = fbPresencia
		# PuertaBBDD["Servo"]["angulo"] = fbPuerta
		# PuertaBBDD["Servo"]["esfuerzo"] = fbForzado

# Estados y Deadlines: Usados para corte de control
ya = time.time()
estado = ""
estPuerta = 1 
estInfra = 0
estForzado = 0
tieMicroSegm = ya
dlMicroSegm = 1.5 #tiempo de escucha por cada golpe para detectar un golpe o no
tiePuerta2 = ya
tiePuerta3 = ya
tiePuerta12 = ya
tiePulsador = ya
tieLeerBBDD = ya
dlLeerBBDD = 1.8
dlPulsadorDEBOUNCE = 0.3
dlPuertaMovimiento = 0.02
dlPuertaAbierta = 4
dlPresencia = 1.2
dlDesbloqueo = 6

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
	fn.log.info("La cantidad de golpes son " + str(cantidadGolpes))
	fn.log.info("Cada vez que se prende el led rojo, se espera o no un golpe")
	if mout > 0:
		time.sleep(2)

#GENERACION DE CODIGO DE GOLPES#

#	cantSegm = 0
#	while cantSegm < cantidadGolpes:
#		senMicroSegm = 0
#                tieMicroSegm = time.time()
#
#		#se prende el led indicando que espera un golpe
#		GPIO.output(GPIO_LED_ROJO,True)
#
#		#bucle de escucha de un golpe.. en el tiempo indicado que dura un golpe
#		while time.time() < tieMicroSegm + dlMicroSegm:
#			if GPIO.input(GPIO_MICROFONO):
#				#prende el led verde indicando que se esucho un golpe
#				GPIO.output(GPIO_LED_VERDE,True)
#				senMicroSegm = 1
#			else:
#				GPIO.output(GPIO_LED_VERDE,False)
#		cantSegm = cantSegm + 1
#
#		#se termina de escuchar un golpe, y se guarda el resultado en la lista
#		GPIO.output(GPIO_LED_ROJO,False)
#		time.sleep(1)
#		fn.log.debug(str(senMicroSegm)+",")
#no guardar password		password.append(senMicroSegm)



#	fn.log.info("Por favor, Ingrese la contrasena")
	fn.log.info("La cantidad de golpes son "+ str(cantidadGolpes))
	fn.log.info("Cada vez que se prende el led amarillo, se espera o no un golpe")

	time.sleep(1)

	# APAGA AMBAS LUCES
	GPIO.output(GPIO_LED_ROJO,False)
	GPIO.output(GPIO_LED_VERDE,False)
	#time.sleep(2)

        fn.log.info("Inicializando escucha. Con Ctrl+C sale del programa")
	estado = arduino.readline()
        fn.log.debug("Estado de la puerta: " + str(estado))
	if mout>0: time.sleep(2)

	######### COMIENZA BUCLE INFINITO ##########
	while True:
		ya = time.time()

		# DEFINIR CAMBIOS DE ESTADO DE PUERTA POR DEADLINE
		senInfra = GPIO.input(GPIO_INFRARROJO) #LEO EL SENSOR INFRARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
		senPulsador = GPIO.input(GPIO_PULSADOR)
		if ya > tieLeerBBDD + dlLeerBBDD:	#Lee archivo cada dlLeerBBDD TIEMPO
			leerPuertaBBDD()
		if estPuerta == 11 and ya > (tiePuerta12 + dlPuertaMovimiento) :
			estPuerta = 12
                        tiePuerta12 = ya
		if estPuerta > 11 and estPuerta < 14:
			encenderLuz(LUZ_BLANCA, dlLedPuertaAbierta) # encender luz mientras este abierta
			if estInfra == 2:
				tiePuerta12 = ya
				estPuerta = 12 #abierta con presencia
			elif ya < (tiePuerta12 + dlPuertaAbierta):
				estPuerta = 13 #abierta sin presencia
			elif ya < (tiePuerta12 + dlPuertaAbierta + dlPuertaMovimiento):
				estPuerta = 14 #cerrando
                                tiePuerta14 = ya
                                arduino.write('A')	#Abrir puerta
		elif estPuerta == 14 and ya > (tiePuerta14 + dlPuertaMovimiento):
				estPuerta = 1 #cerrada y bloqueada
		elif estPuerta < 11:
			if estPuerta == 2 and(ya > tiePuerta2 + dlDesbloqueo): #desbloqueando Y tiempo de debloqueo excedido
				estPuerta = 1

                fn.log.debug("estPuerta:"+str(estPuerta)+" - estInfra:"+str(estInfra)+" - estForzado:"+str(estForzado) )
		## Encendido de Leds
		if estPuerta == 1: encenderLuz(LUZ_AMARILLA, GPIO_LED_AMARILLO)
		mantenerLuz(LUZ_BLANCA)
		mantenerLuz(LUZ_ROJA)
		mantenerLuz(LUZ_VERDE)
		mantenerLuz(LUZ_AMARILLA)

		######## Sensado de INFRARROJO / PRESENCIA #######
		if senInfra == 0:
			if estInfra == 0:
				fn.log.debug("Se comenzo a detectar algo")
				estInfra = 1
				tieInfra1 = ya
			elif estInfra == 1 and (ya > tieInfra1 + dlPresencia): # HAY ALGO
				estInfra = 2
				fn.log.debug("Hay algo")
				encenderLuz(LUZ_BLANCA, dlLedPresencia)

				#fn.log.debug("Detect: ON - LED EN BDD EN FIREBASE: ON ")
				#if (salidaLed.val() == "False"):
				#	firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE
		elif senInfra == 1:
			if estInfra == 1:
				estInfra == 0 #Falsa Presencia
				fn.log.debug("Falsa presencia")
			elif estInfra == 2:
#NOTIFICAR NO PRESENCIA
                                estInfra = 0
				fn.log.debug("Detectada No presencia")
				#if (salidaLed.val() == "True"):
				#	firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE

		######## Sensado de GOLPES #######
		if estPuerta in [1,2] and estInfra == 2: #Puerta cerrada Y Presencia Detectada
                        
			if estPuerta == 1 or (ya < tieMicroSegm + dlMicroSegm and senMicroSegm == 0):	#sensando si hay GOLPE/NO-GOLPE en 1 Vez
				senMicro = GPIO.input(GPIO_MICROFONO)
                                fn.log.debug("Micro:"+str(senMicro))
                                if senMicro == 1:
					# PRIMER GOLPE SENSADO
					if estPuerta == 1:
                                                tiePuerta2 = ya
                                                estPuerta = 2 # Puerta cerrada Desbloqueando
                                                apagarLuz(LUZ_AMARILLA)
                                                golpes = 0
                                                del ingresado[:]
                                        encenderLuz(LUZ_VERDE,dlLedGolpeSensado)
					senMicroSegm = 1
                                        cantSegm += 1
					golpes += 1
				        ingresado.append(senMicroSegm)
			elif estPuerta == 2:
				cantSegm += 1
				ingresado.append(senMicroSegm)
				# Prepara proximo segmento
				tieMicroSegm = ya
				senMicroSegm = 0
				fn.log.debug(str(senMicroSegm)+",")

			if cantSegm == cantidadGolpes:
				#una vez que tiene los golpes ingresados para abrir la puerta, la compara con el pass seteado al principio    
				coincide = 1
				#si no coinciden , cambia la marca de coinciden a 0 y advierte de secuencia incorrecta con el led rojo, de lo contrario con el verde
				for i in range(cantidadGolpes - 1):
                                        fn.log.debug(str(cantidadGolpes) + " ... i:" + str(i))
                                        if (password[i] != ingresado[i]):
					        coincide = 0
						break
					else:
						fn.log.debug("el elemento "+str(i)+" coinciden")

				if(coincide == 0):
					estPuerta = 1 #Puerta Bloqueada
                                        GPIO.output(GPIO_LED_ROJO,True)
					encenderLuz(LUZ_ROJA,dlLedPassMal)
					fn.log.warning("Secuencia incorrecta!!! alerta policia")
				else:
					estPuerta = 11 #Puerta abriendo
					arduino.write('A')	#Abrir puerta
					encenderLuz(LUZ_VERDE,dlLedPassOk)
					fn.log.info("Puerta desbloqueada, por favor, ingrese")
					fn.log.debug("Enviada orden a Arduino")
				cantSegm = 0

		####### Sensado de PULSADOR #######
		if senPulsador == True and ya > tiePulsador + dlPulsadorDEBOUNCE:
                        fn.log.debug("Pulsador TRUE:"+str(estPuerta))
			tiePulsador = ya
			if estPuerta in [12,13]:
				arduino.write('A')	#Cerrar puerta
				estPuerta = 14 #Puerta cerrando
                                tiePuerta14 = ya
			elif estPuerta < 11:
				arduino.write('A')
				estPuerta = 11 #Puerta abriendo

				count = count + 1
				fn.log.debug("Boton presionado " + str(count) + " veces.")
				##estado = arduino.readline()
				##time.sleep(.02) #PERIODO DE ACCION DEL SERVO: 20 ms.

		####### Sensado de SERVO / FORZADO ########
		estado = arduino.readline()
		#fn.log.debug(estado)
		if estPuerta in [1,2,12,13]:
			#fn.log.debug("Arduino:"+estado)
			if estForzado == "FORZADO":
				if estPuerta in [1,2]: #ATENCION: Alertaria durante los golpes
					if estForzado == 0:
						estForzado = 1
						tieForzado = ya
					elif estForzado == 1 and ya > tieForzado + dlForzado:
						estForzado = 2
						fn.log.warning("PUERTA FORZADA")
						#NOTIFICAR A BBDD
			else:
				estForzado = 0

		####### Comprobacion Cambios en PUERTA #######
		impactarCambiosPuerta(False,
							(dlEstadoLuz[LUZ_BLANCA]),
							(estInfra == 2),
							(estPuerta in [12,13]),
							(estForzado == 2))


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

	time.sleep(2) # permitir visibilidad de ultimo estado de leds
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)
