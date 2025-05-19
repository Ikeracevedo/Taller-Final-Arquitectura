class Device:
    def __init__(self):
        self.data_ready = False
        self.data = None

    def generate_data(self, value):
        self.data = value
        self.data_ready = True

    def clear(self):
        self.data_ready = False
        self.data = None

def check_interrupt(self, device):
    if device.data_ready:
        print("Interrupción detectada!")

        # Guardar PC actual para poder regresar después
        self.saved_PC = self.registers['PC']

        # Cambiar PC a dirección de rutina de interrupción (ejemplo: 100)
        self.registers['PC'] = 100

        # Aquí puedes ejecutar directamente la rutina o marcar que estás en modo interrupción
        self.handling_interrupt = True

        # Limpiar la interrupción del dispositivo
        device.clear()
