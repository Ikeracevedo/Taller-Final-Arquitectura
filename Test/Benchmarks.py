import random
from cpu.pipeline import PipelinedCPU

def benchmark_secuencial():
    print("\n=== Benchmark 1: Acceso Secuencial a Memoria ===")
    program_seq = [
        {'opcode': 'MOV', 'operands': ['R1', 1]},
        {'opcode': 'MOV', 'operands': ['R2', 0]},
        {'opcode': 'MOV', 'operands': ['R3', 0]}
    ]
    for _ in range(10):
        program_seq.append({'opcode': 'LOAD', 'operands': ['R4', 'R3']})
        program_seq.append({'opcode': 'ADD', 'operands': ['R2', 'R2', 'R4']})
        program_seq.append({'opcode': 'ADD', 'operands': ['R3', 'R3', 'R1']})
    cpu = PipelinedCPU(program_seq)
    cpu.data_memory = list(range(100))
    metrics = cpu.run()
    print(f"Resultado acumulado: {cpu.registers['R2']} (Esperado: {sum(range(10))})")
    print_metrics(metrics)

def benchmark_aleatorio():
    print("\n=== Benchmark 2: Acceso Aleatorio a Memoria ===")
    program_rand = [{'opcode': 'MOV', 'operands': ['R2', 0]}]
    random.seed(42)
    addresses = [random.randint(0, 99) for _ in range(10)]
    expected_sum = sum(addresses)
    for addr in addresses:
        program_rand.append({'opcode': 'LOAD', 'operands': ['R4', addr]})
        program_rand.append({'opcode': 'ADD', 'operands': ['R2', 'R2', 'R4']})
    cpu = PipelinedCPU(program_rand)
    cpu.data_memory = list(range(100))
    metrics = cpu.run()
    print(f"Resultado acumulado acceso aleatorio: {cpu.registers['R2']} (Esperado: {expected_sum})")
    print_metrics(metrics)

def benchmark_hazard():
    print("\n=== Benchmark 3: Carga y Uso Intensivo de Registros ===")
    program_hazard = [
        {'opcode': 'MOV', 'operands': ['R1', 5]},
        {'opcode': 'MOV', 'operands': ['R2', 10]},
        {'opcode': 'ADD', 'operands': ['R3', 'R1', 'R2']},
        {'opcode': 'SUB', 'operands': ['R4', 'R3', 'R1']},
        {'opcode': 'MUL', 'operands': ['R5', 'R4', 'R2']}
    ]
    cpu = PipelinedCPU(program_hazard)
    metrics = cpu.run()
    print(f"Resultado R5: {cpu.registers['R5']} (Esperado: 100)")
    print_metrics(metrics)

def benchmark_interrupciones():
    print("\n=== Benchmark 4: Manejo de Interrupciones ===")
    program_interrupt = [
        {'opcode': 'MOV', 'operands': ['R1', 1]},
        {'opcode': 'MOV', 'operands': ['R2', 2]},
        {'opcode': 'ADD', 'operands': ['R3', 'R1', 'R2']},
        {'opcode': 'NOP', 'operands': []}
    ]
    cpu = PipelinedCPU(program_interrupt)
    metrics = cpu.run()
    cpu.device.generate_data(42)
    metrics_interrupt = cpu.run()
    # Sumar métricas de ambas ejecuciones
    for key in metrics:
        if key in metrics_interrupt:
            metrics[key] += metrics_interrupt[key]
    print(f"Registro R0 (debe ser 999 si se atendió interrupción): {cpu.registers['R0']}")
    print_metrics(metrics)

def print_metrics(metrics):
    print(f"Métricas:")
    print(f"  Ciclos: {metrics['cycles']}")
    print(f"  Stalls: {metrics['stalls']}")
    print(f"  Cache Hits: {metrics['cache_hits']}")
    print(f"  Cache Misses: {metrics['cache_misses']}")
    print(f"  Interrupciones: {metrics['interrupts']}")

def run_all_benchmarks():
    benchmark_secuencial()
    benchmark_aleatorio()
    benchmark_hazard()
    benchmark_interrupciones()

if __name__ == "__main__":
    run_all_benchmarks()