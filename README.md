# 🎉 Proyecto Final: Simulador de Arquitectura de Computadores 🎉

  
*¡Bienvenido al simulador de CPU pipeline con caché y manejo de interrupciones!*

---

## 🚀 Descripción General

Este proyecto simula un procesador pipeline con las siguientes características clave:

- **ISA básica:** instrucciones aritméticas (ADD, SUB, MUL), carga/almacenamiento (LOAD, STORE), saltos condicionales y no condicionales (JMP, JZ, JNZ).
- **Pipeline de 5 etapas:** IF, ID, EX, MEM, WB con detección y manejo de hazards (stalling y forwarding).
- **Memoria Caché:** simulación parametrizable (mapeo directo y asociativo 2-way) con políticas LRU.
- **Interfaz de Entrada/Salida:** simulación de dispositivos con interrupciones para lectura de datos.
- **Benchmarks:** pruebas para acceso secuencial, aleatorio, cómputo intensivo y manejo de interrupciones.

Este simulador está implementado en **Python**, con diseño modular y documentación clara para facilitar el aprendizaje y extensión.

---

## 📂 Descripción de Carpetas y Contenidos

### 1. `Device/` — Entrada/Salida e Interrupciones

Contiene la implementación del dispositivo simulado que genera datos y dispara interrupciones para la CPU.  
- Archivo principal: `moduloEntradaySalida.py`  
- Funciones principales:  
  - Generar datos para el dispositivo.  
  - Detectar y manejar interrupciones en el pipeline.

### 2. `cpu/` — Núcleo CPU e ISA

Contiene la simulación del procesador:  
- `isa.py`: CPU básica secuencial con instrucciones elementales.  
- `pipeline.py`: Modelo completo del pipeline de 5 etapas con forwarding, stalls, caché y manejo de interrupciones.  
- Funcionalidades destacadas:  
  - Ejecución de instrucciones aritméticas, carga/almacenamiento y saltos.  
  - Detección y resolución de hazards.  
  - Control y ejecución de interrupciones.  

### 3. `memoria/` — Memoria Caché

Implementa la memoria caché con:  
- Clases para líneas y sets de caché.  
- Políticas LRU para reemplazo.  
- Soporte para lectura y escritura con write-through.  
- Archivo principal: `cache.py`.

### 4. `tests/` — Benchmarks y Pruebas

Contiene programas y scripts para evaluar el simulador, como:  
- Acceso secuencial a memoria.  
- Acceso aleatorio a memoria.  
- Cómputo intensivo en registros.  
- Simulación de interrupciones.  
Estos benchmarks permiten medir ciclos, stalls, hits/misses de caché y manejo de interrupciones.

---

## 📦 Detalle de cada Módulo

### 1. `isa.py` — CPU Básica

- **Descripción:** Simula una CPU con registros, memoria de datos (256 posiciones) y ejecución paso a paso de un programa en ISA básica.
- **Funciones Clave:**
  - `execute_arithmetic(op, operands)`: ejecuta instrucciones ADD, SUB, MUL.
  - `execute_load(operands)`, `execute_store(operands)`: carga y almacena datos en memoria.
  - `execute_jump(op, operands)`: salta a otra instrucción según condiciones.
  - `step()`: ejecuta una instrucción.
  - `run()`: ejecuta el programa completo.
- **Cómo usar:**  
  Definir un programa como lista de instrucciones (diccionarios con `'opcode'` y `'operands'`), crear instancia `CPU(program)` y llamar `run()`.  

---

### 2. `cache.py` — Simulación de Caché

- **Descripción:** Modelo de caché con líneas, bloques, sets y asociatividad configurable (directo o 2-way).
- **Características:**
  - Lectura y escritura con política write-through.
  - Manejo de hits y misses con contador LRU para reemplazo.
- **Clases principales:**
  - `CacheLine`: línea individual con `valid`, `tag` y `data`.
  - `Cache`: controlador general de caché que administra sets y líneas.
