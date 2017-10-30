import RPi.GPIO as GPIO
import time
import serial
import signal
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
arduino = serial.Serial('/dev/ttyACM0', 9600) #Objeto arduino linkeado al puerto serie

count = 0
estado = arduino.readline()


### FUNCIONES:
def signal_handler(signal, frame):
    print('Ha Presionado Ctrl+C, saliendo')
    arduino.close()
    GPIO.cleanup()
    sys.exit(0)

print("Inicializando escucha. Con Ctrl+C sale del programa")
print("Estado de la puerta: " + str(estado))

while True:
    inputValue = GPIO.input(24)
    if (inputValue == True):
        count = count + 1
        print("Boton presionado " + str(count) + " veces.")
        arduino.write('A')
        time.sleep(.3) #DEBOUNCE
        estado = arduino.readline()
        print(estado)
        time.sleep(.02) #PERIODO DE ACCION DEL SERVO: 20 ms.
    estado = arduino.readline()
    strEstado = str(estado)
    print(estado)
    #NO FUNCIONA ESTE IF REVISAR
    #if (strEstado == "FORZADO"):
    #    print(estado)
    signal.signal(signal.SIGINT, signal_handler)
    time.sleep(.01)
