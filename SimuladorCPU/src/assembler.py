# assembler.py
# Versión 2.1 — Completo: R, I, S, B, J, Vault/Hash/Sign (SecureRISC)

import re
from Instruction import parse_instructions

# === Tabla de opcodes (según ISA.md actualizado) ===
OPCODES = {
    "ADD": 0x00, "SUB": 0x00, "MUL": 0x00, "DIV": 0x00, "MOD": 0x00,
    "AND": 0x01, "OR": 0x01, "XOR": 0x01, "NOT": 0x01,
    "SLL": 0x02, "SRL": 0x02, "ROL": 0x02,
    "ADDI": 0x03, "SUBI": 0x03, "ANDI": 0x03, "ORI": 0x03,
    "XORI": 0x03, "SLLI": 0x03, "LUI": 0x03,
    "LD": 0x04, "SD": 0x05,
    "BEQ": 0x06, "BNE": 0x06, "BLT": 0x06, "BGE": 0x06,
    "J": 0x07, "JAL": 0x08, "JR": 0x09,  # Opcodes diferentes para cada jump
    "VSTORE": 0x10, "VINIT": 0x10,
    "HBLOCK": 0x11, "HMULK": 0x11, "HMODP": 0x11, "HFINAL": 0x11,
    "VSIGN": 0x12, "VVERIF": 0x12,
    "NOP": 0x3F, "HALT": 0x3F
}

# === Tabla de funct para formatos R, I y B ===
FUNCT_CODES = {
    # R-type functions (6 bits)
    "ADD": 0x00, "SUB": 0x01, "MUL": 0x02, "DIV": 0x03, "MOD": 0x04,
    "AND": 0x00, "OR": 0x01, "XOR": 0x02, "NOT": 0x03,
    "SLL": 0x00, "SRL": 0x01, "ROL": 0x02
}

# === Tabla de funct para instrucciones I-type (4 bits) ===
I_FUNCT_CODES = {
    "ADDI": 0x00, "SUBI": 0x01, "ANDI": 0x02, "ORI": 0x03,
    "XORI": 0x04, "SLLI": 0x05, "LUI": 0x06
}

# === Tabla de funct para instrucciones B-type (4 bits) ===
B_FUNCT_CODES = {
    "BEQ": 0x00, "BNE": 0x01, "BLT": 0x02, "BGE": 0x03
}

def reg_num(reg):
    try:
        return int(reg.replace('R', '').strip())
    except Exception:
        raise ValueError(f"Registro inválido: {reg}")

# --- Encoders por formato (alineados al ISA) ---
def encode_R(op, instr):
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    rs2 = reg_num(instr.rs2) if instr.rs2 else 0
    rd  = reg_num(instr.rd)
    shamt = 0
    funct = FUNCT_CODES.get(op, 0)
    return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | (rd << 11) | (shamt << 6) | funct

def encode_I(op, instr):
    # Nuevo formato I: opcode | rs1 | rd | funct | imm (12 bits)
    # |31----26|25---21|20---16|15---12|11-------------0|
    # | opcode |  rs1  |  rd   | funct |   immediate    |
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1) if instr.rs1 else 0
    rd  = reg_num(instr.rd)
    funct = I_FUNCT_CODES.get(op, 0)  # 4 bits
    imm = int(instr.immediate) & 0xFFF  # 12 bits
    return (opcode << 26) | (rs1 << 21) | (rd << 16) | (funct << 12) | imm

def encode_S(op, instr):
    # LD/SD: opcode | base(rs1) | src/rd (rs2) | offset (16)
    opcode = OPCODES[op]
    base = reg_num(instr.rs1)
    src  = reg_num(instr.rs2)
    offset = int(instr.imm) & 0xFFFF
    return (opcode << 26) | (base << 21) | (src << 16) | offset

def encode_B(op, instr):
    # Nuevo formato B: opcode | rs1 | rs2 | funct | offset (12 bits)
    # |31----26|25---21|20---16|15---12|11-----------0|
    # | opcode |  rs1  |  rs2  | funct |   offset     |
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    rs2 = reg_num(instr.rs2)
    funct = B_FUNCT_CODES.get(op, 0)  # 4 bits
    offset = int(instr.immediate) & 0xFFF  # 12 bits
    return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | (funct << 12) | offset

def encode_J(op, instr):
    # Formato J para J y JAL: opcode | address (26 bits)
    opcode = OPCODES[op]
    if op == "JAL":
        # JAL rd, addr -> necesitamos rd en el address field (modificar si necesario)
        addr = int(instr.immediate) & 0x3FFFFFF
        return (opcode << 26) | addr
    else:  # J
        addr = int(instr.immediate) & 0x3FFFFFF
        return (opcode << 26) | addr