- **Cómo usar:**  
  Crear instancia `Cache(num_lines, block_size, associativity)`. Usar `read(address, main_memory)` y `write(address, value, main_memory)` para acceder a memoria caché.

---

### 3. `moduloEntradaySalida.py` — Dispositivo de Entrada/Salida e Interrupciones

- **Descripción:** Simula un dispositivo que genera datos y puede disparar una interrupción para la CPU.
- **Clase principal:** `Device`
  - `generate_data(value)`: marca el dispositivo con datos listos.
  - `clear()`: limpia la señal de interrupción.
- **Funcionalidad de interrupción:**  
  El pipeline detecta si `device.data_ready` y activa la rutina de interrupción, guardando el estado del PC y ejecutando la rutina correspondiente.

---

### 4. `pipeline.py` — Simulación Pipeline Completa

- **Descripción:** Modelo completo de CPU pipeline con las 5 etapas clásicas y soporte para hazards y forwarding.
- **Componentes:**
  - Registros: R0 - R5, PC, Flag Z.
  - Etapas del pipeline: IF, ID, EX, MEM, WB.
  - Cache integrada para acceso a memoria.
  - Detección de stalls por hazards y manejo de forwarding.
  - Manejo de interrupciones con rutina y restablecimiento.
- **Funciones importantes:**
  - `fetch()`, `decode()`, `execute()`, `memory_access()`, `write_back()`: ciclo completo pipeline.
  - `check_interrupt()`, `interrupt_service_routine()`: gestión de interrupciones.
  - `step()`, `run()`: para avanzar ciclo a ciclo o ejecutar programa completo.
- **Benchmarks incluidos:**  
  Programas para probar acceso secuencial, aleatorio, intensivo en registros y manejo de interrupciones.
- **Cómo ejecutar:**  
  Ejecutar directamente el archivo `pipeline.py`. Los benchmarks se ejecutan automáticamente y muestran métricas y estados del pipeline.

---

## ⚙️ Cómo Ejecutar el Proyecto

1. **Requisitos:**
   - Python 3.7 o superior.
   - No requiere librerías externas.

2. **Ejecución básica:**

   - Para probar la CPU básica:
     ```bash
     python isa.py
     ```

   - Para probar el pipeline completo con caché y dispositivos:
     ```bash
     python pipeline.py
     ```

3. **Personalización:**

   - Puedes modificar los programas en `isa.py` y `pipeline.py` para probar nuevas instrucciones.
   - Ajusta parámetros de caché en `pipeline.py` al crear la instancia `Cache`.
   - Modifica el dispositivo de entrada/salida en `moduloEntradaySalida.py` para simular interrupciones.

---

## 📊 Métricas y Resultados

El simulador muestra en consola:

- Número de ciclos totales ejecutados.
- Cantidad de stalls por hazards.
- Hits y misses de caché.
- Número de interrupciones atendidas.
- Estado de registros en cada ciclo del pipeline.

Esto permite evaluar y comparar rendimiento bajo diferentes condiciones y configuraciones.

---

## 💡 Explicación de Conceptos Clave

| Concepto            | Explicación Breve                                                      |
|---------------------|-----------------------------------------------------------------------|
| Pipeline            | Ejecución simultánea de instrucciones dividida en etapas para mejorar rendimiento. |
| Hazard              | Situación que puede causar error o retraso en pipeline (datos o control). |
| Forwarding          | Técnica para evitar stalls pasando resultados directamente entre etapas. |
| Caché               | Memoria rápida que almacena bloques de datos para acelerar accesos frecuentes. |
| Interrupción        | Evento que detiene temporalmente la CPU para atender un dispositivo externo. |

---

## 🎯 Objetivos del Proyecto

- Aplicar conceptos de jerarquía de memoria y organización de procesadores.
- Implementar pipeline con detección y resolución de hazards.
- Simular memoria caché con diferentes configuraciones.
- Gestionar I/O con interrupciones.
- Medir desempeño con benchmarks variados.

---

# ¡Disfruta explorando la arquitectura de computadores con este simulador! ⚙️💻✨
