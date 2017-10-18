'''
* Control de ServoMotor en Arduino desde Raspberry Pi
* Ver: https://github.com/mcortex/ArduinoTests/blob/master/RaspberryLed/RaspberryServo.ino
'''

import serial

arduino = serial.Serial('/dev/ttyACM0', 9600) #Objeto arduino linkeado al puerto serie

print ("Comenzando comunicacion serial con Arduino: ")

while True:
    comando = raw_input('Introduce una A para abrir y una C para cerrar, S para salir: ') #Input por teclado
    arduino.write(comando) #Envia el comando por el puerto serial
    if comando == 'A':
        print('Servo Abierto: posicion 0 grados')
    elif comando == 'C':
        print ('Servo Cerrado: posicion 90 grados')
    elif comando == 'S':
        print ('Saliendo, cerrando comunicacion serie.')
        arduino.close() #Cerramos la comunicacion serie
        break

