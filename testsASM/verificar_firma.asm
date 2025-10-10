# Inicialización 
LUI R1, 0x0020            # Dirección base de clave pública
LUI R2, 0x1000            # Dirección base de archivo
LUI R3, 0x2000            # Dirección de firma digital
VINIT 2                   # Inicializa contexto de verificación (Vault[2])
VSTORE 2, R1              # Carga clave pública en Vault[2]

# Carga y hash de los bloques
LD R4, 0(R2)              # Carga bloque 1
VSTORE 0, R4
HBLOCK R4

ADDI R2, R2, 8
LD R5, 0(R2)              # Carga bloque 2
VSTORE 0, R5
HBLOCK R5

# Digest final 
HFINAL R6                 # Digest en R6–R9

# Verificación de la firma
LD R10, 0(R3)             # Carga firma en R10
VSTORE 3, R10             # Guarda firma en Vault[3]
VVERIF R6, 2              # Verifica digest usando clave pública Vault[2]

HALT
