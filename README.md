# SecureRISC - Arquitectura RISC con Extensiones de Seguridad

[![ISA Version](https://img.shields.io/badge/ISA-v1.0-blue.svg)](docs/isa.md)
[![Python](https://img.shields.io/badge/Python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-yellow.svg)](LICENSE)

**Proyecto Grupal #1 - Arquitectura de Computadores I**  
Instituto Tecnológico de Costa Rica  
Escuela de Ingeniería en Computadores

---

## Tabla de Contenidos

- [Descripción](#descripción)
- [Características Principales](#características-principales)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Documentación](#documentación)
- [Desarrollo](#desarrollo)
- [Equipo](#equipo)
- [Referencias](#referencias)

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
├── README.md                               # Este archivo
├── LICENSE                                 # Licencia del proyecto
├── .gitignore                              # Archivos ignorados por Git
│
├── docs/                                   # Documentación
│   ├── isa.md                              # Especificación completa de la ISA
│   ├── green_card.html                     # Hoja de referencia rápida
│   ├── USER_MANUAL.md                      # Manual de usuario
│   ├── Diagrama.png                        # Diagrama de microarquitectura
│   └── analysis/                           # Gráficas de análisis
│       ├── instruction_width_analysis.png  #
│       └── addressing_modes_analysis.png   #
│
├── SimuladorCPU/                           # Carpeta contenedora
│   ├── gitignore                           # Archivos ignorados por Git
│   ├── readme.md                           # Instrucciones para iniciar el simulador
│   └── src                                 # Codigo Fuente
│       ├── CPU                             # Archivos del CPU
|       |   ├── HazardUnit.py               
|       |   ├── Memory.py                    
|       |   ├── Pipeline.py                  
|       |   └── RegisterFile.py              
│       ├── UI                              # Archivos de Interfaz Grafica
|       |   ├── Console.py                  
|       |   ├── MemoryView.py                
|       |   ├── RegisterView.py              
|       |   └── TextEditor.py                
│       ├── App.py                          # Codigo Principal
│       ├── Instruction.py                  # Set de instrucciones
│       ├── assembler.py                    # Traductor de lenguaje
│       └── main.py                         # Archivo Principal
└── testASM                                 # Codigos de pruebas
    ├── firmar_archivo.asm                  # Prueba de firma de archivo
    ├── test1.asm                           # Prueba de algunos comandos
    ├── test_all_instructions               # Prueba de todas las instrucciones
    └── verificar_firma.asm                 # Prueba para verificar firma
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
git clone https://github.com/Kendall2300/ProyectoG1-ISA
cd SimuladorCPU/src

# 2. Crear entorno virtual (recomendado)
python3 -m venv venv

# 3. Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# 4. Verificar instalación
python3 main.py --version
```

---

## Documentación

### Documentos Principales

| Documento | Descripción | Ubicación |
|-----------|-------------|-----------|
| **ISA Specification** | Especificación completa de la ISA con justificaciones | [`docs/ISA.md`](docs/isa.md) |
| **Green Card** | Hoja de referencia rápida (HTML/PDF) | [`docs/green_card.html`](docs/green_card.html) |
| **Diagrama de Arquitectura** | Diagrama de arquitectura desarrollada | [`docs/diagrama.png`](docs/Diagrama.png) |
| **User Manual** | Manual de usuario completo | [`docs/USER_MANUAL.md`](docs/USER_MANUAL.md) |

### Características de la ISA

Revisar documentacion especifica: [`docs/ISA.md`](docs/isa.md).

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

# 3. Configurar pre-commit hooks (opcional)
pre-commit install

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

**v1.0.1**

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
