import datetime
from time import sleep

import json
#from firebase import jsonutil
#from firebase.firebase import FirebaseApplication, FirebaseAuthentication
import os

script_dir = os.path.dirname(os.path.abspath(__file__)) #<-- absolute dir the script is in
rel_path = "-json-read-write.txt"
abs_file_path = os.path.join(script_dir, rel_path)

def leer(path):
    if os.path.exists(path):
        arch=open(path,"r+")
        arch=arch.read()
        if arch!="":
            return json.loads(arch)
    return None



if __name__ == '__main__':
    s = ".\-json-read-write.txt"
    print(s)
    print(abs_file_path)

    intentos=0
    while intentos<10:
        intentos+=1
        tmp=leer(abs_file_path)
        if tmp!=None:
            print(leer(abs_file_path))
        else:
            print("Archivo inexistente:", abs_file_path)

        sleep(5)
        
##        f.write(datetime.datetime.now())

##    SECRET = 'AIzaSyDHvAOR5d1hd1gEEHBS3Ep2LxybRvUu_OA'
##    DSN = 'https://soatp-2dfc9.firebaseio.com'
##    EMAIL = 'ferbroqua@gmail.com'

##    SECRET = '12345678901234567890'
##    DSN = 'https://firebase.localhost'
##    EMAIL = 'your@email.com'
##    authentication = FirebaseAuthentication(SECRET,EMAIL, True, True)
    #firebase = FirebaseApplication(DSN, authentication)

##    firebase = FirebaseApplication(DSN, None)
##
##    data = {'name': 'Sarasa Sarlanga', 'age': 28,
##            'created_at': datetime.datetime.now()}
##
##    snapshot = firebase.post('/users', data)
##    print(snapshot['name'])
##    with open(s, 'a') as f:
##        f.write("\t")
##        f.write(snapshot['name'])
##
##    snapshot = firebase.get('/users/puts', 'usr1',
##                            params={'print': 'pretty'},
##                            headers={'X_FANCY_HEADER': 'very fancy'})
##    with open(s, 'a') as f:
##        f.write("\t")
##        if snapshot!=None:
##            f.write(snapshot['name'])
##        else:
##            f.write("no vino 'usr1'")

