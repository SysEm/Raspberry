import RPi.GPIO as GPIO
import time
import serial
import signal
import sys

import logging

###########     FUNCIONES      ############
def signal_handler(signal, frame): # Captura de Teclado
	logger.warn('Ha Presionado Ctrl+C, saliendo')
	arduino.close()
	GPIO.cleanup()
	sys.exit(0)

# def imprimir(msj)
	# if mout==0: logger(msj)
	# elif mout==1: write(
	
###########  CONFIGURACIONES   ############
#Nivel de Log a mostrar
#logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
#Mensajes salientes
mout=0
#Patas GPIO usadas
micro = 17
ledRojo = 4
ledVerde = 18
servo = 24
#tiempo de escucha por cada golpe para detectar un golpe o no
tiempoEscucha = 1.5
#seteo de numeros de golpes que se ingresaran como password
cantidadGolpes = 5

########### VARIABLES GLOBALES ############
#listas, contiene el password por default de golpes inicial y el que ingreses al intentar abrir la puerta
password = []
ingresado = []
logger = logging.getLogger(__name__)
veces = 0
count = 0

try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(micro, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## GPIO 17 como entrada
	GPIO.setup(ledRojo, GPIO.OUT) ## GPIO 4 como salida
	GPIO.setup(ledVerde, GPIO.OUT) ## GPIO 18 como salida
	GPIO.setup(servo, GPIO.IN) ## GPIO 24 como entrada

	#Objeto arduino linkeado al puerto serie
	arduino = serial.Serial('/dev/ttyACM0', 9600) 

    logger.info("Por favor, setee la secuencia de golpes")
    logger.info("La cantidad de golpes son ", cantidadGolpes)
    logger.info("Cada vez que se prende el led rojo, se espera o no un golpe")
	if mout>0: time.sleep(2)

	## LECTURA DE CÓDIGO DE GOLPES ##
	veces = 0
    while veces < cantidadGolpes:
        valor = 0
        deadLine = time.time() + tiempoEscucha
        
        #se prende el led indicando que espera un golpe
        GPIO.output(ledRojo,True)
    
		#bucle de escucha de un golpe.. en el tiempo indicado que dura un golpe
        while time.time() < deadLine :
            if GPIO.input(micro):
                #prende el led verde indicando que se esucho un golpe
                GPIO.output(ledVerde,True)
                valor = 1
            else:
                GPIO.output(ledVerde,False)
        veces = veces + 1
        
        #se termina de escuchar un golpe, y se guarda el resultado en la lista
        GPIO.output(ledRojo,False)
        time.sleep(1)
        logger.debug(valor,",")
        password.append(valor)
	
    # PRENDE AMBAS LUCES : indica que se va pedir que ingreses el pass para abrir o no la puerta
    GPIO.output(ledRojo,True)
    GPIO.output(ledVerde,True)
	
	
    logger.info("Por favor, Ingrese la contraseña")
    logger.info("La cantidad de golpes son ", cantidadGolpes)
    logger.info("Cada vez que se prende el led rojo, se espera o no un golpe")

    time.sleep(1)
	# APAGA AMBAS LUCES
    GPIO.output(ledRojo,False)
    GPIO.output(ledVerde,False)
    time.sleep(2)
	
	estado = arduino.readline()

	logger.info("Inicializando escucha. Con Ctrl+C sale del programa")
	logger.debug("Estado de la puerta: " + str(estado))
	if mout>0: time.sleep(2)

    veces = 0	
	######### COMIENZA BUCLE INFINITO ##########
	while True:
		######## Sensado de GOLPES #######
		if veces < cantidadGolpes:
			valor = 0
			deadLine = time.time() + tiempoEscucha
			GPIO.output(ledRojo,True)

			while time.time() < deadLine :
				if GPIO.input(micro):
					GPIO.output(ledVerde,True)
					valor = 1
				else:
					GPIO.output(ledVerde,False)
					
			veces = veces + 1
			GPIO.output(ledRojo,False)
			time.sleep(1)
			logger.debug(valor,",")
			ingresado.append(valor)
		else:
			#una vez que tiene los golpes ingresados para abrir la puerta, la compara con el pass seteado al principio    
			coincide = 1
			
			#si no coinciden ,, cambia la marca de coinciden a 0 y advierte de secuencia incorrecta con el led rojo, de lo contrario con el verde
			for i in range(cantidadGolpes - 1):
				if (password[i] != ingresado[i]):
					coincide = 0
				else:
					logger.debug("el elemento ",i,"coinciden")
			
			if(coincide == 0):
				GPIO.output(ledRojo,True)
				logger.error("Secuencia incorrecta!!! alerta policia")
			else:
				GPIO.output(ledVerde,True)
				logger.info("Puerta abierta, por favor, ingrese")
	
		####### Sensado de SERVO #######
		inputValue = GPIO.input(24)

		if (inputValue == True):
			count = count + 1
			logger.debug("Boton presionado " + str(count) + " veces.")
			arduino.write('A')
			time.sleep(.3) #DEBOUNCE
			estado = arduino.readline()
			logger.debug(estado)
			#time.sleep(.02) #PERIODO DE ACCION DEL SERVO: 20 ms.

		estado = arduino.readline()
		strEstado = str(estado)
		logger.debug(estado)
		#NO FUNCIONA ESTE IF REVISAR
		#if (strEstado == "FORZADO"):
		#    logger.debug(estado)
		signal.signal(signal.SIGINT, signal_handler)
		time.sleep(.01)
finally:
	time.sleep(2)
    GPIO.cleanup()