# SecureRISC - Arquitectura del Set de Instrucciones

**Proyecto Grupal #1 - Arquitectura de Computadores I**  
**Grupo:** 1  
**Integrante 1 - Arquitecto ISA:** Kendall Martínez Carvajal
**Integrante 2 - Diseñador de Microarquitectura:** Marco Villatoro Chacon
**Integrante 3 - Programador del simulador:** Andrés Alfaro Mayorga
**Integrante 4 - Programador ensamblador:** Daniel Ureña López

---

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Características Generales](#características-generales)
3. [Registros](#registros)
4. [Formatos de Instrucción](#formatos-de-instrucción)
5. [Set de Instrucciones](#set-de-instrucciones)
6. [Instrucciones Especiales de Seguridad](#instrucciones-especiales-de-seguridad)
7. [Modos de Direccionamiento](#modos-de-direccionamiento)
8. [Codificación Binaria](#codificación-binaria)
9. [Justificación de Diseño](#justificación-de-diseño)
10. [Referencias](#referencias)

---

## Introducción

**SecureRISC** es una arquitectura del set de instrucciones (ISA) RISC de 64 bits diseñada específicamente para aplicaciones de seguridad de la información. La arquitectura provee soporte nativo para:

- Función hash criptográfica ToyMDMA
- Almacenamiento seguro de llaves privadas (bóveda)
- Operaciones de firma y verificación digital
- Ejecución eficiente con pipeline de 5 etapas

### Filosofía de Diseño

SecureRISC sigue los principios RISC clásicos:
- Instrucciones de tamaño fijo (32 bits)
- Arquitectura load-store
- Gran número de registros (32 GPRs)
- Pipeline simple y eficiente
- Extensiones especializadas para el dominio de aplicación

---

## Características Generales

| Característica | Valor | Justificación |
|---------------|-------|---------------|
| **Ancho de palabra** | 64 bits | Procesamiento eficiente de bloques criptográficos |
| **Tamaño de instrucción** | 32 bits fijos | Decodificación simple, fetch predecible |
| **Registros GPR** | 32 × 64 bits | Reduce spills a memoria (~5%), área aceptable |
| **Pipeline** | 5 etapas | Balance clásico RISC (IF-ID-EX-MEM-WB) |
| **Endianness** | Little-endian | Compatibilidad con sistemas modernos |
| **Bóveda segura** | 8 slots × 64 bits | 4 llaves privadas + 4 valores init hash |

---

## Registros

### Registros de Propósito General (GPR)

| Registro | Nombre | Descripción | Convención |
|----------|--------|-------------|------------|
| R0 | ZERO | Constante 0 (hardwired) | Read-only |
| R1 | RET | Valor de retorno | Caller-saved |
| R2-R7 | ARG0-ARG5 | Argumentos de función | Caller-saved |
| R8-R15 | T0-T7 | Registros temporales | Caller-saved |
| R16-R23 | S0-S7 | Registros salvados | Callee-saved |
| R24-R28 | T8-T12 | Temporales adicionales | Caller-saved |
| R29 | FP | Frame pointer | Callee-saved |
| R30 | SP | Stack pointer | Callee-saved |
| R31 | LR | Link register | Caller-saved |

### Registros Especiales

- **PC** (64 bits): Program Counter
- **FLAGS** (8 bits): Registro de banderas
  - Bit 0: Z (Zero)
  - Bit 1: N (Negative)
  - Bit 2: C (Carry)
  - Bit 3: V (Overflow)
  - Bit 4-7: (Reservados en caso de ocupar banderas que faciliten los procesos)

### Bóveda Segura (Aislada)

**NO accesible como memoria tradicional**. Solo mediante instrucciones especiales.

- **VAULT[0-3]**: 4 llaves privadas de 64 bits
- **INIT[0-3]**: 4 valores iniciales de hash (A, B, C, D)

### Estado Interno de Hash

- **HS_A, HS_B, HS_C, HS_D**: Estado de 256 bits del hash ToyMDMA
- Actualizado por `HBLOCK`, leído por `HFINAL`

---

## Formatos de Instrucción

Todas las instrucciones tienen **32 bits** de longitud.

### Formato R (Register-Register)
```
|31----26|25---21|20---16|15---11|10----6|5-----0|
| opcode |  rs1  |  rs2  |  rd   | shamt | funct |
| 6 bits | 5 bits| 5 bits| 5 bits| 5 bits| 6 bits|
```
**Uso:** Operaciones ALU entre registros

### Formato I (Immediate)
```
|31----26|25---21|20---16|15---12|11-------------0|
| opcode |  rs1  |  rd   | funct |   immediate    |
| 6 bits | 5 bits| 5 bits|  4 bits |  12 bits    |
```
**Uso:** Operaciones con inmediato, loads

### Formato S (Store)
```
|31----26|25---21|20---16|15----------------0|
| opcode |  rs1  |  rs2  |      offset       |
| 6 bits | 5 bits| 5 bits|     16 bits       |
```
**Uso:** Almacenamiento en memoria

### Formato B (Branch)
```
|31----26|25---21|20---16|15---12|11-----------0|
| opcode |  rs1  |  rs2  | funct |   offset     |
| 6 bits | 5 bits| 5 bits|  4    | 12 bits      |
```
**Uso:** Saltos condicionales (bits 15-14 codifican tipo de branch)

### Formato J (Jump)
```
|31----26|25-----------------------0|
| opcode |        address           |
| 6 bits |        26 bits           |
```
**Uso:** Saltos incondicionales

### Formato V (Vault/Hash/Sign)
```
|31----26|25---21|20---16|15---11|10-----------0|
| opcode |  vidx |  rd   | funct |   reserved   |
| 6 bits | 5 bits| 5 bits| 5 bits|   11 bits    |
```
**Uso:** Operaciones de bóveda, hash y firma digital

---

## Set de Instrucciones

### Instrucciones Aritméticas (Opcode 0x00)

| Mnemónico | Formato | Sintaxis | Operación | Funct |
|-----------|---------|----------|-----------|-------|
| ADD | R | `ADD rd, rs1, rs2` | rd = rs1 + rs2 | 0x00 |
| SUB | R | `SUB rd, rs1, rs2` | rd = rs1 - rs2 | 0x01 |
| MUL | R | `MUL rd, rs1, rs2` | rd = rs1 × rs2 | 0x02 |
| DIV | R | `DIV rd, rs1, rs2` | rd = rs1 / rs2 | 0x03 |
| MOD | R | `MOD rd, rs1, rs2` | rd = rs1 % rs2 | 0x04 |

### Instrucciones Lógicas (Opcode 0x01)

| Mnemónico | Formato | Sintaxis | Operación | Funct |
|-----------|---------|----------|-----------|-------|
| AND | R | `AND rd, rs1, rs2` | rd = rs1 & rs2 | 0x00 |
| OR | R | `OR rd, rs1, rs2` | rd = rs1 \| rs2 | 0x01 |
| XOR | R | `XOR rd, rs1, rs2` | rd = rs1 ^ rs2 | 0x02 |
| NOT | R | `NOT rd, rs1` | rd = ~rs1 | 0x03 |

### Instrucciones de Shift/Rotate (Opcode 0x02)

| Mnemónico | Formato | Sintaxis | Operación | Funct |
|-----------|---------|----------|-----------|-------|
| SLL | R | `SLL rd, rs1, rs2` | rd = rs1 << rs2            | 0x00 |
| SRL | R | `SRL rd, rs1, rs2` | rd = rs1 >> rs2            | 0x01 |
| ROL | R | `ROL rd, rs1, rs2` | rd = rotate_left(rs1, rs2) | 0x02 |

### Instrucciones con Inmediato (Opcode 0x03)

| Mnemónico | Formato | Sintaxis | Operación | Funct |
|-----------|---------|----------|-----------|-------|
| ADDI | I | `ADDI rd, rs1, imm` | rd = rs1 + imm  | 0x00 |
| SUBI | I | `SUBI rd, rs1, imm` | rd = rs1 - imm  | 0x01 |
| ANDI | I | `ANDI rd, rs1, imm` | rd = rs1 & imm  | 0x02 |
| ORI  | I | `ORI rd, rs1, imm`  | rd = rs1 \| imm | 0x03 |
| XORI | I | `XORI rd, rs1, imm` | rd = rs1 ^ imm  | 0x04 |
| SLLI | I | `SLLI rd, rs1, imm` | rd = rs1 << imm | 0x05 |
| LUI  | I | `LUI rd, imm`       | rd = imm << 48  | 0x06 |

### Instrucciones de Memoria

| Mnemónico | Opcode | Formato | Sintaxis | Operación | Opcode |
|-----------|--------|---------|----------|-----------|-------|
| LD | 0x04 | I | `LD rd, offset(rs1)`  | rd = MEM[rs1 + offset]  | 0x04 |
| SD | 0x05 | S | `SD rs2, offset(rs1)` | MEM[rs1 + offset] = rs2 | 0x05 |

### Instrucciones de Control de Flujo

#### Branches (Opcode 0x06)

| Mnemónico | Condición | Sintaxis | Operación | Funct |
|-----------|-----------|----------|-----------|-------|
| BEQ | rs1 == rs2 | `BEQ rs1, rs2, offset` | if (rs1 == rs2) PC += offset | 0x00 |
| BNE | rs1 != rs2 | `BNE rs1, rs2, offset` | if (rs1 != rs2) PC += offset | 0x01 |
| BLT | rs1 < rs2  | `BLT rs1, rs2, offset` | if (rs1 < rs2) PC += offset  | 0x02 |
| BGE | rs1 >= rs2 | `BGE rs1, rs2, offset` | if (rs1 >= rs2) PC += offset | 0x03 |

#### Jumps

| Mnemónico | Opcode | Sintaxis | Operación | Opcode |
|-----------|--------|----------|-----------|-------|
| J   | 0x07 | `J addr`       | PC = addr            | 0x07 |
| JAL | 0x07 | `JAL rd, addr` | rd = PC+4; PC = addr | 0x08 |
| JR  | 0x08 | `JR rs1`       | PC = rs1             | 0x09 |

### Instrucciones de Sistema (Opcode 0x3F)

| Mnemónico | Sintaxis | Operación |
|-----------|----------|-----------|
| NOP  | `NOP`  | No operation         |
| HALT | `HALT` | Detiene la ejecución |

---

## Instrucciones Especiales de Seguridad

### Operaciones con Bóveda (Opcode 0x10)

#### VSTORE - Store to Vault
```assembly
VSTORE vidx, rs1
```
**Operación:** 
- Si `vidx < 4`: VAULT[vidx] = rs1 (almacena llave privada)
- Si `4 <= vidx < 8`: INIT[vidx-4] = rs1 (almacena valor inicial)

**Restricción:** Los datos en la bóveda NO pueden ser leídos a registros GPR.

**Ejemplo:**
```assembly
LUI R1, 0x1234
VSTORE 0, R1        # Guarda llave privada en VAULT[0]
LUI R2, 0x6745
VSTORE 4, R2        # Guarda valor inicial A en INIT[0]
```

#### VINIT - Initialize Hash State
```assembly
VINIT vidx
```
**Operación:** Carga valores iniciales desde INIT[0-3] al estado de hash interno (HS_A, HS_B, HS_C, HS_D).

**Ejemplo:**
```assembly
VINIT 0             # Inicializa estado de hash con INIT[0-3]
```

---

### Operaciones de Hash ToyMDMA (Opcode 0x11)

#### HBLOCK - Hash Block Processing
```assembly
HBLOCK rs1
```
**Operación:** Procesa un bloque de 64 bits (rs1) con el algoritmo ToyMDMA y actualiza el estado interno.

**Implementación interna:**
1. f = (HS_A & HS_B) | (~HS_A & HS_C)
2. g = (HS_B & HS_C) | (~HS_B & HS_D)
3. h = HS_A ^ HS_B ^ HS_C ^ HS_D
4. mul = (block × 0x9e3779b97f4a7c15) & 0xFFFFFFFFFFFFFFFF
5. HS_A = rol64(HS_A + f + mul, 7) + HS_B
6. HS_B = rol64(HS_B + g + block, 11) + (HS_C × 3)
7. HS_C = rol64(HS_C + h + mul, 17) + (HS_D % 0xFFFFFFFB)
8. HS_D = rol64(HS_D + HS_A + block, 19) ^ (f × 5)

**Ciclos:** 1 ciclo por bloque (aceleración por hardware)

**Ejemplo:**
```assembly
LD R1, 0(R10)       # Cargar bloque de 64 bits
HBLOCK R1           # Procesar con ToyMDMA (1 ciclo)
ADDI R10, R10, 8    # Avanzar puntero
```

#### HMULK - Hash Multiply by Constant
```assembly
HMULK rd, rs1
```
**Operación:** rd = (rs1 × 0x9e3779b97f4a7c15) & 0xFFFFFFFFFFFFFFFF

**Justificación:** Constante áurea fija permite implementación eficiente con sumadores.

#### HMODP - Hash Modulo Prime
```assembly
HMODP rd, rs1
```
**Operación:** rd = rs1 % 0xFFFFFFFB

**Justificación:** Primo fijo permite optimización en hardware.

#### HFINAL - Finalize Hash
```assembly
HFINAL rd
```
**Operación:** Extrae el hash de 256 bits del estado interno a 4 registros consecutivos:
- rd = HS_A
- rd+1 = HS_B
- rd+2 = HS_C
- rd+3 = HS_D

**Ejemplo:**
```assembly
HFINAL R4           # Hash en R4, R5, R6, R7
```

---

### Operaciones de Firma Digital (Opcode 0x12)

#### VSIGN - Digital Signature Generation
```assembly
VSIGN rd, vidx
```
**Operación:** Genera firma combinando el hash con la llave privada:
- K = VAULT[vidx]
- rd = HS_A XOR K
- rd+1 = HS_B XOR K
- rd+2 = HS_C XOR K
- rd+3 = HS_D XOR K

**Resultado:** Firma de 256 bits en 4 registros consecutivos.

**Ejemplo:**
```assembly
VSIGN R8, 0         # Firma en R8-R11 usando VAULT[0]
```

#### VVERIF - Signature Verification
```assembly
VVERIF rs, vidx
```
**Operación:** Recupera el hash original de una firma:
- K = VAULT[vidx]
- HS_A = rs XOR K
- HS_B = rs+1 XOR K
- HS_C = rs+2 XOR K
- HS_D = rs+3 XOR K

**Uso:** Después de ejecutar, comparar el estado de hash recuperado con el hash recalculado del archivo.

**Ejemplo:**
```assembly
VVERIF R8, 0        # Recupera hash de firma en R8-R11
HFINAL R12          # Extrae hash recalculado a R12-R15
# Comparar R8==R12, R9==R13, R10==R14, R11==R15
```

---

## Modos de Direccionamiento

| Modo | Ejemplo | Descripción |
|------|---------|-------------|
| **Registro**      | `ADD R3, R1, R2`   | Operandos en registros      |
| **Inmediato**     | `ADDI R1, R2, 100` | Constante en la instrucción |
| **Base + Offset** | `LD R1, 8(R2)`     | Dirección = R2 + 8          |
| **Absoluto**      | `J 0x1000`         | Dirección directa           |
| **PC-Relativo**   | `BEQ R1, R2, 16`   | Dirección = PC + offset     |

---

## Codificación Binaria

### Tabla de Opcodes

| Opcode | Hex | Binario | Categoría |
|--------|-----|---------|-----------|
| 0x00 | 00 | 000000 | Aritmética    |
| 0x01 | 01 | 000001 | Lógica        |
| 0x02 | 02 | 000010 | Shift/Rotate  |
| 0x03 | 03 | 000011 | Inmediato     |
| 0x04 | 04 | 000100 | Load          |
| 0x05 | 05 | 000101 | Store         |
| 0x06 | 06 | 000110 | Branch        |
| 0x07 | 07 | 000111 | Jump          |
| 0x08 | 08 | 001000 | Jump Register |
| 0x10 | 10 | 010000 | Vault         |
| 0x11 | 11 | 010001 | Hash          |
| 0x12 | 12 | 010010 | Signature     |
| 0x3F | 3F | 111111 | System        |

### Ejemplo de Codificación

```assembly
ADD R3, R1, R2
```

**Formato R:**
- Opcode: 0x00 (000000)
- rs1: R1 (00001)
- rs2: R2 (00010)
- rd: R3 (00011)
- shamt: 0 (00000)
- funct: 0x00 (000000)

**Binario:** `000000 00001 00010 00011 00000 000000`  
**Hexadecimal:** `0x00422000`

---

## Justificación de Diseño

### 1. Instrucciones de 32 bits

**Decisión:** Tamaño fijo de 32 bits

**Ventajas:**
- Decodificación simple y rápida
- Fetch predecible (4 bytes por instrucción)
- Balance entre densidad de código y complejidad

**Trade-off:**
- Inmediatos limitados a 16 bits
- Suficientes para la mayoría de offsets y constantes
- Se puede usar LUI + ADDI para constantes de 64 bits

**Alternativas consideradas:**
- 16 bits: Muy limitado, codificación compleja
- 64 bits: Desperdicio de memoria, baja densidad

### 2. 32 Registros de Propósito General

**Decisión:** 32 registros de 64 bits

**Análisis:**

| # Registros | Spills (%) | Área Relativa | Bits Codificación |
|-------------|------------|---------------|-------------------|
| 8      | 35%    | 10     | 3     |
| 16     | 15%    | 20     | 4     |
| **32** | **5%** | **40** | **5** |
| 64     | 3%     | 80     | 6     |

**Justificación:**
- Reduce spills a memoria de 35% a 5%
- 5 bits de codificación caben perfectamente en instrucciones de 32 bits
- Área aceptable para el beneficio de rendimiento
- Estándar en arquitecturas RISC modernas (ARM, RISC-V)

### 3. Pipeline de 5 Etapas

**Decisión:** IF - ID - EX - MEM - WB

**Análisis:**

| Etapas | CPI | Freq (MHz) | Rendimiento | Complejidad |
|--------|-----|------------|-------------|-------------|
| 3 | 1.5 | 500 | 333 MIPS | Baja |
| **5** | **1.2** | **800** | **666 MIPS** | **Media** |
| 7 | 1.1 | 1200 | 1090 MIPS | Alta |
| 10 | 1.05 | 1500 | 1428 MIPS | Muy Alta |

**Justificación:**
- Balance clásico de RISC
- Complejidad manejable para implementación
- Buen rendimiento (666 MIPS relativos)
- Penalizaciones moderadas por hazards

### 4. Instrucción HBLOCK Completa

**Decisión:** Una instrucción procesa un bloque completo de hash

**Análisis de alternativas:**

| Diseño | Ciclos/Bloque | Complejidad HW | Flexibilidad |
|--------|---------------|----------------|--------------|
| Todo en SW | 50 | 0% | 100% |
| Primitivas | 20 | 30% | 80% |
| **HBLOCK** | **1** | **60%** | **70%** |
| Coprocesador | 1 | 95% | 30% |

**Justificación:**
- 50x speedup vs software puro
- Complejidad moderada y aceptable
- Mantiene flexibilidad para el programador
- Balance óptimo: eficiencia vs costo

**Instrucciones auxiliares:**
- HMULK: Multiplicación por constante áurea
- HMODP: Módulo por primo específico
- HFINAL: Extracción de resultado

### 5. Bóveda de Llaves Aislada

**Decisión:** Memoria separada, inaccesible desde memoria principal

**Análisis:**

| Diseño | Seguridad | Latencia | Costo Impl. |
|--------|-----------|----------|-------------|
| Memoria General | 20% | 10 ciclos | 10% |
| Registros Especiales | 50% | 1 ciclo | 30% |
| **Bóveda Aislada** | **90%** | **1 ciclo** | **50%** |
| HSM Externo | 95% | 100 ciclos | 90% |

**Justificación:**
- Seguridad muy alta (90/100)
- Latencia mínima (1 ciclo)
- Costo moderado de implementación
- Cumple requisito de Root of Trust
- Las llaves NUNCA pueden ser leídas por software

**Capacidad:**
- 4 llaves privadas (VAULT[0-3])
- 4 valores iniciales de hash (INIT[0-3])
- Total: 64 bytes de almacenamiento seguro

---

## Ejemplo Completo: Programa de Firma Digital

```assembly
#==================================================
# Programa de Firma Digital con SecureRISC
# Firma un archivo usando ToyMDMA y llave privada
#==================================================

# 1. Inicialización de la bóveda
    LUI R1, 0x1234          # Cargar llave privada (parte alta)
    ORI R1, R1, 0x5678      # Completar llave privada
    VSTORE 0, R1            # Guardar en VAULT[0]
    
    # Cargar valores iniciales de hash (A, B, C, D)
    LUI R2, 0x6745
    VSTORE 4, R2            # INIT[0] = A
    
    LUI R3, 0x23C1
    VSTORE 5, R3            # INIT[1] = B
    
    LUI R4, 0xEFCD
    VSTORE 6, R4            # INIT[2] = C
    
    LUI R5, 0xAB89
    VSTORE 7, R5            # INIT[3] = D

# 2. Inicializar estado de hash
    VINIT 0                 # Cargar INIT[0-3] -> HS_A, HS_B, HS_C, HS_D

# 3. Procesar archivo
    LUI R10, 0x2000         # R10 = dirección base del archivo
    ADDI R11, R0, 16        # R11 = número de bloques (16 × 8 bytes = 128 bytes)

hash_loop:
    LD R1, 0(R10)           # Cargar bloque de 64 bits
    HBLOCK R1               # Procesar con ToyMDMA (1 ciclo!)
    ADDI R10, R10, 8        # Avanzar al siguiente bloque
    SUBI R11, R11, 1        # Decrementar contador
    BNE R11, R0, hash_loop  # Continuar si quedan bloques

# 4. Generar firma digital
    VSIGN R4, 0             # Firma en R4-R7 usando VAULT[0]

# 5. Guardar firma al final del archivo
    SD R4, 0(R10)           # Guardar primeros 64 bits
    SD R5, 8(R10)           # Guardar segundos 64 bits
    SD R6, 16(R10)          # Guardar terceros 64 bits
    SD R7, 24(R10)          # Guardar últimos 64 bits

# 6. Finalizar
    HALT                    # Detener ejecución

#==================================================
# Verificación de Firma
#==================================================

verify_signature:
    # Cargar archivo firmado
    LUI R10, 0x2000         # Dirección del archivo
    ADDI R11, R0, 16        # Bloques a procesar
    
    # Recalcular hash del archivo original
    VINIT 0                 # Reiniciar estado

verify_loop:
    LD R1, 0(R10)
    HBLOCK R1
    ADDI R10, R10, 8
    SUBI R11, R11, 1
    BNE R11, R0, verify_loop
    
    # Cargar firma almacenada
    LD R8, 0(R10)           # Cargar firma en R8-R11
    LD R9, 8(R10)
    LD R10, 16(R10)
    LD R11, 24(R10)
    
    # Recuperar hash de la firma
    VVERIF R8, 0            # Descifrar firma -> HS_A, HS_B, HS_C, HS_D
    
    # Extraer hash recalculado
    HFINAL R12              # Hash recalculado en R12-R15
    
    # Comparar (debe hacerse con código adicional)
    # Si R8==R12 && R9==R13 && R10==R14 && R11==R15 -> Firma válida
    
    HALT
```

---

## Métricas de Rendimiento Estimadas

### Procesamiento de Hash ToyMDMA

- **Ciclos por bloque:** 1 ciclo (con HBLOCK)
- **Archivo de 1KB (128 bloques):** ~128 ciclos
- **Speedup vs software:** 50x
- **Throughput:** 800 MB/s @ 800 MHz

### Firma Digital

- **Generación:** Hash + VSIGN = ~130 ciclos
- **Verificación:** Hash + VVERIF + comparación = ~135 ciclos
- **Overhead de seguridad:** < 1%

### Área Estimada del CPU

- **Banco de registros:** 30%
- **ALU + Unidades hash:** 35%
- **Control + Pipeline:** 25%
- **Bóveda segura:** 10%

---

## Referencias

1. **Proyecto Grupal #1 Especificación** - Dr.-Ing. Jeferson González Gómez
2. **Merkle-Damgård Construction** - Ivan Bjerre Damgård, CRYPTO '89
3. **RISC-V ISA Specification** - Andrew Waterman, Krste Asanovic
4. **ARM Architecture Reference Manual** - ARM Limited
5. **Computer Organization and Design RISC-V Edition** - Patterson & Hennessy

---

## Archivos Relacionados

- `green_card.pdf` - Hoja de referencia rápida de instrucciones
- `isa_analysis.py` - Script de análisis de características
- `assembler.py` - Ensamblador SecureRISC
- `../src/cpu_model.py` - Modelo de simulación del CPU
- `../examples/digital_signature.asm` - Ejemplo completo de firma digital

---

**Última actualización:** Octubre 2025  
**Versión ISA:** 1.1