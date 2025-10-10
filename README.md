# SecureRISC - Arquitectura RISC con Extensiones de Seguridad

[![ISA Version](https://img.shields.io/badge/ISA-v1.0-blue.svg)](docs/ISA.md)
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
- [Uso Rápido](#-uso-rápido)
- [Ejemplos](#-ejemplos)
- [Documentación](#-documentación)
- [Desarrollo](#-desarrollo)
- [Equipo](#-equipo)
- [Referencias](#-referencias)

---

## Descripción

**SecureRISC** es una arquitectura del set de instrucciones (ISA) RISC de 64 bits diseñada específicamente para aplicaciones de seguridad de la información. La arquitectura provee soporte nativo en hardware para:

- ✅ **Función hash criptográfica ToyMDMA** - Procesamiento acelerado por hardware (50x speedup)
- ✅ **Almacenamiento seguro de llaves privadas** - Bóveda aislada (Root of Trust)
- ✅ **Operaciones de firma y verificación digital** - Instrucciones nativas VSIGN/VVERIF
- ✅ **Pipeline eficiente de 5 etapas** - IF-ID-EX-MEM-WB clásico RISC

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
│
├── docs/                       # Documentación
│   ├── ISA.md                 # Especificación completa de la ISA
│   ├── ENCODING.md            # Referencia de codificación binaria
│   ├── green_card.html        # Hoja de referencia rápida
│   ├── green_card.pdf         # Green Card en PDF
│   ├── CPU_MODEL.md           # Documentación del simulador
│   ├── ASSEMBLER.md           # Guía del ensamblador
│   ├── USER_MANUAL.md         # Manual de usuario
│   ├── diagrams/              # Diagramas de arquitectura
│   │   ├── isa_overview.png
│   │   ├── pipeline.png
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
│   ├── test_assembler.py      # Tests del ensamblador
│   ├── test_cpu.py            # Tests del CPU
│   ├── test_instructions.py   # Tests de instrucciones
│   ├── test_hash.py           # Tests de ToyMDMA
│   ├── test_vault.py          # Tests de bóveda
│   └── integration/           # Tests de integración
│
├── scripts/                   # Scripts de utilidad
│   ├── isa_analysis.py        # Análisis de características ISA
│   ├── run_tests.sh           # Ejecutar todos los tests
│   └── benchmark.py           # Benchmarks de rendimiento
│
└── test_files/                # Archivos de prueba
    ├── input/                 # Archivos para firmar
    │   ├── test1.txt
    │   └── test2.bin
    ├── signed/                # Archivos firmados
    └── results/               # Resultados de validación
```

---

## Requisitos

### Software Necesario

- **Python 3.8 o superior**
- **pip** (gestor de paquetes de Python)
- **Git** (para clonar el repositorio)

### Dependencias Python

Las dependencias se instalan automáticamente, pero aquí está la lista:

```
numpy>=1.21.0
matplotlib>=3.4.0
```

**Opcional para desarrollo:**
```
pytest>=7.0.0          # Para ejecutar tests
black>=22.0.0          # Para formateo de código
pylint>=2.12.0         # Para análisis estático
```

---

## Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/SecureRISC.git
cd SecureRISC
```

### 2. Crear Entorno Virtual (Recomendado)

```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Verificar Instalación

```bash
python src/assembler.py --version
python scripts/isa_analysis.py --help
```

---

## Uso Rápido

### Ejecutar Análisis de la ISA

Genera las 6 gráficas de justificación de diseño:

```bash
python scripts/isa_analysis.py
```

**Salida:**
```
ANÁLISIS COMPLETO DE CARACTERÍSTICAS ISA - SecureRISC
════════════════════════════════════════════════════════

ANÁLISIS 1: ANCHO DE INSTRUCCIÓN
✓ DECISIÓN: 32 bits
Gráfica guardada: docs/analysis/instruction_width_analysis.png

ANÁLISIS 2: NÚMERO DE REGISTROS
✓ DECISIÓN: 32 registros
Gráfica guardada: docs/analysis/register_count_analysis.png

[... más análisis ...]

Análisis completado exitosamente!
```

### Ensamblar un Programa

```bash
python src/assembler.py examples/hello_world.asm -o output.bin
```

**Opciones:**
- `-o, --output`: Archivo de salida (default: `a.out`)
- `-f, --format`: Formato de salida (`hex`, `bin`, `bytes`) (default: `hex`)
- `-v, --verbose`: Modo detallado
- `--dump`: Mostrar código ensamblado en consola

**Ejemplo con opciones:**
```bash
python src/assembler.py examples/digital_signature.asm \
    -o signature.bin \
    -f hex \
    --verbose \
    --dump
```

### Ejecutar un Programa

```bash
python src/cpu.py output.bin
```

**Opciones:**
- `-d, --debug`: Modo debug (muestra estado del CPU paso a paso)
- `-m, --metrics`: Mostrar métricas de ejecución
- `-b, --breakpoint ADDR`: Establecer breakpoint en dirección
- `--max-cycles N`: Límite de ciclos de ejecución

**Ejemplo con debug:**
```bash
python src/cpu.py output.bin --debug --metrics
```

### Pipeline Completo: Ensamblar y Ejecutar

```bash
# Ensamblar
python src/assembler.py examples/digital_signature.asm -o signature.bin

# Ejecutar con métricas
python src/cpu.py signature.bin --metrics

# O en una sola línea:
python src/assembler.py examples/digital_signature.asm -o /tmp/prog.bin && \
python src/cpu.py /tmp/prog.bin --metrics
```

---

## Ejemplos

### Ejemplo 1: Programa Simple - Suma de Números

**Archivo:** `examples/simple_add.asm`

```assembly
# Programa simple: suma dos números
    ADDI R1, R0, 10        # R1 = 10
    ADDI R2, R0, 20        # R2 = 20
    ADD  R3, R1, R2        # R3 = R1 + R2 = 30
    HALT                   # Detener
```

**Compilar y ejecutar:**
```bash
python src/assembler.py examples/simple_add.asm -o add.bin
python src/cpu.py add.bin --debug
```

**Salida esperada:**
```
[Ciclo 1] IF: PC=0x0000, Instr=0x0C010010
[Ciclo 2] ID: ADDI R1, R0, 10
[Ciclo 3] EX: R1 = 0 + 10 = 10
...
[Ciclo 10] WB: R3 = 30

Ejecución completada en 10 ciclos
Registros finales:
  R1 = 0x000000000000000A (10)
  R2 = 0x0000000000000014 (20)
  R3 = 0x000000000000001E (30)
```

### Ejemplo 2: Firma Digital de un Archivo

**Archivo:** `examples/digital_signature.asm`

```assembly
# ==========================================
# Firma Digital con SecureRISC
# ==========================================

# 1. Cargar llave privada en bóveda
    LUI    R1, 0x1234           # Llave privada
    VSTORE 0, R1                # Guardar en VAULT[0]

# 2. Cargar valores iniciales de hash
    LUI    R2, 0x6745           # Valor A
    VSTORE 4, R2                # INIT[0]
    LUI    R3, 0x23C1           # Valor B
    VSTORE 5, R3                # INIT[1]
    LUI    R4, 0xEFCD           # Valor C
    VSTORE 6, R4                # INIT[2]
    LUI    R5, 0xAB89           # Valor D
    VSTORE 7, R5                # INIT[3]

# 3. Inicializar hash
    VINIT  0                    # Cargar INIT → estado hash

# 4. Procesar archivo
    LUI    R10, 0x2000          # Dirección del archivo
    ADDI   R11, R0, 16          # 16 bloques

hash_loop:
    LD     R1, 0(R10)           # Cargar bloque
    HBLOCK R1                   # Procesar (1 ciclo!)
    ADDI   R10, R10, 8          # Siguiente bloque
    SUBI   R11, R11, 1
    BNE    R11, R0, hash_loop

# 5. Generar firma
    VSIGN  R4, 0                # Firma en R4-R7

# 6. Guardar firma
    SD     R4, 0(R10)
    SD     R5, 8(R10)
    SD     R6, 16(R10)
    SD     R7, 24(R10)

    HALT
```

**Ejecutar:**
```bash
# Preparar archivo de prueba
echo "Mensaje secreto" > test_files/input/mensaje.txt

# Ensamblar
python src/assembler.py examples/digital_signature.asm -o sign.bin

# Ejecutar (firma el archivo en memoria 0x2000)
python src/cpu.py sign.bin \
    --load test_files/input/mensaje.txt@0x2000 \
    --dump-memory 0x2000:0x2100 \
    --metrics
```

**Salida esperada:**
```
Cargando archivo: test_files/input/mensaje.txt → 0x2000
Ejecutando programa...

[Ciclo 100] Hash loop: bloque 1/16 procesado
[Ciclo 200] Hash loop: bloque 8/16 procesado
[Ciclo 300] Hash loop completado
[Ciclo 305] Firma generada: 0xABCD1234...

Ejecución completada en 350 ciclos
CPI: 1.21
Instrucciones ejecutadas: 289

Memoria 0x2000-0x2100:
  [Archivo original + Firma al final]
  ...
  0x2080: A3 B4 C5 D6 E7 F8 09 1A  ← Firma (32 bytes)
```

### Ejemplo 3: Usar la Green Card

Abre la hoja de referencia rápida:

```bash
# En navegador (Linux)
xdg-open docs/green_card.html

# En navegador (Mac)
open docs/green_card.html

# En navegador (Windows)
start docs/green_card.html

# O ver el PDF
xdg-open docs/green_card.pdf
```

### Ejemplo 4: Ejecutar Todos los Tests

```bash
# Ejecutar suite completa
python -m pytest tests/ -v

# Solo tests del ensamblador
python -m pytest tests/test_assembler.py -v

# Con cobertura
python -m pytest tests/ --cov=src --cov-report=html
```

---

## Documentación

### Documentos Principales

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **ISA Specification** | Especificación completa de la ISA con justificaciones | [`docs/ISA.md`](docs/isa.md) |
| **Green Card** | Hoja de referencia rápida (HTML/PDF) | [`docs/green_card.html`](docs/green_card.html) |
| **Diagrama** | Diagrama de la arquitectura | [`docs/Diagrama.png`](docs/Diagrama.png) |

### Características de la ISA

#### Registros

- **R0-R31**: 32 registros de propósito general (64 bits)
  - R0: Siempre 0 (hardwired)
  - R1: Valor de retorno
  - R2-R7: Argumentos
  - R29: Frame pointer (FP)
  - R30: Stack pointer (SP)
  - R31: Link register (LR)

- **Registros especiales**: PC, FLAGS

- **Bóveda (aislada)**: 
  - VAULT[0-3]: 4 llaves privadas
  - INIT[0-3]: 4 valores iniciales de hash

#### Formatos de Instrucción

- **R**: Registro-Registro (ADD, SUB, MUL, etc.)
- **I**: Inmediato (ADDI, LD, etc.)
- **S**: Store (SD)
- **B**: Branch (BEQ, BNE, BLT, BGE)
- **J**: Jump (J, JAL)
- **V**: Vault/Security (VSTORE, HBLOCK, VSIGN, etc.)

#### Instrucciones por Categoría

| Categoría | Cantidad | Ejemplos |
|-----------|----------|----------|
| Aritméticas | 5 | ADD, SUB, MUL, DIV, MOD |
| Lógicas | 4 | AND, OR, XOR, NOT |
| Shift/Rotate | 4 | SLL, SRL, ROL, ROR |
| Inmediato | 7 | ADDI, SUBI, LUI, etc. |
| Memoria | 2 | LD, SD |
| Control | 7 | BEQ, BNE, J, JAL, JR, etc. |
| Seguridad | 9 | VSTORE, VINIT, HBLOCK, VSIGN, etc. |
| Sistema | 2 | NOP, HALT |

**Total: ~42 instrucciones**

### Sintaxis Assembly

```assembly
# Comentarios empiezan con #

# Etiquetas
main:
    ADDI R1, R0, 100       # R1 = 100
    
# Instrucciones con inmediato
    LUI  R2, 0x1000        # R2 = 0x1000 << 48

# Memoria: offset(registro)
    LD   R3, 8(R10)        # R3 = MEM[R10 + 8]
    SD   R3, 16(R10)       # MEM[R10 + 16] = R3

# Branches con labels
loop:
    ADDI R1, R1, -1
    BNE  R1, R0, loop      # while (R1 != 0)

# Llamada a función
    JAL  R31, function     # R31 = PC+4; PC = function
    JR   R31               # return
```

---

## Desarrollo

### Configurar Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Formatear código
black src/ tests/

# Análisis estático
pylint src/
```

### Flujo de Trabajo Git

```bash
# Crear branch para nueva feature
git checkout -b feature/add-ror-instruction

# Hacer cambios y commits
git add src/assembler.py
git commit -m "feat: add ROR instruction encoding"

# Push y crear Pull Request
git push origin feature/add-ror-instruction
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_assembler.py::test_encode_add

# Con cobertura
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Benchmarking

```bash
# Ejecutar benchmarks
python scripts/benchmark.py

# Comparar con versión anterior
python scripts/benchmark.py --compare v0.9
```

---

## Equipo

### Proyecto Grupal #1 - Grupo 1

| Rol | Nombre | Responsabilidad |
|-----|--------|-----------------|
| **Arquitecto ISA** | [Kendall] | Diseño de la ISA, formatos, instrucciones |
| **Implementador CPU** | [Andres] | Simulador del CPU, pipeline |
| **Desarrollador SW** | [Daniel] | Ensamblador, herramientas |
| **Especialista Seguridad** | [Marco] | Bóveda, hash, firma digital |

### Curso
- **Materia**: CE-4301 Arquitectura de Computadores I
- **Profesor**: Dr.-Ing. Jeferson González Gómez
- **Institución**: Instituto Tecnológico de Costa Rica
- **Escuela**: Ingeniería en Computadores
- **Período**: II Semestre 2025

---

## Métricas del Proyecto
### Rendimiento

| Métrica | Valor |
|---------|-------|
| **CPI promedio** | 1.2 ciclos/instrucción |
| **Frecuencia objetivo** | 800 MHz |
| **MIPS** | ~666 MIPS |
| **Hash throughput** | 800 MB/s @ 800MHz |
| **Speedup HBLOCK** | 50x vs software |

---

## Licencia

Este proyecto es de naturaleza académica y está desarrollado como parte del curso CE-4301 Arquitectura de Computadores I del Instituto Tecnológico de Costa Rica.

**Uso Académico Únicamente** - No se permite uso comercial sin autorización.

---

## Soporte y Contacto

### Issues y Bugs

Si encuentras un bug o tienes una sugerencia:

1. Revisa los [issues existentes](https://github.com/Kendall2300/ProyectoG1-ISA/issues)
2. Crea un nuevo issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Logs o capturas de pantalla

### Preguntas

Para preguntas sobre el proyecto:
- Abre un [Discussion](https://github.com/Kendall2300/ProyectoG1-ISA/discussions/landing)

### Contribuciones

Este es un proyecto académico cerrado. Las contribuciones externas no son aceptadas durante el período del curso.

---

## 🎓 Agradecimientos

- Dr.-Ing. Jeferson González Gómez por la guía y especificación del proyecto
- Instituto Tecnológico de Costa Rica
- Comunidad RISC-V por referencias de arquitectura
- Estudiantes del curso por el feedback

**Última actualización:** Octubre 2025  
**Versión:** 1.0.0-alpha
**Hecho con amor por el Equipo SecureRISC**
