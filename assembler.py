# assembler.py
# Versión 1.0 (binaria básica)

from Instruction import parse_instructions

# === Tabla de opcodes (según tu ISA) ===
OPCODES = {
    "ADD": 0x00, "SUB": 0x00, "MUL": 0x00, "DIV": 0x00, "MOD": 0x00,
    "AND": 0x01, "OR": 0x01, "XOR": 0x01, "NOT": 0x01,
    "SLL": 0x02, "SRL": 0x02, "ROL": 0x02,
    "ADDI": 0x03, "SUBI": 0x03, "ANDI": 0x03, "ORI": 0x03,
    "XORI": 0x03, "SLLI": 0x03, "LUI": 0x03,
    "LD": 0x04, "SD": 0x05,
    "BEQ": 0x06, "BNE": 0x06, "BLT": 0x06, "BGE": 0x06,
    "J": 0x07, "JAL": 0x07, "JR": 0x08,
    "VSTORE": 0x10, "VINIT": 0x10,
    "HBLOCK": 0x11, "HMULK": 0x11, "HMODP": 0x11, "HFINAL": 0x11,
    "VSIGN": 0x12, "VVERIF": 0x12,
    "NOP": 0x3F, "HALT": 0x3F
}

# === Tabla de funct (simplificada) ===
FUNCT_CODES = {
    "ADD": 0x00, "SUB": 0x01, "MUL": 0x02, "DIV": 0x03, "MOD": 0x04,
    "AND": 0x00, "OR": 0x01, "XOR": 0x02, "NOT": 0x03,
    "SLL": 0x00, "SRL": 0x01, "ROL": 0x02
}

# === Función para extraer número de registro ===
def reg_num(reg):
    return int(reg.replace('R', '').strip())

# === Codificadores de formato ===
def encode_R(op, instr):
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    rs2 = reg_num(instr.rs2) if instr.rs2 else 0
    rd = reg_num(instr.rd)
    shamt = 0
    funct = FUNCT_CODES.get(op, 0)
    return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | (rd << 11) | (shamt << 6) | funct

def encode_I(op, instr):
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    rd = reg_num(instr.rd)
    imm = int(instr.immediate)
    imm &= 0xFFFF
    return (opcode << 26) | (rs1 << 21) | (rd << 16) | imm

def encode_S(op, instr):
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    rs2 = reg_num(instr.rs2)
    offset = int(instr.imm) & 0xFFFF
    return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | offset

def encode_J(op, instr):
    opcode = OPCODES[op]
    addr = int(instr.immediate) & 0x3FFFFFF
    return (opcode << 26) | addr

def encode_SYS(op):
    opcode = OPCODES[op]
    return (opcode << 26)

# === Función principal de ensamblado ===
def assemble(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    instrs = parse_instructions(lines)
    bin_lines = []

    for instr in instrs:
        try:
            op = instr.op
            opcode = OPCODES.get(op)

            if op in {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "NOT", "SLL", "SRL", "ROL"}:
                code = encode_R(op, instr)
            elif op in {"ADDI", "SUBI", "ANDI", "ORI", "XORI", "SLLI", "LUI"}:
                code = encode_I(op, instr)
            elif op in {"LD", "SD"}:
                code = encode_S(op, instr)
            elif op in {"J", "JAL", "JR"}:
                code = encode_J(op, instr)
            elif op in {"NOP", "HALT"}:
                code = encode_SYS(op)
            else:
                print(f"[WARN] Instrucción no soportada aún: {op}")
                continue

            bin_str = f"{code:032b}"
            bin_lines.append(bin_str)

        except Exception as e:
            print(f"[ERROR] Línea '{instr}': {e}")

    # === Escribir archivo binario ===
    with open(output_file, 'w') as f:
        for line in bin_lines:
            f.write(line + '\n')

    print(f"[OK] Archivo binario generado: {output_file}")
    print(f"Total de instrucciones ensambladas: {len(bin_lines)}")


if __name__ == "__main__":
    assemble("test.asm", "out/test.bin")
