# Inicialización 
LUI R1, 0x0010            # Direccion base de clave privada
LUI R2, 0x1000            # Direccion base de archivo
VINIT 1                   # Inicializa contexto HASH/SHA256 (Vault[1])
VSTORE 1, R1              # Carga clave privada en Vault[1]

# Carga y procesamiento de bloques
# Asumimos 2 bloques de datos (pueden ser más)
LD R3, 0(R2)              # Carga bloque 1 en R3
VSTORE 0, R3              # Guarda bloque 1 en Vault[0]
HBLOCK R3                 # Procesa bloque 1

ADDI R2, R2, 8            # Avanza al siguiente bloque
LD R4, 0(R2)              # Carga bloque 2 en R4
VSTORE 0, R4              # Guarda bloque 2 en Vault[0]
HBLOCK R4                 # Procesa bloque 2

# Finalización del hash 
HFINAL R6                 # Escribe digest resultante en R6–R9

# Firma digital 
VSIGN R10, 1              # Firma digest (R6–R9) usando clave privada Vault[1]

HALT
