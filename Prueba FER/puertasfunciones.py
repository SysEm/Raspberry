import json
from firebase import jsonutil
import os
import logging #https://docs.python.org/3/howto/logging.html

###########     FUNCIONES COMUNES     ############
base_dir = os.path.dirname(os.path.abspath(__file__)) #<-- absolute dir del script
def abs_path(rel_path):
    return os.path.join(base_dir, rel_path)

# Lee en forma segura un archivo (comprueba si no existe el archivo)
# return: objeto 'dict' con el json del archivo, None en otro caso
def leer(path):
    if os.path.exists(path):
        arch=open(path,"r+")
        arch=arch.read()
        if arch!="":
            return json.loads(arch)
    return None
	
# Guarda un objeto serializable en un archivo (crea si no existe, pisa contenido)
# return: string de objeto serializado guardado en archivo, None en otro caso
def escribir(path,json_obj):
    try:
        jobj=json.dumps(json_obj, cls=jsonutil.JSONEncoder)
    except TypeError:
        jobj=None
    if jobj!="" and jobj!=None:
        with open(path,"w+") as arch:
            arch.write(jobj)
    return jobj

#Nivel de Log a mostrar
#logging.basicConfig(level=logging.INFO)
#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='puerta.log',level=logging.DEBUG)
#logging.basicConfig(level=logging.CRITICAL)

# Variable Global log como logging
log = logging.getLogger(__name__)
	
if __name__ == "__main__":
	print("Archivo para importar. No lo ejecute.")
else:
	print("Path Base:",abs_path(""))
