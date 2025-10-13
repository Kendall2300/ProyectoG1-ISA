# ==============================
# R-TYPE INSTRUCTIONS
# ==============================
LUI R1, 0x0010
LUI R2, 0x0001
ADD R3, R1, R2
SUB R4, R1, R2
MUL R5, R1, R2
DIV R6, R1, R2
MOD R7, R1, R2
AND R8, R1, R2
OR  R9, R1, R2
XOR R10, R1, R2
NOT R11, R1
SLL R12, R1, R2
SRL R13, R1, R2
ROL R14, R1, R2

# ==============================
# I-TYPE INSTRUCTIONS
# ==============================
ADDI R15, R1, 5
SUBI R16, R1, 2
ANDI R17, R1, 3
ORI  R18, R1, 1
XORI R19, R1, 7
SLLI R20, R1, 2
LUI  R21, 0x0002

# ==============================
# MEMORY (LD / SD)
# ==============================
SD R3, 8(R0)
LD R22, 8(R0)

# ==============================
# BRANCH & JUMPS
# ==============================
BEQ R1, R1, 2
ADDI R23, R0, 9
BNE R1, R2, 2
ADDI R24, R0, 8
BLT R2, R1, 2
ADDI R25, R0, 7
BGE R1, R2, 2
ADDI R26, R0, 6
J  40
ADDI R27, R0, 5
JAL R28, 48
ADDI R29, R0, 4
JR R0

# ==============================
# VAULT & HASH MODULE
# ==============================
VINIT 0
VSTORE 0, R1
HBLOCK R1
HMULK R2, R1
HMODP R3, R1
HFINAL R4
VSIGN R5, 0
VVERIF R6, 0

# ==============================
# END
# ==============================
HALT
