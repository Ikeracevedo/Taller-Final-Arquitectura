#Clase CPU que simula los procesos de la isa como un pequeño computador
class CPU:
    #Constructor de la clase CPU
    #Que requiere como parametros program
    #Para saber la serie de instrucciones para la CPU ejecutar
    def __init__(self, program):
        #La variable registers es un diccionario que contiene:
        #Registros tempotales para alamacenar datos temporales, los que empiezan por "R"
        #"PC" lleva la cuenta de la posicion actual en el programa
        #"Z" es un indicador que se usa para saber si el resultado de la operacion es 0
        self.registers = {
            'R0': 0,
            'R1': 0,
            'R2': 0,
            'R3': 0,
            'PC': 0,    # Contador de programa
            'Z': 0      # Flag de cero
        }
        #Se crea una lista de posiciones de 256 que simula la RAM donde se pueden leer y escribir datos
        self.data_memory = [0] * 256  # Memoria de datos
        #Conjunto de instrucciones a ejecutar 
        self.program = program        # Programa a ejecutar

    #Funcion get_value que obtiene el valor de un operando (registro o valor inmediato)
    def get_value(self, operand):
        #Busca el operador si la cadena empieza por "R" lo busca en el diccionario de resgistros
        if isinstance(operand, str) and operand.startswith('R'):
            return self.registers[operand]
        #Sino retorna el valor
        return operand
    #Metodo execute_arithmetic que ejecuta operaciones aritméticas: ADD, SUB, MUL
    #Recibe como parametros:
    #OP que es una cadena que indica la operacion a realizar
    #operands que es una lisra donde estan las ubicaciones de los registros
    def execute_arithmetic(self, op, operands):
        #Dest: Lugar donde va a llegar el resultado de la operacion
        dest = operands[0]
        # src1 y 2 son los operandos fuente, los que van a ser utilizados para la operacion
        src1 = self.get_value(operands[1])
        src2 = self.get_value(operands[2])
        #Este selector permite decidoir la operacion y que deberia retornar cada operacion
        if op == 'ADD':
            result = src1 + src2
        elif op == 'SUB':
            result = src1 - src2
        elif op == 'MUL':
            result = src1 * src2
        else:
            #Si se escribe una operacion no valida se muestra la operacion y un mensaje de alerta
            raise ValueError(f"Operación no soportada: {op}")
        #Si el registro destino no existe en self.registers, lanzará un error de clave
        self.registers[dest] = result
        self.registers['Z'] = 1 if result == 0 else 0

    #Metodo execute_load carga un valor de memoria a un registro
    #Recibe como parametro operands que es un arreglo donde se guardan registros
    def execute_load(self, operands):
        #Selecciona el registro destino.
        reg = operands[0]
        #Seleccion la direccion de origen
        address = operands[1]
        # Toma el valor del registro address de la memoria de datos y lo guarda en el registro 
        self.registers[reg] = self.data_memory[address]

    #Metodo execute_store que almacena un valor de registro en memoria
    #Recibe como parametro operands que es un arreglo donde se guardan registros
    def execute_store(self, operands):
        #Selecciona el registro destino
        reg = operands[0]
        #Seleccion la direccion de origen
        address = operands[1]
        #Se toma el calor almacenado del registro y lo guarda en la posicion de memoria
        self.data_memory[address] = self.registers[reg]

    #Metodo execute_jump maneja los saltos condicionales
    #Recibe como parametros:
    #operands que es un arreglo donde se guardan registros
    #Op: es el tipo de salto
    def execute_jump(self, op, operands):
        #target: dirección de destino del salto
        target = operands[0]
        #Selector que define que hace cada salto
        if op == 'JMP':
            self.registers['PC'] = target
        elif op == 'JZ' and self.registers['Z'] == 1:
            self.registers['PC'] = target
        elif op == 'JNZ' and self.registers['Z'] == 0:
            self.registers['PC'] = target

    #Metodo step ejecuta una instrucción del programa
    def step(self):
        #Obtiene el contador del programa
        pc = self.registers['PC']
        #Verfica si el prorgrama termino
        if pc >= len(self.program):
            return False  # Fin del programa
        #Extrae la instruccion actual 
        instruction = self.program[pc]
        #Extrae el tipo de instruccion
        opcode = instruction['opcode']
        #Extrae los operandos de la instruccion 
        operands = instruction['operands']

        # Ejecutar instrucción'
        #Si es aricmetica
        if opcode in ['ADD', 'SUB', 'MUL']:
            self.execute_arithmetic(opcode, operands)
        #Si es de carga
        elif opcode == 'LOAD':
            self.execute_load(operands)
        #Si es de almacenamiento
        elif opcode == 'STORE':
            self.execute_store(operands)
        #Si es de salto
        elif opcode in ['JMP', 'JZ', 'JNZ']:
            self.execute_jump(opcode, operands)
        #En caso de no reconocer la instruccion
        else:
            raise ValueError(f"Instrucción desconocida: {opcode}")

        # Actualizar PC si no fue modificado por un salto
        if self.registers['PC'] == pc:
            self.registers['PC'] += 1

        return True
    #Metodo que corre el programa por completo
    def run(self):
        cycle = 0
        while (self.IF_stage or self.ID_stage or self.EX_stage or
                self.MEM_stage or self.WB_stage):
            self.step()
            cycle += 1
        print(f"Total ciclos: {cycle}")
        return cycle

#Estos datos son de prueba para comprobar que la cache funcione por si sola y asi ir verificando los procesos
#En la construccion del programa
# Programa que suma números del 1 al 5
program = [
    # Inicializar valores
    {'opcode': 'LOAD', 'operands': ['R0', 0]},  # R0 = 0 (contador)
    {'opcode': 'LOAD', 'operands': ['R1', 1]},  # R1 = 1 (incremento)
    {'opcode': 'LOAD', 'operands': ['R2', 2]},  # R2 = 0 (acumulador)

    # Almacenar valores iniciales en memoria
    {'opcode': 'STORE', 'operands': ['R0', 10]},  # Mem[10] = 0
    {'opcode': 'STORE', 'operands': ['R1', 11]},  # Mem[11] = 1

    # Bucle principal
    {'opcode': 'LOAD', 'operands': ['R3', 10]},  # R3 = contador
    {'opcode': 'ADD', 'operands': ['R3', 'R3', 'R1']},  # Incrementar contador
    {'opcode': 'STORE', 'operands': ['R3', 10]},  # Actualizar contador
    {'opcode': 'ADD', 'operands': ['R2', 'R2', 'R3']},  # Acumular
    {'opcode': 'SUB', 'operands': ['R0', 'R3', 5]},  # Comparar con 5
    {'opcode': 'JNZ', 'operands': [6]},  # Saltar a instrucción 6 si no es cero
]

# Configurar CPU y ejecutar
cpu = CPU(program)
cpu.data_memory[0] = 0  # Inicializar valores en memoria
cpu.data_memory[1] = 1
cpu.run()

print("Resultado suma 1-5:", cpu.registers['R2'])  # Debería ser 15