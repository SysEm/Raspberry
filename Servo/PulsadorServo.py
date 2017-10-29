import RPi.GPIO as GPIO
import time
import serial


GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.IN)
arduino = serial.Serial('/dev/ttyACM0', 9600) #Objeto arduino linkeado al puerto serie

count = 0
estado = arduino.readline()

print("Estado de la puerta: " + str(estado))

while True:
    inputValue = GPIO.input(24)
    if (inputValue == True):
        count = count + 1
        print("Boton presionado " + str(count) + " veces.")
        arduino.write('A')
        estado = arduino.readline()
        print(estado)
        time.sleep(.3) #DEBOUNCE
    time.sleep(.01)

GPIO.cleanup()
