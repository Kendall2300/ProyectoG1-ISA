# SecureRISC - Arquitectura RISC con Extensiones de Seguridad

[![ISA Version](https://img.shields.io/badge/ISA-v1.0-blue.svg)](docs/isa.md)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)](LICENSE)

**Proyecto Grupal #1 - Arquitectura de Computadores I**  
Instituto Tecnológico de Costa Rica  
Escuela de Ingeniería en Computadores

---

## Tabla de Contenidos

- [Descripción](#-descripción)
- [Características Principales](#-características-principales)
- [Estructura del Repositorio](#-estructura-del-repositorio)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Ejemplos](#-ejemplos)
- [Documentación](#-documentación)
- [Desarrollo](#-desarrollo)
- [Equipo](#-equipo)
- [Referencias](#-referencias)

---

## Descripción

**SecureRISC** es una arquitectura del set de instrucciones (ISA) RISC de 64 bits diseñada específicamente para aplicaciones de seguridad de la información. La arquitectura provee soporte nativo en hardware para:

- **Función hash criptográfica ToyMDMA** - Procesamiento acelerado por hardware (50x speedup)
- **Almacenamiento seguro de llaves privadas** - Bóveda aislada (Root of Trust)
- **Operaciones de firma y verificación digital** - Instrucciones nativas VSIGN/VVERIF
- **Pipeline eficiente de 5 etapas** - IF-ID-EX-MEM-WB clásico RISC

Este proyecto incluye:
1. **Especificación completa de la ISA** con justificaciones cuantitativas
2. **Ensamblador funcional** que traduce assembly a código máquina
3. **Simulador del CPU** que ejecuta programas SecureRISC
4. **Implementación de firma digital** usando ToyMDMA y la bóveda segura

---

## Características Principales

### Arquitectura

| Característica | Valor | Justificación |
|---------------|-------|---------------|
| **Ancho de palabra** | 64 bits | Procesamiento eficiente de bloques criptográficos |
| **Tamaño de instrucción** | 32 bits (fijo) | Decodificación simple, fetch predecible |
| **Registros GPR** | 32 × 64 bits | Reduce spills (~5%), área aceptable |
| **Pipeline** | 5 etapas | Balance clásico RISC (CPI ~1.2 @ 800 MHz) |
| **Bóveda segura** | 8 slots × 64 bits | 4 llaves privadas + 4 valores init hash |

### Set de Instrucciones

- **~42 instrucciones** organizadas en 7 categorías
- **6 formatos** de instrucción (R, I, S, B, J, V)
- **Instrucciones especiales de seguridad:**
  - `HBLOCK` - Procesa bloque de hash en 1 ciclo
  - `VSIGN` - Genera firma digital
  - `VVERIF` - Verifica firma digital
  - `VSTORE` - Almacena en bóveda segura
  - `VINIT` - Inicializa estado de hash

### Seguridad

- **Bóveda aislada**: Las llaves privadas NO pueden leerse desde software
- **Root of Trust**: Almacenamiento seguro independiente de la memoria principal
- **Hash acelerado**: HBLOCK procesa 64 bits en 1 ciclo (vs 50 ciclos en software)
- **Firma nativa**: Operaciones XOR optimizadas con acceso directo a la bóveda

---

## Estructura del Repositorio

```
SecureRISC/
├── README.md                   # Este archivo
├── LICENSE                     # Licencia del proyecto
├── .gitignore                  # Archivos ignorados por Git
├── requirements.txt            # Dependencias Python
├── requirements-dev.txt        # Dependencias de desarrollo
│
├── docs/                       # Documentación
│   ├── ISA.md                 # Especificación completa de la ISA
│   ├── ENCODING.md            # Referencia de codificación binaria
│   ├── green_card.html        # Hoja de referencia rápida
│   ├── green_card.pdf         # Green Card en PDF
│   ├── CPU_MODEL.md           # Documentación del simulador
│   ├── ASSEMBLER.md           # Guía del ensamblador
│   ├── USER_MANUAL.md         # Manual de usuario
│   ├── VALIDATION.md          # Reporte de validación
│   ├── diagrams/              # Diagramas de arquitectura
│   │   ├── isa_overview.png
│   │   ├── pipeline.png
│   │   ├── microarchitecture.png
│   │   └── security_arch.png
│   └── analysis/              # Gráficas de análisis
│       ├── instruction_width_analysis.png
│       ├── register_count_analysis.png
│       ├── hash_instruction_analysis.png
│       ├── vault_security_analysis.png
│       ├── pipeline_analysis.png
│       └── addressing_modes_analysis.png
│
├── src/                       # Código fuente
│   ├── __init__.py
│   ├── assembler.py           # Ensamblador SecureRISC
│   ├── cpu.py                 # Simulador del CPU
│   ├── memory.py              # Sistema de memoria
│   ├── registers.py           # Banco de registros
│   ├── vault.py               # Bóveda segura
│   ├── alu.py                 # Unidad aritmético-lógica
│   ├── hash_unit.py           # Unidad ToyMDMA
│   ├── pipeline.py            # Pipeline del CPU
│   └── utils.py               # Utilidades
│
├── examples/                  # Programas de ejemplo
│   ├── hello_world.asm        # Programa simple
│   ├── digital_signature.asm  # Firma digital completa
│   ├── signature_verify.asm   # Verificación de firma
│   ├── hash_calculation.asm   # Cálculo de hash ToyMDMA
│   ├── test_all_instructions.asm  # Test completo
│   └── function_calls.asm     # Llamadas a función
│
├── tests/                     # Tests
│   ├── __init__.py
│   ├── test_assembler.py      # Tests del ensamblador
│   ├── test_cpu.py            # Tests del CPU
│   ├── test_instructions.py   # Tests de instrucciones
│   ├── test_hash.py           # Tests de ToyMDMA
│   ├── test_vault.py          # Tests de bóveda
│   └── integration/           # Tests de integración
│       ├── test_signature.py
│       └── test_full_system.py
│
├── scripts/                   # Scripts de utilidad
│   ├── isa_analysis.py        # Análisis de características ISA
│   ├── run_tests.sh           # Ejecutar todos los tests
│   └── benchmark.py           # Benchmarks de rendimiento
│
├── test_files/                # Archivos de prueba
│   ├── input/                 # Archivos para firmar
│   │   ├── test1.txt
│   │   ├── test2.bin
│   │   └── mensaje.txt
│   ├── signed/                # Archivos firmados
│   │   ├── test1_signed.txt
│   │   └── test2_signed.bin
│   └── results/               # Resultados de validación
│       ├── validation_report.txt
│       └── metrics.json
│
└── presentation/              # Materiales de presentación
    ├── slides.pdf            # Presentación
    └── demo_script.md        # Script de demostración
```

---

## Requisitos

### Software Necesario

- **Python 3.8 o superior** ([Descargar](https://www.python.org/downloads/))
- **pip** (gestor de paquetes de Python, incluido con Python)
- **Git** (para clonar el repositorio) ([Descargar](https://git-scm.com/))


### Verificar Requisitos

```bash
# Verificar Python
python --version    # Debe ser 3.8+

# Verificar pip
pip --version

# Verificar Git
git --version
```

---

## Instalación

### Instalación Completa 

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/SecureRISC.git
cd SecureRISC

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv

# 3. Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Verificar instalación
python src/assembler.py --version
python scripts/isa_analysis.py --help
```

---

## Ejemplos

### Ejemplo 1: Programa Simple - Suma de Números

**Archivo:** `examples/simple_add.asm`

```assembly
# ==========================================
# Programa simple: suma dos números
# ==========================================

    ADDI R1, R0, 10        # R1 = 10
    ADDI R2, R0, 20        # R2 = 20
    ADD  R3, R1, R2        # R3 = R1 + R2 = 30
    
    # Guardar resultado en memoria
    LUI  R10, 0x3000       # R10 = dirección base
    SD   R3, 0(R10)        # MEM[0x3000] = 30
    
    HALT                   # Detener
```

**Ejecutar:**
```bash
python src/assembler.py examples/simple_add.asm -o add.bin --dump
python src/cpu.py add.bin --debug --dump-registers
```

**Salida esperada:**
```
Ensamblado:
  0x0000: 0x0C01000A  ADDI R1, R0, 10
  0x0004: 0x0C020014  ADDI R2, R0, 20
  0x0008: 0x00422000  ADD  R3, R1, R2
  0x000C: 0x0C0A3000  LUI  R10, 0x3000
  0x0010: 0x15430000  SD   R3, 0(R10)
  0x0014: 0xFC000001  HALT

Ejecución:
  [Ciclo 1-3]  R1 ← 10
  [Ciclo 4-6]  R2 ← 20
  [Ciclo 7-9]  R3 ← 30
  [Ciclo 10-12] R10 ← 0x3000...
  [Ciclo 13-15] MEM[0x3000] ← 30
  [Ciclo 16] HALT

Registros finales:
  R1  = 0x000000000000000A (10)
  R2  = 0x0000000000000014 (20)
  R3  = 0x000000000000001E (30)
  R10 = 0x3000000000000000

Memoria 0x3000: 0x000000000000001E
```

### Ejemplo 2: Firma Digital Completa

**Archivo:** `examples/digital_signature.asm`

```assembly
# ==========================================
# Firma Digital con SecureRISC
# ==========================================

# 1. Cargar llave privada en bóveda
    LUI    R1, 0x1234           # Llave privada (parte alta)
    VSTORE 0, R1                # Guardar en VAULT[0]

# 2. Cargar valores iniciales de hash (A, B, C, D)
    LUI    R2, 0x6745           # Valor inicial A
    VSTORE 4, R2                # INIT[0] = A
    
    LUI    R3, 0x23C1           # Valor inicial B
    VSTORE 5, R3                # INIT[1] = B
    
    LUI    R4, 0xEFCD           # Valor inicial C
    VSTORE 6, R4                # INIT[2] = C
    
    LUI    R5, 0xAB89           # Valor inicial D
    VSTORE 7, R5                # INIT[3] = D

# 3. Inicializar estado de hash
    VINIT  0                    # Cargar INIT[0-3] → HS_A,B,C,D

# 4. Configurar procesamiento del archivo
    LUI    R10, 0x2000          # R10 = dirección base del archivo
    ADDI   R11, R0, 16          # R11 = número de bloques (16 × 8 bytes = 128 bytes)

# 5. Loop de procesamiento de hash
hash_loop:
    LD     R1, 0(R10)           # Cargar bloque de 64 bits
    HBLOCK R1                   # Procesar con ToyMDMA (1 ciclo!)
    ADDI   R10, R10, 8          # Avanzar al siguiente bloque
    SUBI   R11, R11, 1          # Decrementar contador
    BNE    R11, R0, hash_loop   # Continuar si quedan bloques

# 6. Generar firma digital
    VSIGN  R4, 0                # Firma en R4-R7 usando VAULT[0]
                                # R4 = HS_A XOR VAULT[0]
                                # R5 = HS_B XOR VAULT[0]
                                # R6 = HS_C XOR VAULT[0]
                                # R7 = HS_D XOR VAULT[0]

# 7. Guardar firma al final del archivo
    SD     R4, 0(R10)           # Guardar primeros 64 bits de firma
    SD     R5, 8(R10)           # Guardar segundos 64 bits
    SD     R6, 16(R10)          # Guardar terceros 64 bits
    SD     R7, 24(R10)          # Guardar últimos 64 bits

# 8. Finalizar
    HALT                        # Detener ejecución
```

**Preparar y ejecutar:**
```bash
# 1. Crear archivo de prueba
echo "Este es un mensaje secreto para firmar" > test_files/input/mensaje.txt

# 2. Ensamblar programa
python src/assembler.py examples/digital_signature.asm \
    -o signature.bin \
    --verbose \
    --dump

# 3. Ejecutar (el simulador carga el archivo en 0x2000)
python src/cpu.py signature.bin \
    --load test_files/input/mensaje.txt@0x2000 \
    --metrics \
    --dump-memory 0x2000:0x2100 \
    --dump-registers
```

**Salida esperada:**
```
Cargando archivo: test_files/input/mensaje.txt → 0x2000 (40 bytes)
Padding a múltiplo de 8 bytes: 40 → 128 bytes (16 bloques)

Ejecutando...
[Ciclo 1-15]   Inicialización de bóveda
[Ciclo 16]     VINIT: Estado hash inicializado
[Ciclo 17-20]  Configuración de loop
[Ciclo 21]     Hash loop inicio
[Ciclo 22]     LD R1 ← bloque 1
[Ciclo 23]     HBLOCK: bloque 1 procesado ← 1 ciclo!
[...]
[Ciclo 150]    Hash loop completado (16 bloques)
[Ciclo 151]    VSIGN: Firma generada
[Ciclo 152-155] Guardar firma en memoria
[Ciclo 156]    HALT

Métricas:
  Ciclos totales:        156
  Instrucciones:         129
  CPI:                   1.21
  Bloques hash:          16
  Ciclos/bloque:         1  ← Aceleración!

Memoria 0x2080-0x2100 (Firma):
  0x2080: A3 B4 C5 D6 E7 F8 09 1A  ← R4 (HS_A XOR llave)
  0x2088: 1B 2C 3D 4E 5F 60 71 82  ← R5 (HS_B XOR llave)
  0x2090: 93 A4 B5 C6 D7 E8 F9 0A  ← R6 (HS_C XOR llave)
  0x2098: 0B 1C 2D 3E 4F 50 61 72  ← R7 (HS_D XOR llave)

Firma generada exitosamente: 32 bytes al final del archivo
```

### Ejemplo 3: Verificación de Firma

**Archivo:** `examples/signature_verify.asm`

```assembly
# ==========================================
# Verificación de Firma Digital
# ==========================================

# 1. Cargar la misma llave privada
    LUI    R1, 0x1234
    VSTORE 0, R1

# 2. Cargar mismos valores iniciales
    LUI    R2, 0x6745
    VSTORE 4, R2
    LUI    R3, 0x23C1
    VSTORE 5, R3
    LUI    R4, 0xEFCD
    VSTORE 6, R4
    LUI    R5, 0xAB89
    VSTORE 7, R5

# 3. Recalcular hash del archivo original
    VINIT  0
    LUI    R10, 0x2000
    ADDI   R11, R0, 16

verify_loop:
    LD     R1, 0(R10)
    HBLOCK R1
    ADDI   R10, R10, 8
    SUBI   R11, R11, 1
    BNE    R11, R0, verify_loop

# 4. Extraer hash recalculado
    HFINAL R12                  # Hash en R12-R15

# 5. Cargar firma almacenada
    LD     R8, 0(R10)           # Firma en R8-R11
    LD     R9, 8(R10)
    LD     R10, 16(R10)
    LD     R11, 24(R10)

# 6. Recuperar hash de la firma
    VVERIF R8, 0                # HS ← firma XOR VAULT[0]

# 7. Extraer hash recuperado
    HFINAL R16                  # Hash recuperado en R16-R19

# 8. Comparar hashes (R12-R15 vs R16-R19)
    XOR    R20, R12, R16        # Diferencias en R20-R23
    XOR    R21, R13, R17
    XOR    R22, R14, R18
    XOR    R23, R15, R19
    
    OR     R24, R20, R21        # Si alguno != 0, firma inválida
    OR     R24, R24, R22
    OR     R24, R24, R23
    
    BEQ    R24, R0, valid       # Si R24 == 0, firma válida

invalid:
    ADDI   R1, R0, 0            # R1 = 0 (inválido)
    HALT

valid:
    ADDI   R1, R0, 1            # R1 = 1 (válido)
    HALT
```

**Ejecutar:**
```bash
python src/assembler.py examples/signature_verify.asm -o verify.bin
python src/cpu.py verify.bin \
    --load test_files/signed/mensaje_signed.txt@0x2000 \
    --metrics

# Verificar resultado
echo "Resultado de verificación: R1 = 1 significa firma válida"
```

### Ejemplo 4: Abrir la Green Card

```bash
# Navegador (Linux)
xdg-open docs/green_card.html

# Navegador (Mac)
open docs/green_card.html

# Navegador (Windows)
start docs/green_card.html

# PDF
xdg-open docs/green_card.pdf
```

---

## Documentación

### Documentos Principales

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **ISA Specification** | Especificación completa de la ISA con justificaciones | [`docs/ISA.md`](docs/isa.md) |
| **Green Card** | Hoja de referencia rápida (HTML/PDF) | [`docs/green_card.html`](docs/green_card.html) |
| **Diagrama de Arquitectura** | Diagrama de arquitectura desarrollada | [`docs/diagrama.png`](docs/diagrama.png) |
| **CPU Model** | Documentación del simulador | [`docs/CPU_MODEL.md`](docs/CPU_MODEL.md) |
| **User Manual** | Manual de usuario completo | [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) |

### Características de la ISA

#### Registros

- **R0-R31**: 32 registros de propósito general (64 bits)
  - R0: Siempre 0 (hardwired)
  - R1: Valor de retorno
  - R2-R7: Argumentos
  - R8-R15: Temporales (caller-saved)
  - R16-R23: Salvados (callee-saved)
  - R24-R28: Temporales adicionales
  - R29: Frame pointer (FP)
  - R30: Stack pointer (SP)
  - R31: Link register (LR)

- **Registros especiales**: PC (64 bits), FLAGS (8 bits: Z, N, C, V)

- **Bóveda (aislada del espacio de memoria)**: 
  - VAULT[0-3]: 4 llaves privadas de 64 bits
  - INIT[0-3]: 4 valores iniciales de hash (A, B, C, D)

- **Estado interno de hash**: HS_A, HS_B, HS_C, HS_D (no visibles directamente)

#### Formatos de Instrucción (32 bits fijos)

- **R**: Registro-Registro (ADD, SUB, MUL, AND, OR, XOR, SLL, SRL, ROL, ROR)
- **I**: Inmediato (ADDI, SUBI, LUI, LD)
- **S**: Store (SD)
- **B**: Branch (BEQ, BNE, BLT, BGE)
- **J**: Jump (J, JAL)
- **V**: Vault/Security (VSTORE, VINIT, HBLOCK, HMULK, HMODP, HFINAL, VSIGN, VVERIF)

#### Instrucciones por Categoría

| Categoría | Cantidad | Ejemplos |
|-----------|----------|----------|
| **Aritméticas** | 5 | ADD, SUB, MUL, DIV, MOD |
| **Lógicas** | 4 | AND, OR, XOR, NOT |
| **Shift/Rotate** | 4 | SLL, SRL, ROL, ROR |
| **Inmediato** | 7 | ADDI, SUBI, LUI, ANDI, ORI, XORI, SLLI |
| **Memoria** | 2 | LD, SD |
| **Control** | 7 | BEQ, BNE, BLT, BGE, J, JAL, JR |
| **Seguridad** | 9 | VSTORE, VINIT, HBLOCK, HMULK, HMODP, HFINAL, VSIGN, VVERIF |
| **Sistema** | 2 | NOP, HALT |

**Total: ~42 instrucciones**

### Diferenciación de Instrucciones

SecureRISC usa tres estrategias para diferenciar instrucciones:

#### 1. Campo `funct` (Tipos R y V)
Instrucciones con el mismo opcode se diferencian por el campo `funct`:

**Ejemplo - Opcode 0x00 (Aritméticas):**
- ADD: funct = 0x00
- SUB: funct = 0x01
- MUL: funct = 0x02
- DIV: funct = 0x03
- MOD: funct = 0x04

#### 2. Opcodes Únicos (Tipos I, S, J)
Cada instrucción tiene su propio opcode:
- ADDI: 0x03
- LD: 0x04
- SD: 0x05
- J: 0x07
- JR: 0x08

#### 3. Bits del Offset (Branches - Tipo B)
Branches usan bits 15-14 del offset para diferenciar tipo:
- BEQ: bits[15:14] = 00
- BNE: bits[15:14] = 01
- BLT: bits[15:14] = 10
- BGE: bits[15:14] = 11

### Sintaxis Assembly

```assembly
# Comentarios empiezan con #

# Etiquetas para saltos
main:
    ADDI R1, R0, 100       # R1 = 100
    
# Instrucciones con inmediato
    LUI  R2, 0x1000        # R2 = 0x1000 << 48

# Memoria: offset(registro)
    LD   R3, 8(R10)        # R3 = MEM[R10 + 8]
    SD   R3, 16(R10)       # MEM[R10 + 16] = R3

# Branches con labels
loop:
    SUBI R1, R1, 1
    BNE  R1, R0, loop      # while (R1 != 0)

# Llamada a función
    JAL  R31, function     # R31 = PC+4; PC = function
    JR   R31               # return

# Instrucciones de seguridad
    VSTORE 0, R1           # Guardar llave en bóveda
    VINIT  0               # Inicializar hash
    HBLOCK R1              # Procesar bloque de hash
    VSIGN  R4, 0           # Generar firma
```

---

## Desarrollo

### Configurar Entorno de Desarrollo

```bash
# 1. Clonar y entrar al repositorio
git clone https://github.com/Kendall2300/ProyectoG1-ISA.git
cd ProyectoG1-ISA

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# 4. Configurar pre-commit hooks (opcional)
pre-commit install

# 5. Verificar instalación
pytest --version
black --version
pylint --version
```

---

## Equipo

### Proyecto Grupal #1 - Grupo 1

| Rol | Nombre | Email | Responsabilidad |
|-----|--------|-------|-----------------|
| **Arquitecto ISA** | Kendall Martinez Carvajal | [kendallmc@estudiantec.cr] | Diseño de la ISA, formatos, instrucciones |
| **Implementador CPU** | Andres Alfaro Mayorga | [a.alfaro@estudiantec.cr] | Simulador del CPU, pipeline |
| **Desarrollador SW** | Daniel Ureña Lopez | [dlurena24@estudiantec.cr] | Ensamblador, herramientas |
| **Especialista Seguridad** | Marco Villatoro C | [mavic@estudiantec.cr] | Bóveda, hash, firma digital |

### Información Académica

- **Curso**: CE-4301 Arquitectura de Computadores I
- **Profesor**: Dr.-Ing. Jeferson González Gómez
- **Institución**: Instituto Tecnológico de Costa Rica
- **Escuela**: Ingeniería en Computadores
- **Sede**: Sede Central Cartago
- **Período**: II Semestre 2025
- **Fecha de Entrega**: 13 de octubre de 2025

---

## Métricas del Proyecto

### Estadísticas del Código

```bash
# Contar líneas de código (requiere cloc)
cloc src/ examples/ tests/

# O manualmente
find src -name "*.py" | xargs wc -l
find examples -name "*.asm" | xargs wc -l
find tests -name "*.py" | xargs wc -l
```

### Rendimiento Estimado

| Métrica | Valor | Comparación |
|---------|-------|-------------|
| **CPI promedio** | 1.2 ciclos/instrucción | RISC típico: 1.0-1.5 |
| **Frecuencia objetivo** | 800 MHz | Realista para FPGA |
| **MIPS** | ~666 MIPS | Competitivo para embedded |
| **Hash throughput** | 800 MB/s @ 800MHz | SHA-256 SW: ~50 MB/s |
| **Speedup HBLOCK** | 50x vs software | Justifica HW especializado |
| **Ciclos por firma** | ~350 ciclos | Incluye hash + firma |
| **Latencia bóveda** | 1 ciclo | Acceso directo |

### Distribución de Área Estimada (en gates)

| Componente | % Área | Justificación |
|------------|--------|---------------|
| Banco de Registros | 30% | 32 × 64 bits |
| ALU + Hash Unit | 35% | HBLOCK más complejo |
| Control + Pipeline | 25% | Decodificador, hazards |
| Bóveda Segura | 10% | 512 bits aislados |

---

## Referencias

### Arquitectura

1. **Proyecto Especificación** - Dr.-Ing. Jeferson González Gómez, TEC, 2025
2. [**RISC-V ISA Specification**](https://riscv.org/technical/specifications/) - RISC-V International
3. [**RISC-V Bitmanip Extension**](https://github.com/riscv/riscv-bitmanip) - Incluye ROL/ROR
4. [**ARM Architecture Reference Manual**](https://developer.arm.com/documentation/) - ARM Limited
5. **Computer Organization and Design RISC-V Edition** - Patterson & Hennessy, 6th Ed.
6. **Computer Architecture: A Quantitative Approach** - Hennessy & Patterson, 6th Ed.

### Criptografía

1. [**Merkle-Damgård Construction**](https://en.wikipedia.org/wiki/Merkle%E2%80%93Damg%C3%A5rd_construction) - Ivan Bjerre Damgård, CRYPTO '89
2. **Applied Cryptography** - Bruce Schneier, 2nd Edition
3. [**SHA-256 Specification**](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf) - NIST FIPS 180-4
4. [**Digital Signature Standard (DSS)**](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf) - NIST FIPS 186-4
5. **Cryptographic Hash Functions** - Handbook of Applied Cryptography, Ch. 9

### Seguridad en Hardware

1. [**ARM TrustZone**](https://developer.arm.com/ip-products/security-ip/trustzone) - ARM Security Extension
2. [**Intel SGX**](https://www.intel.com/content/www/us/en/developer/tools/software-guard-extensions/overview.html) - Software Guard Extensions
3. [**RISC-V Physical Memory Protection**](https://github.com/riscv/riscv-tee) - PMP Specification
4. **Building Secure Systems** - Viega & McGraw

### Herramientas y Recursos

- [**Python 3 Documentation**](https://docs.python.org/3/)
- [**Git Documentation**](https://git-scm.com/doc)
- [**Markdown Guide**](https://www.markdownguide.org/)

---

## Licencia

Este proyecto es de naturaleza **académica** y está desarrollado como parte del curso CE-4301 Arquitectura de Computadores I del Instituto Tecnológico de Costa Rica.

**Uso Académico Únicamente** - No se permite uso comercial sin autorización expresa.

Copyright © 2025 

---

### Contribuciones

Este es un **proyecto académico cerrado**. Las contribuciones externas no son aceptadas durante el período del curso (hasta octubre 2025).

Después de la entrega, el proyecto puede abrirse para contribuciones educativas.

---

## Estado del Proyecto

### Progreso de Milestones

- [x] **Milestone 1**: Fase de Diseño ISA **Completado**
  - [x] Documentacion Completa y Green Card
  - [x] Diseño Base de la ISA
  - [x] Set de Instrucciones Base
  - [x] Extensiones de Seguridad
  - [x] Codificación binaria completa y Ensamblador
  - [x] isa.md documentado

- [x] **Milestone 2**: Implementación Ensamblador **Completado**
  - [x] Determinar unidades funcionales requeridas
  - [x] Diseño del diagrama con pipeline
  - [x] Hacer diseño completo del diagrama de bloques
  - [x] Hacer diseño completo del diagrama de bloques

- [x] **Milestone 3**: Implementación Ensamblador **Completado**
  - [x] Agregar soporte para instrucciones especiales de seguridad
  - [x] Agregar soporte para instrucciones de Control de flujo
  - [x] Implementar carga de .bin
  - [x] Decodificar instrucciones
  - [x] Codificar formatos R, I, S, J
  - [x] Integrar parser de Instruction.py
  - [x] Implementar lectura de archivo .asm
  - [x] Crear simulator.py
  - [x] Soporte para hexadecimales en inmediatos
  - [x] Validar con programa de prueba (test.asm)
  - [x] Generar archivo .bin
  - [x] Agregar tabla de opcodes y funct
  - [x] Agregar códigos de prueba .asm para probar caracteristicas del ISA


- [x] **Milestone 4**: Simulador del CPU **Completado**
  - [x] Implementar la Estructura Base de Memoria
  - [x] Implementar estructura de registros
  - [x] Implementar funciones de lectura y escritura para los registros VAULT, INIT y HASH_STATE
  - [x] Implementar funciones de lectura y escritura para el Program Counter (PC)
  - [x] Implementar lectura y escritura en registros de propósito general
  - [x] Mostrar los valores de los registros en la interfaz de la CPU
  - [x] Implementar la interfaz de la CPU
  - [x] Implementar funciones de lectura y escritura para el registro de Flags
  - [x] Bug de la impresion de la instrucción, offset se ve como None
  - [x] Implementar Pipeline
  - [x] Actualizar memoria de interfaz al final de la ejecución del pipeline
  - [x] Implementar ISA
  - [x] Implementar Editor de texto
  - [x] Implementar la Unidad de Control y Generación de Señales (Control Unit)
  - [x] Mostrar memoria en la UI
  - [x] Implementar la Unidad Aritmético-Lógica (ALU) y Operaciones Base
  - [x] Implementar salida de consola
  - [x] Probar funcionalidad de simulator.py

- [x] **Milestone 5**: Validación Firma Digital **Completado**
  - [x] Cargar archivos de prueba
  - [x] Probar con múltiples archivos y llaves
  - [x] Validar contra implementación de referencia del profesor
  - [x] Verificar firmas correcta
  - [x] Generar firmas correctas con ToyMDMA
  - [x] Implementar programa de verificación de firma digital 
  - [x] Implementar programa de firma digital

- [x] **Milestone 6**: Testing y Depuración **Completado**
  - [x] Tests unitarios para cada componente
  - [x] Tests de casos límite y errores
  - [x] Agregar campo de funct a la ISA
  - [x] Crear suite completa de tests
  - [x] Instruccion del Vault no funcional
  - [x] Programa que usa todas las instrucciones 
  - [x] Benchmarks de rendimiento
  - [x] Identificar y corregir bugs
  - [x] Validar métricas
  - [x] Tests de integración del sistema completo
  - [x] Documentar proceso completo
  - [x] Validación y Preparación de Entrega

- [ ] **Milestone 7**: Defensa del Proyecto **# de Octubre 2025**


### Versión Actual

**v1.0.0**

---

## Información

### Repositorio
- **GitHub**: [https://github.com/Kendall2300/ProyectoG1-ISA](https://github.com/Kendall2300/ProyectoG1-ISA)
- **Issues**: [https://github.com/Kendall2300/ProyectoG1-ISA/issues](https://github.com/Kendall2300/ProyectoG1-ISA/issues)
- **Discussions**: [https://github.com/Kendall2300/ProyectoG1-ISA/discussions/landing](https://github.com/Kendall2300/ProyectoG1-ISA/discussions/landing)

### Arquitectura de Computadores 1
- **Profesor**: Dr.-Ing. Jeferson González Gómez
- **Email**: [jeferson.gonzalez@tec.ac.cr]

---

## Créditos

### Desarrolladores Principales
- **Kendall Martinez C** - Arquitecto ISA
- **Andres Alfaro M** - Implementador CPU
- **Daniel Ureña L** - Desarrollador SW
- **Marco Villatoro C** - Especialista Seguridad

### Herramientas Utilizadas
- **Python** - Lenguaje de programación
- **Git/GitHub** - Control de versiones
- **VS Code / PyCharm** - IDEs
- **Markdown** - Documentación

---

[Documentación](docs/isa.md)
[Green Card](docs/green_card.html)
[Issues](https://github.com/Kendall2300/ProyectoG1-ISA/issues)
[Discussions](https://github.com/Kendall2300/ProyectoG1-ISA/discussions/landing)

---

**SecureRISC v1.0** | **TEC 2025** | **CE-4301**

**Última actualización:** Octubre 2025  
