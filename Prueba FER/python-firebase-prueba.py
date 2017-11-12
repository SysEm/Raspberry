# http://ozgur.github.io/python-firebase/
# https://github.com/ozgur/python-firebase

##from firebase import firebase
###import firebase ##
##from time import sleep
##from firebase import jsonutil ##
##
##firebase2 = firebase.FirebaseApplication('https://soatp-2dfc9.firebaseio.com', authentication=None)
##
##casa = ""
##
##def log_puertas(response):
##    #with open('%TEMP%/%s.json' % response.keys()[0], 'w') as users_file:
##    #    users_file.write(json.dumps(response, cls=jsonutil.JSONEncoder))
##    casa = response
##
###get_async(self, url, name, callback=None, params=None, headers=None)
##firebase2.get_async('/baseDatosSoa/puertas/Puerta Fer', None, None, log_puertas, {'print': 'pretty'})
##
##tiempo = 0
##sleep(1)
####while (casa==""):
####    tiempo = tiempo + 1
##
##print(casa)

import datetime
from time import sleep
import json
from firebase import jsonutil ##
from firebase.firebase import FirebaseApplication, FirebaseAuthentication


if __name__ == '__main__':
    s = "C:\\-python-firebase-prueba.txt"
    print(s)
    with open(s, 'a') as f:
        f.write("\n")
        f.write(s)
##        f.write(datetime.datetime.now())

    SECRET = 'AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA'
    DSN = 'https://soatp-2dfc9.firebaseio.com'
    EMAIL = 'ferbroqua@gmail.com'
##    SECRET = '12345678901234567890'
##    DSN = 'https://firebase.localhost'
##    EMAIL = 'your@email.com'
    authentication = FirebaseAuthentication(SECRET,EMAIL, True, True)
    #firebase = FirebaseApplication(DSN, authentication)
    firebase = FirebaseApplication(DSN, None)

    data = {'name': 'Fernando Broqua', 'age': 28,
            'created_at': datetime.datetime.now()}
    snapshot = firebase.post('/users/posts', data)    #post con ID autogenerado
    print(snapshot['name'])
    with open(s, 'a') as f:
        f.write("\tPOST:")
        f.write(snapshot['name'])

    # Obtener el último de la lista "puts", ordenado por clave alfabéticamente
##    prms = {'print': 'pretty',
##            'orderBy' : '"$key"',
##            'limitToLast' : '1'}
    # Obtener el último de la lista "puts", ordenado por clave secundaria: "age"
    prms = {'print': 'pretty',
            'orderBy' : '"age"',
            'limitToLast' : '1'}
    print(json.dumps(prms))
    snapshot = firebase.get('/users/puts', None,
                            params=prms,
                            headers={'X_FANCY_HEADER': 'very fancy'})
    print(json.dumps(snapshot))
    with open(s, 'a') as f:
        f.write("\tGET:")
        #f.write(snapshot['name'])
        f.write(json.dumps(snapshot, cls=jsonutil.JSONEncoder))

    for key,value in snapshot.items():
    	print(key, ' ', json.dumps(value))
    	snapshot = value
    edad = snapshot['age'] + 1 
    nuevoid = "usr"+str(edad)
    snapshot['name'] = "Usuario "+str(edad)
    snapshot['age'] = edad
    snapshot = firebase.put('/users/puts', nuevoid, snapshot)    #put con ID Personalizado
    print(snapshot['name'])
    with open(s, 'a') as f:
        f.write("\tPUT:")
        f.write(json.dumps(snapshot, cls=jsonutil.JSONEncoder))

    # Obtener /users/puts/usr1
    updateid = 'usr1'
    snapshot = firebase.get('/users/puts/', updateid,
                            params={'print': 'pretty'},
                            headers={'X_FANCY_HEADER': 'very fancy'})
    snapshot['age'] = edad
    print(snapshot['age']) #cambia edad
    snapshot = firebase.put('/users/puts', updateid, snapshot)    #actualiza/graba usr1
    with open(s, 'a') as f:
        f.write("\tGET:")
        #f.write(snapshot['name'])
        f.write(json.dumps(snapshot, cls=jsonutil.JSONEncoder))



    def callback_get(response):
#        with open('/dev/null', 'w') as f:
##        s = "C:\\Users\\ferbr_000\\AppData\\Local\\Temp\\-python-firebase-prueba.txt"
        with open(s, 'a') as f:
            f.write("\tGET_ASYNC:")
            f.write("VOLVIO")
    firebase.get_async('/users', 'usr1', callback=callback_get)

##sleep(5)
