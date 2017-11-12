import RPi.GPIO as GPIO
import time
import serial
import signal
import sys
#import os

import puertasfunciones as fn

###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	global arduino
	fn.log.warning('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

# def imprimir(msj)
	# if mout==0: logger(msj)
	# elif mout==1: write(

def playDingDong(): #Reproduce audio "ding-dong.mp3" en el mismo path
	os.system('mpg321 -q ding-dong.mp3 &')


########### VARIABLES GLOBALES ############
#listas, contiene el password por default de golpes inicial y el que ingreses al intentar abrir la puerta
password = []
ingresado = []
veces = 0
count = 0
# Estados y Deadlines: Usados para corte de control
deadLine = time.time()
dl

###########  CONFIGURACIONES   ############
#Mensajes salientes
mout=0
#Patas GPIO usadas
GPIO_LED_ROJO = 4
GPIO_LED_VERDE = 5
GPIO_MICROFONO = 17
GPIO_LED_BLANCO = 18
GPIO_LED_PRESENCIA = GPIO_LED_BLANCO
GPIO_INFRARROJO = 23
GPIO_SERVO = 24
#tiempo de escucha por cada golpe para detectar un golpe o no
tiempoEscucha = 1.5
#seteo de numeros de golpes que se ingresaran como password
cantidadGolpes = 5

try:
	# Setup / Configuracion de GPIO
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(GPIO_INFRARROJO, GPIO.IN) ## entrada
	GPIO.setup(GPIO_LED_PRESENCIA, GPIO.OUT) ## salida
	GPIO.setup(GPIO_MICROFONO, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## entrada
	GPIO.setup(GPIO_LED_ROJO, GPIO.OUT) ## salida
	GPIO.setup(GPIO_LED_VERDE, GPIO.OUT) ## salida
	GPIO.setup(GPIO_LED_BLANCO, GPIO.OUT) ## salida
	GPIO.setup(GPIO_SERVO, GPIO.IN) ## entrada

	#Objeto arduino linkeado al puerto serie
	arduino = serial.Serial('/dev/ttyACM0', 9600) 

    fn.log.info("Por favor, setee la secuencia de golpes")
    fn.log.info("La cantidad de golpes son ", cantidadGolpes)
    fn.log.info("Cada vez que se prende el led rojo, se espera o no un golpe")
	if mout>0: time.sleep(2)

	## GENERACION DE CÓDIGO DE GOLPES ##
	veces = 0
    while veces < cantidadGolpes:
        valor = 0
        deadLine = time.time() + tiempoEscucha
        
        #se prende el led indicando que espera un golpe
        GPIO.output(GPIO_LED_ROJO,True)
    
		#bucle de escucha de un golpe.. en el tiempo indicado que dura un golpe
        while time.time() < deadLine :
            if GPIO.input(GPIO_MICROFONO):
                #prende el led verde indicando que se esucho un golpe
                GPIO.output(GPIO_LED_VERDE,True)
                valor = 1
            else:
                GPIO.output(GPIO_LED_VERDE,False)
        veces = veces + 1
        
        #se termina de escuchar un golpe, y se guarda el resultado en la lista
        GPIO.output(GPIO_LED_ROJO,False)
        time.sleep(1)
        fn.log.debug(valor,",")
        password.append(valor)
	
    # PRENDE AMBAS LUCES : indica que se va pedir que ingreses el pass para abrir o no la puerta
    GPIO.output(GPIO_LED_ROJO,True)
    GPIO.output(GPIO_LED_VERDE,True)
	
	
    fn.log.info("Por favor, Ingrese la contraseña")
    fn.log.info("La cantidad de golpes son ", cantidadGolpes)
    fn.log.info("Cada vez que se prende el led rojo, se espera o no un golpe")

    time.sleep(1)
	
	# APAGA AMBAS LUCES
    GPIO.output(GPIO_LED_ROJO,False)
    GPIO.output(GPIO_LED_VERDE,False)
    #time.sleep(2)
	
	estado = arduino.readline()

	fn.log.info("Inicializando escucha. Con Ctrl+C sale del programa")
	fn.log.debug("Estado de la puerta: " + str(estado))
	if mout>0: time.sleep(2)

	######### COMIENZA BUCLE INFINITO ##########
	while True:	
		ya = time.time()
		######## Sensado de PRESENCIA #######
'''
    if (salidaLed.val() == "True"):
        print("Estado actual: True")
    elif (salidaLed.val() == "False"):
        print("Estado actual: False")
'''
		senInfra = GPIO.input(GPIO_INFRARROJO) #LEO EL SENSOR INFRARROJO PARA SABER SI DETECTO ALGO O NO, DEVUELVE 0 SI DETECTO ALGO
		if sensor==0:
			fn.log.debbug("Se comenzo a detectar algo")
			#fn.log.debbug("Se detecto algo")
			GPIO.output(GPIO_LED_PRESENCIA, True) # PRENDO EL LED
			fn.log.debbug("Detect: ON - LED EN BDD EN FIREBASE: ON ")
			if (salidaLed.val() == "False"):
				 firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE
		elif sensor==1:
			fn.log.debbug("No se detecta nada")
			GPIO.output(GPIO_LED_PRESENCIA, False)
			fn.log.debbug("Detect: OFF - LED EN BDD EN FIREBASE: OFF ")
			if (salidaLed.val() == "True"):
				firebase_(puerta,salidaLed.val()) # LLAMO A UNA FUNCION PARA MODIFICAR EL CAMPO ESTADO EN FIREBASE

		######## Sensado de GOLPES #######
		senMicro = GPIO.input(GPIO_MICROFONO)
		if ya < deadLine:	#sensando si hay GOLPE/NO-GOLPE en 1 Vez
			if senMicro:
				GPIO.output(GPIO_LED_VERDE,True)
				valor = 1
			else:
				GPIO.output(GPIO_LED_VERDE,False)
		else: #sensado completo de 1 Vez
			if veces > cantidadGolpes:
				veces = 0 # reinicia la cuenta de Veces
			deadLine = time.time() + tiempoEscucha
		if veces < cantidadGolpes:
			valor = 0
			deadLine = time.time() + tiempoEscucha
			GPIO.output(GPIO_LED_ROJO,True)

			while time.time() < deadLine :
					
			veces = veces + 1
			GPIO.output(GPIO_LED_ROJO,False)
			time.sleep(1)
			fn.log.debug(valor,",")
			ingresado.append(valor)
			
		if veces == cantidadGolpes:
			#una vez que tiene los golpes ingresados para abrir la puerta, la compara con el pass seteado al principio    
			coincide = 1
			#si no coinciden , cambia la marca de coinciden a 0 y advierte de secuencia incorrecta con el led rojo, de lo contrario con el verde
			for i in range(cantidadGolpes - 1):
				if (password[i] != ingresado[i]):
					coincide = 0
					break
				else:
					fn.log.debug("el elemento ",i," coinciden")
			
			if(coincide == 0):
				GPIO.output(GPIO_LED_ROJO,True)
				fn.log.error("Secuencia incorrecta!!! alerta policia")
			else:
				GPIO.output(GPIO_LED_VERDE,True)
				fn.log.info("Puerta abierta, por favor, ingrese")
	
		####### Sensado de SERVO #######
		senServo = GPIO.input(GPIO_SERVO)

		if (senServo == True):
			count = count + 1
			fn.log.debug("Boton presionado " + str(count) + " veces.")
			arduino.write('A')
			time.sleep(.3) #DEBOUNCE
			estado = arduino.readline()
			fn.log.debug(estado)
			#time.sleep(.02) #PERIODO DE ACCION DEL SERVO: 20 ms.

		estado = arduino.readline()
		strEstado = str(estado)
		fn.log.debug(estado)
		#NO FUNCIONA ESTE IF REVISAR
		#if (strEstado == "FORZADO"):
		#    fn.log.debug(estado)
		#signal.signal(signal.SIGINT, signal_handler)
		#time.sleep(.01)
	
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
	
	time.sleep(2) # permitir visibilidad de último estado de leds
	arduino.close()
    GPIO.cleanup()
	sys.exit(0)