import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from memoria import cache
from Device import moduloEntradaySalida

class PipelinedCPU:
    def __init__(self, program):
        self.registers = {
            'R0': 0, 'R1': 0, 'R2': 0, 'R3': 0, 'R4': 0, 'R5': 0,
            'PC': 0, 'Z': 0
        }
        self.data_memory = [0] * 256
        self.program = program
        self.IF_stage = None
        self.ID_stage = None
        self.EX_stage = None
        self.MEM_stage = None
        self.WB_stage = None
        self.stall = False
        self.forwarding = True
        self.cache = cache.Cache(num_lines=16, block_size=8)
        self.device = moduloEntradaySalida.Device()
        self.handling_interrupt = False
        self.saved_PC = None
        self.stall_count = 0
        self.cycle_count = 0
        self.interrupt_count = 0

    def get_operand_value(self, operand):
        if isinstance(operand, str) and operand.startswith('R'):
            return self.registers[operand]
        return operand

    def fetch(self):
        if self.stall:
            return  # no buscar nueva instrucción si hay stall
        if self.registers['PC'] < len(self.program):
            self.IF_stage = self.program[self.registers['PC']]
            self.registers['PC'] += 1
        else:
            self.IF_stage = None

    def decode(self):
        if self.stall:
            self.stall_count += 1
            self.stall = False
            self.ID_stage = None
            return

        instruction = self.IF_stage
        if not instruction:
            self.ID_stage = None
            return

        opcode = instruction['opcode']
        operands = instruction['operands']

        if opcode in ['JMP', 'JZ', 'JNZ', 'JE']:
            take_branch = False
            target = operands[0]
            if opcode == 'JMP':
                take_branch = True
            elif opcode == 'JZ' or opcode == 'JE':
                take_branch = (self.registers['Z'] == 1)
            elif opcode == 'JNZ':
                take_branch = (self.registers['Z'] == 0)

            if take_branch:
                self.registers['PC'] = target
                self.IF_stage = None
                self.ID_stage = None
                self.EX_stage = None
                return
            else:
                self.ID_stage = None
                return

        decoded = {
            'opcode': opcode,
            'operands': operands,
            'dest_reg': None,
            'src_regs': [],
            'resolved_operands': []
        }

        # Manejo de instrucciones según su tipo
        if opcode in ['ADD', 'SUB', 'MUL', 'SHL', 'AND']:
            decoded['dest_reg'] = operands[0]
            decoded['resolved_operands'].append(operands[0])
            for i in range(1, len(operands)):
                op = operands[i]
                if isinstance(op, str) and op.startswith('R'):
                    decoded['src_regs'].append(op)
                    val = None
                    # Forwarding desde WB
                    if self.WB_stage and self.WB_stage.get('dest_reg') == op:
                        val = self.WB_stage.get('result')
                    # Forwarding desde MEM
                    elif self.MEM_stage and self.MEM_stage.get('dest_reg') == op:
                        val = self.MEM_stage.get('result')
                    # Forwarding desde EX (excepto para LOAD)
                    elif self.EX_stage and self.EX_stage.get('dest_reg') == op and self.EX_stage['opcode'] != 'LOAD':
                        val = self.EX_stage.get('result')
                    # Si no hay forwarding, usar valor del registro
                    if val is None:
                        val = self.registers[op]
                    decoded['resolved_operands'].append(val)
                else:
                    decoded['resolved_operands'].append(op)
        elif opcode == 'LOAD':
            decoded['dest_reg'] = operands[0]
            decoded['resolved_operands'].append(operands[0])
            if len(operands) > 1:
                op = operands[1]
                if isinstance(op, str) and op.startswith('R'):
                    decoded['src_regs'].append(op)
                    val = None
                    if self.WB_stage and self.WB_stage.get('dest_reg') == op:
                        val = self.WB_stage.get('result')
                    elif self.MEM_stage and self.MEM_stage.get('dest_reg') == op:
                        val = self.MEM_stage.get('result')
                    elif self.EX_stage and self.EX_stage.get('dest_reg') == op and self.EX_stage['opcode'] != 'LOAD':
                        val = self.EX_stage.get('result')
                    if val is None:
                        val = self.registers[op]
                    decoded['resolved_operands'].append(val)
                else:
                    decoded['resolved_operands'].append(op)
        elif opcode == 'MOV':
            decoded['dest_reg'] = operands[0]
            decoded['resolved_operands'].append(operands[0])
            if len(operands) > 1:
                op = operands[1]
                if isinstance(op, str) and op.startswith('R'):
                    decoded['src_regs'].append(op)
                    val = None
                    if self.WB_stage and self.WB_stage.get('dest_reg') == op:
                        val = self.WB_stage.get('result')
                    elif self.MEM_stage and self.MEM_stage.get('dest_reg') == op:
                        val = self.MEM_stage.get('result')
                    elif self.EX_stage and self.EX_stage.get('dest_reg') == op and self.EX_stage['opcode'] != 'LOAD':
                        val = self.EX_stage.get('result')
                    if val is None:
                        val = self.registers[op]
                    decoded['resolved_operands'].append(val)
                else:
                    decoded['resolved_operands'].append(op)

        elif opcode == 'STORE':
            for i in range(len(operands)):
                op = operands[i]
                if isinstance(op, str) and op.startswith('R'):
                    decoded['src_regs'].append(op)
                    val = None
                    if self.WB_stage and self.WB_stage.get('dest_reg') == op:
                        val = self.WB_stage.get('result')
                    elif self.MEM_stage and self.MEM_stage.get('dest_reg') == op:
                        val = self.MEM_stage.get('result')
                    elif self.EX_stage and self.EX_stage.get('dest_reg') == op and self.EX_stage['opcode'] != 'LOAD':
                        val = self.EX_stage.get('result')
                    if val is None:
                        val = self.registers[op]
                    decoded['resolved_operands'].append(val)
                else:
                    decoded['resolved_operands'].append(op)

        # Verificar load-use hazard
        hazard = False
        for src_reg in decoded['src_regs']:
            if self.EX_stage and self.EX_stage.get('dest_reg') == src_reg and self.EX_stage['opcode'] == 'LOAD':
                hazard = True
                break

            if self.MEM_stage and self.MEM_stage.get('dest_reg') == src_reg and self.MEM_stage['opcode'] == 'LOAD':
                # Forwarding desde MEM para LOAD
                decoded['resolved_operands'] = [decoded['resolved_operands'][0]] + [self.MEM_stage.get('result') if reg == src_reg else val for reg, val in zip(decoded['src_regs'], decoded['resolved_operands'][1:])]

        if hazard:
            self.stall = True
            self.stall_count += 1
            self.registers['PC'] -= 1
            self.ID_stage = None
            return

        self.ID_stage = decoded

    def execute(self):
        if not self.ID_stage:
            self.EX_stage = None
            return

        instruction = self.ID_stage
        op = instruction['opcode']
        result = None

        if op in ['ADD', 'SUB', 'MUL']:
            op1 = instruction['resolved_operands'][1]
            op2 = instruction['resolved_operands'][2]
            if isinstance(op1, str) and op1.startswith('R'):
                op1 = self.registers[op1]
            if isinstance(op2, str) and op2.startswith('R'):
                op2 = self.registers[op2]
            if op == 'ADD':
                result = op1 + op2
            elif op == 'SUB':
                result = op1 - op2
            elif op == 'MUL':
                result = op1 * op2
            self.registers['Z'] = 1 if result == 0 else 0
        elif op == 'LOAD':
            address = instruction['resolved_operands'][1]
            if isinstance(address, str) and address.startswith('R'):
                address = self.registers[address]
            result = address
        elif op == 'STORE':
            value = instruction['resolved_operands'][0]
            address = instruction['resolved_operands'][1]
            if isinstance(address, str) and address.startswith('R'):
                address = self.registers[address]
            result = address
        elif op == 'MOV':
            if len(instruction['resolved_operands']) > 1:
                val = instruction['resolved_operands'][1]
                if isinstance(val, str) and val.startswith('R'):
                    val = self.registers[val]
                result = val
            else:
                result = 0
        elif op == 'SHL':
            val = instruction['resolved_operands'][1]
            shift = instruction['resolved_operands'][2]
            if isinstance(val, str) and val.startswith('R'):
                val = self.registers[val]
            if isinstance(shift, str) and shift.startswith('R'):
                shift = self.registers[shift]
            result = val << shift
        elif op == 'AND':
            val1 = instruction['resolved_operands'][1]
            val2 = instruction['resolved_operands'][2]
            if isinstance(val1, str) and val1.startswith('R'):
                val1 = self.registers[val1]
            if isinstance(val2, str) and val2.startswith('R'):
                val2 = self.registers[val2]
            result = val1 & val2
        elif op == 'CMP':
            val1 = instruction['resolved_operands'][0]
            val2 = instruction['resolved_operands'][1]
            if isinstance(val1, str) and val1.startswith('R'):
                val1 = self.registers[val1]
            if isinstance(val2, str) and val2.startswith('R'):
                val2 = self.registers[val2]
            self.registers['Z'] = 1 if val1 == val2 else 0
            result = None

        self.EX_stage = {
            'opcode': op,
            'dest_reg': instruction['dest_reg'],
            'result': result,
            'operands': instruction['operands']
        }

    def memory_access(self):
        if not self.EX_stage:
            self.MEM_stage = None
            return

        instruction = self.EX_stage
        result = instruction['result']

        if instruction['opcode'] == 'LOAD':
            address = result
            result = self.cache.read(address, self.data_memory)
            print(f"MemoryAccess: Cargando valor {result} desde memoria en dirección {address}")
        elif instruction['opcode'] == 'STORE':
            address = result
            value = self.registers[instruction['operands'][0]]
            print(f"MemoryAccess: Almacenando valor {value} en memoria en dirección {address}")
            self.cache.write(address, value, self.data_memory)

        self.MEM_stage = {
            'opcode': instruction['opcode'],
            'dest_reg': instruction['dest_reg'],
            'result': result
        }

    def write_back(self):
        if not self.MEM_stage:
            self.WB_stage = None
            return

        instruction = self.MEM_stage
        if instruction['dest_reg'] and instruction['opcode'] != 'STORE':
            valor = instruction['result']
            reg = instruction['dest_reg']
            print(f"WriteBack: Escribiendo {valor} en registro {reg}")
            self.registers[reg] = valor

        self.WB_stage = instruction

    def check_interrupt(self):
        if self.device.data_ready and not self.handling_interrupt:
            print("Interrupción detectada!")
            self.saved_PC = self.registers['PC']
            self.registers['PC'] = 100
            self.handling_interrupt = True
            self.device.clear()
            self.interrupt_count += 1

    def interrupt_service_routine(self):
        if self.handling_interrupt:
            print("Ejecutando rutina de interrupción...")
            self.registers['R0'] = 999
            self.registers['PC'] = self.saved_PC
            self.handling_interrupt = False

    def step(self):
        self.check_interrupt()
        if self.handling_interrupt:
            self.interrupt_service_routine()
        else:
            self.write_back()
            self.memory_access()
            self.execute()
            self.decode()
            self.fetch()
        self.cycle_count += 1

    def run(self, max_cycles=100):
        self.cycle_count = 0
        self.stall_count = 0
        self.interrupt_count = 0
        self.cache.hits = 0
        self.cache.misses = 0
        self.fetch()
        while any([self.IF_stage, self.ID_stage, self.EX_stage, self.MEM_stage, self.WB_stage]) or self.device.data_ready:
            print(f"\nCiclo {self.cycle_count}:")
            self.step()
            self.print_pipeline_state()

        metrics = {
            'cycles': self.cycle_count,
            'stalls': self.stall_count,
            'cache_hits': self.cache.hits,
            'cache_misses': self.cache.misses,
            'interrupts': self.interrupt_count
        }
        print(f"Total ciclos: {metrics['cycles']}")
        print(f"Total stalls: {metrics['stalls']}")
        print(f"Cache Hits: {metrics['cache_hits']}, Cache Misses: {metrics['cache_misses']}")
        print(f"Interrupciones: {metrics['interrupts']}")
        return metrics

    def print_pipeline_state(self):
        stages = {
            'IF': self.IF_stage['opcode'] if self.IF_stage else 'NOP',
            'ID': self.ID_stage['opcode'] if self.ID_stage and isinstance(self.ID_stage, dict) else 'NOP',
            'EX': self.EX_stage['opcode'] if self.EX_stage else 'NOP',
            'MEM': self.MEM_stage['opcode'] if self.MEM_stage else 'NOP',
            'WB': self.WB_stage['opcode'] if self.WB_stage else 'NOP'
        }
        print("Pipeline:", " | ".join(f"{stage}: {val}" for stage, val in stages.items()))
        print("Registros:", self.registers)

if __name__ == "__main__":
    from Test import Benchmarks
    Benchmarks.run_all_benchmarks()