def encode_JR(op, instr):
    # JR rs1 -> opcode | rs1 | reserved (21 bits)
    opcode = OPCODES[op]
    rs1 = reg_num(instr.rs1)
    return (opcode << 26) | (rs1 << 21)

def encode_V(op, instr):
    # Vault/Hash/Sign family: we place vidx/rd in the rs1/rd fields as appropriate.
    opcode = OPCODES[op]
    # Different V ops have different operand semantics; assembler selects mapping below.
    # This function is a fallback; higher-level logic will use encode_I/R or custom packing.
    return (opcode << 26)

def encode_SYS(op):
    return (OPCODES[op] << 26)

# --- Ensamblado principal ---
def assemble(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    patched_lines = []
    for line in lines:
        clean = line.strip()
        if not clean or clean.startswith('#'):
            continue

        # LUI convenient normalization: allow "LUI R1, 0x10" or "LUI R1, R0, 0x10"
        if clean.upper().startswith("LUI") and clean.count(',') == 1:
            parts = clean.split(',')
            rd_part = parts[0].split()[1]
            imm_part = parts[1]
            clean = f"LUI {rd_part}, R0, {imm_part}"

        # convert hex immediates
        for match in re.findall(r'0x[0-9A-Fa-f]+', clean):
            clean = clean.replace(match, str(int(match, 16)))

        patched_lines.append(clean + "\n")

    instrs = parse_instructions(patched_lines)
    bin_lines = []

    for instr in instrs:
        try:
            op = instr.op.upper()

            # R-type arithmetic/logical
            if op in FUNCT_CODES:
                code = encode_R(op, instr)

            # I-type arithmetic and LUI family
            elif op in {"ADDI", "SUBI", "ANDI", "ORI", "XORI", "SLLI", "LUI"}:
                code = encode_I(op, instr)

            # Load/Store
            elif op in {"LD", "SD"}:
                code = encode_S(op, instr)

            # Branches
            elif op in {"BEQ", "BNE", "BLT", "BGE"}:
                code = encode_B(op, instr)

            # Jumps
            elif op in {"J", "JAL"}:
                code = encode_J(op, instr)
            elif op == "JR":
                code = encode_JR(op, instr)

            # Vault / Hash / Sign (special encodings)
            elif op in {"VSTORE", "VINIT"}:
                # VSTORE vidx, rs1  -> opcode | vidx in rs1(5) | rs1 reg in rs2
                opcode = OPCODES[op]
                vidx = instr.vidx
                rs1_reg = reg_num(instr.rs1) if instr.rs1 else 0
                code = (opcode << 26) | (vidx << 21) | (rs1_reg << 16)

            elif op == "HBLOCK":
                # HBLOCK rs1 (use I-like packing: opcode | rs1 | rd=0 | imm=0)
                opcode = OPCODES[op]
                rs1 = reg_num(instr.rs1)
                code = (opcode << 26) | (rs1 << 21)

            elif op in {"HMULK", "HMODP"}:
                # HMULK rd, rs1  -> pkg as I: opcode | rs1 | rd
                opcode = OPCODES[op]
                rd = reg_num(instr.rd)
                rs1 = reg_num(instr.rs1)
                code = (opcode << 26) | (rs1 << 21) | (rd << 16)

            elif op == "HFINAL":
                # HFINAL rd -> opcode | rd in bits [20:16]
                opcode = OPCODES[op]
                rd = reg_num(instr.rd)
                code = (opcode << 26) | (0 << 21) | (rd << 16)

            elif op == "VSIGN":
                # VSIGN rd, vidx -> opcode | vidx in rs1 | rd in rd field
                opcode = OPCODES[op]
                rd = reg_num(instr.rd)
                vidx = instr.vidx
                code = (opcode << 26) | (vidx << 21) | (rd << 16)

            elif op == "VVERIF":
                # VVERIF rs, vidx -> opcode | vidx in rs1 | rs register in rs2
                opcode = OPCODES[op]
                rs = reg_num(instr.rs)
                vidx = instr.vidx
                code = (opcode << 26) | (vidx << 21) | (rs << 16)

            # System
            elif op in {"NOP", "HALT"}:
                code = encode_SYS(op)

            else:
                print(f"[WARN] Instrucción no soportada aún: {op}")
                continue

            bin_lines.append(f"{code:032b}")

        except Exception as e:
            print(f"[ERROR] Línea '{instr}': {e}")

    with open(output_file, 'w') as f:
        for line in bin_lines:
            f.write(line + '\n')

    print(f"[OK] Archivo binario generado: {output_file}")
    print(f"Total de instrucciones ensambladas: {len(bin_lines)}")
