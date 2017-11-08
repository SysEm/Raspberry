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

from firebase.firebase import FirebaseApplication, FirebaseAuthentication


if __name__ == '__main__':
    s = "C:\\Users\\ferbr_000\\AppData\\Local\\Temp\\-python-firebase-prueba.txt"
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

    data = {'name': 'Ozgur Vatansever', 'age': 26,
            'created_at': datetime.datetime.now()}

    snapshot = firebase.post('/users', data)
    print(snapshot['name'])
    with open(s, 'a') as f:
        f.write("\t")
        f.write(snapshot['name'])

    snapshot = firebase.get('/users', 'usr1',
                            params={'print': 'pretty'},
                            headers={'X_FANCY_HEADER': 'very fancy'})
    with open(s, 'a') as f:
        f.write("\t")
        f.write(snapshot['name'])


    def callback_get(response):
#        with open('/dev/null', 'w') as f:
        s = "C:\\Users\\ferbr_000\\AppData\\Local\\Temp\\-python-firebase-prueba.txt"
        with open(s, 'a') as f:
            f.write("\t")
            f.write("VOLVIO")
    firebase.get_async('/users', 'usr1', callback=callback_get)

sleep(50)
