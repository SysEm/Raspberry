import RPi.GPIO as GPIO
import time


#GPIO que se usan para el microfono y los leds
micro = 17
ledRojo = 4
ledVerde = 18

#seteo como inputs y outputs de los GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(micro, GPIO.IN, pull_up_down=GPIO.PUD_UP) ## GPIO 17 como entrada
GPIO.setup(ledRojo, GPIO.OUT) ## GPIO 4 como salida
GPIO.setup(ledVerde, GPIO.OUT) ## GPIO 18 como salida

#listas, contiene el password por default de golpes inicial y el que ingreses al intentar
#abrir la puerta
password = []
ingresado = []

#tiempo de escucha por cada golpe para detectar un golpe o no
tiempoEscucha = 3

#seteo de numeros de golpes que se ingresaran como password
cantidadGolpes = 3

try:
    veces = 0

######################## GRABACION DE PASSWORD DE SONIDO ######################## 
    print ("Por favor, setee la secuencia de golpes")
    print ("La cantidad de golpes son ", cantidadGolpes)
    print ("cada ves que se prende el led rojo, se espera o no un golpe")
    #el sleep es para que se pueda leer lo que se pide ja.. se puede indicar con los led, claro
    time.sleep(1)
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
                time.sleep(0.3)
            else:
                GPIO.output(ledVerde,False)

        veces = veces + 1

        #se termina de escuchar un golpe, y se guarda el resultado en la lista
        GPIO.output(ledRojo,False)
        time.sleep(.5)
        print (valor,",")
        password.append(valor)


######################## VERIFICACION DE PASSWORD DE SONIDO ######################## 
    # indica que se va pedir que ingreses el pass para abrir o no la puerta
    GPIO.output(ledRojo,True)
    GPIO.output(ledVerde,True)

    print ("Por favor, Ingrese la contrasena")
    print ("La cantidad de golpes son ", cantidadGolpes)
    print ("cada ves que se prende el led rojo, se espera o no un golpe")


    time.sleep(.5)
    GPIO.output(ledRojo,False)
    GPIO.output(ledVerde,False)
    time.sleep(.3)

    veces = 0

    while veces < cantidadGolpes:
        valor = 0
        deadLine = time.time() + tiempoEscucha
        GPIO.output(ledRojo,True)

        while time.time() < deadLine :
            if GPIO.input(micro):
                GPIO.output(ledVerde,True)
                valor = 1
                time.sleep(0.3)
            else:
                GPIO.output(ledVerde,False)

        veces = veces + 1
        GPIO.output(ledRojo,False)
        time.sleep(1)
        print (valor,",")
        ingresado.append(valor)

    #una vez que tiene los golpes ingresados para abrir la puerta, la compara con el pass seteado al principio    
    coincide = 1

    #si no coinciden ,, cambia la marca de coinciden a 0 y advierte de secuencia incorrecta con el led rojo, de lo contrario con el verde
    for i in range(cantidadGolpes):
        if (password[i] != ingresado[i]):
            coincide = 0
        else:
            print("el elemento ",i,"coinciden")

    if(coincide == 0):
        GPIO.output(ledRojo,True)
        print ("Secuencia incorrecta!!! alerta policia")
    else:
        GPIO.output(ledVerde,True)
        print ("Puerta abierta, por favor, ingrese")

#este para que se vea el resultado en los led. sino se apagan con el clean...
    time.sleep(2)
finally:
    GPIO.cleanup()



#manera de declarar un metodo y los eventos detect y callback
##def callback(micro)d:
##    if GPIO.input(micro):
##        print ("sonido detectado")
##        GPIO.output(4, True)
##    else:
##        print ("sonido sin detectar")
##        GPIO.output(4, 
##GPIO.add_event_detect(micro, GPIO.BOTH, bouncetime=100)
##GPIO.add_event_callback(micro, callback)
