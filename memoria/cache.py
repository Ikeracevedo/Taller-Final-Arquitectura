#Clase CacheLine simula el comportamiento de una linea de cache
class CacheLine:
    #Constructor de la clase cache que pasa por composicion
    #Valid: Indicador de datos validos en la linea de cache
    #tag: etiqueta para identificar a que bloque de memoria principal corresponde
    #data: los datos que se guardan en cada linea 
    def __init__(self):
        self.valid = False
        self.tag = None
        self.data = None
        

#Clase Cache que simula el funcionamiento de una memoria cache
class Cache:
    #Constructor que recibe como parametros
    #num_lines: el numero de lineas de cache a simular
    #block_size: ek tamaño de cada bloque de cache
    def __init__(self, num_lines, block_size):
        self.num_lines = num_lines
        self.block_size = block_size
        #El self.lines genera lineas de cache en un rango de 1 hasta las lineas determinadas por la funcion
        self.lines = [CacheLine() for _ in range(num_lines)]
        self.hits = 0
        self.misses = 0

    #Metodo read que simula la lectura de datos desde la cache 
    #Recibe como parametros:
    #Adress es la direccion en memoria que se quiere leer
    #main_memory es la memoria principal como la lista o el arreglo a trabajar 
    def read(self, address, main_memory):
        #Por medio de esta operacion se calcula el indice donde esta el bloque de memoria solicitado 
        line_index = (address // self.block_size) % self.num_lines
        #Calcula la etiqueta tag asociada a la direccion, ayuda a comprobar si el bloque corresponde a la direccion solicitada
        tag = address // (self.block_size * self.num_lines)
        #Accede a la linea por medio del indice que ya ha sido calculado 
        line = self.lines[line_index]
        #Por medio del selector se verigica si la linea de cache es valida y el tag coincide
        if line.valid and line.tag == tag:
            self.hits += 1
            # Cache hit (Acierto) si hace este hit eso significa que el dato ya esta en la cache 
            print("Cache hit!")
            #Offset es la posicion exacta del dato dentro de un bloque 
            offset = address % self.block_size
            #Retorna el dato de la posicion obetnida en el offset
            return line.data[offset]
        else:
            self.misses += 1
            #Si hay un fallo en cargar el dato de la memoria cache, carga el bloque completo 
            # Cache miss: cargar bloque desde memoria principal
            print("Cache miss, cargando bloque...")
            # Se marca la linea como valida
            line.valid = True
            # se actualiza la etiqueta tag
            line.tag = tag
            # Se calcula el inicio del bloque en la memoria principal
            start = address - (address % self.block_size)
            # Se carga el bloque desde la memoria principal
            line.data = main_memory[start:start + self.block_size]
            # Se calcula el offset y se retorna el dato
            offset = address % self.block_size
            return line.data[offset]
    #Metodo write que simula la escritura de los datos en la memoria cache 
    #Recibe como parametros:
    #Adress: que es la direccion a leer
    #Value: que es el valor o cantidad de dato con el que se va a llenar esa posicion
    #main_memory: Este es lo que simula la memoria principal o donde se guarda todo lo de la cache
    def write(self, address, value, main_memory):
        #Determina en que linea de cache esta el bloque a modificar
        line_index = (address // self.block_size) % self.num_lines
        #Calcula la etiqueta asosidad a ese bloque de memoria
        tag = address // (self.block_size * self.num_lines)
        #Accede a la linea correspondiente
        line = self.lines[line_index]
        #Comprueba si la linea de cache es valida y si la etiqueta conincide
        if line.valid and line.tag == tag:
            # Cache hit: escribir en caché y memoria principal (write-through)
            #El offset permite saber la posicion dentro del bloque
            offset = address % self.block_size
            #Escribe un dato en la linea de cache 
            line.data[offset] = value
            #Escribe el dato en la memoria principal
            main_memory[address] = value
            #Mensajes de debug
            print("Cache hit: escribiendo dato.")
        else:
            # Cache miss: escribir directamente en memoria principal
            #Si ni hubo acceso a la memoria solo se esribe el valor en la memoria principal 
            main_memory[address] = value
            #Mensajes de debug
            print("Cache miss: escribiendo solo en memoria principal.")
