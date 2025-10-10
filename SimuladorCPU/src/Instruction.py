# Instruction.py
# Parser de instrucciones (ampliado para Vault/Hash/Sign)

R_TYPE_INSTRS = {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "NOT", "SLL", "SRL", "ROL"}
I_TYPE_INSTRS = {"ADDI", "SUBI", "ANDI", "ORI", "XORI", "SLLI", "LUI"}
S_TYPE_INSTRS = {"LD", "SD"}
B_TYPE_INSTRS = {"BEQ", "BNE", "BLT", "BGE"}
V_TYPE_INSTRS = {"VSTORE", "VINIT", "HBLOCK", "HMULK", "HMODP", "HFINAL", "VSIGN", "VVERIF"}
SYSTEM_TYPE_INSTRS = {"NOP", "HALT"}

class Instruction:
    def __init__(self, instr_str: str):
        tokens = instr_str.replace(',', ' ').strip().split()
        if not tokens:
            raise ValueError("Empty instruction")

        self.op = tokens[0].upper()

        # Common operand fields
        self.rs1 = None
        self.rs2 = None
        self.rd = None
        self.immediate = None
        self.imm = None   # for S-type offset
        self.vidx = None
        self.rs = None

        # R-type: OP RD, RS1, RS2   (NOT: OP RD, RS1)
        if self.op in R_TYPE_INSTRS:
            self.rd = tokens[1].strip()
            self.rs1 = tokens[2].strip(',')
            if self.op != "NOT":
                self.rs2 = tokens[3].strip()

        # I-type: OP RD, RS1, IMM   (LUI: OP RD, IMM  OR OP RD, R0, IMM)
        elif self.op in I_TYPE_INSTRS:
            self.rd = tokens[1].strip()
            # LUI can be "LUI R1, IMM" or "LUI R1, R0, IMM"
            if self.op == "LUI":
                # Cases: tokens length 3 -> LUI R1 IMM
                #        tokens length 4 -> LUI R1 R0 IMM
                if len(tokens) == 3:
                    self.rs1 = "R0"
                    self.immediate = int(tokens[2].strip())
                elif len(tokens) >= 4:
                    self.rs1 = tokens[2].strip(',')
                    self.immediate = int(tokens[3].strip())
                else:
                    raise ValueError("Formato inválido para LUI")
            else:
                self.rs1 = tokens[2].strip(',')
                self.immediate = int(tokens[3].strip())

        # S-type: LD/SD formats: OP RD, offset(base)  OR OP RS2, offset(base)
        elif self.op in S_TYPE_INSTRS:
            reg_field = tokens[1].strip(',')
            offset_part = tokens[2]
            offset, base = offset_part.split('(')
            base = base.strip(')')
            self.imm = int(offset)
            if self.op == "LD":
                self.rd = reg_field
            else:
                self.rs2 = reg_field
            self.rs1 = base

        # Branch type: OP RS1, RS2, OFFSET
        elif self.op in B_TYPE_INSTRS:
            self.rs1 = tokens[1].strip(',')
            self.rs2 = tokens[2].strip(',')
            self.immediate = int(tokens[3].strip())

        # Jumps
        elif self.op == "J":
            self.immediate = int(tokens[1].strip())
        elif self.op == "JAL":
            self.rd = tokens[1].strip(',')
            self.immediate = int(tokens[2].strip())
        elif self.op == "JR":
            self.rs1 = tokens[1].strip()

        # System
        elif self.op in SYSTEM_TYPE_INSTRS:
            pass

        # V-type: Vault / Hash / Sign operations
        elif self.op in V_TYPE_INSTRS:
            if self.op in {"VSTORE", "VINIT"}:
                # VSTORE vidx, rd  OR VINIT (sin argumentos)
                if self.op == "VSTORE":
                    self.vidx = int(tokens[1].strip())
                    self.rd = tokens[2].strip()
                else:  # VINIT
                    self.vidx = 0
                    self.rd = None
            elif self.op == "HBLOCK":
                # HBLOCK rs1 - En formato V: rs1 va en campo 'rd'
                self.vidx = 0
                self.rd = tokens[1].strip()  # rs1 fuente va en rd
            elif self.op in {"HMULK", "HMODP"}:
                # HMULK rd, rs1 / HMODP rd, rs1 - En formato V: rd=rd, rs1=vidx
                self.rd = tokens[1].strip(',')    # registro destino
                self.vidx = int(tokens[2].strip().replace('R', ''))  # registro fuente como número
            elif self.op == "HFINAL":
                # HFINAL rd - Solo registro destino
                self.vidx = 0
                self.rd = tokens[1].strip()
            elif self.op == "VSIGN":
                # VSIGN rd, vidx
                self.rd = tokens[1].strip(',')
                self.vidx = int(tokens[2].strip())
            elif self.op == "VVERIF":
                # VVERIF vidx, rd
                self.vidx = int(tokens[1].strip(','))
                self.rd = tokens[2].strip()

        else:
            raise ValueError(f"Unknown instruction: {self.op}")

    def __str__(self):
        if self.op in R_TYPE_INSTRS:
            if self.op == "NOT":
                return f"{self.op} {self.rd}, {self.rs1}"
            return f"{self.op} {self.rd}, {self.rs1}, {self.rs2}"
        elif self.op in I_TYPE_INSTRS:
            return f"{self.op} {self.rd}, {self.rs1}, {self.immediate}"
        elif self.op in S_TYPE_INSTRS:
            if self.op == "LD":
                return f"{self.op} {self.rd}, {self.imm}({self.rs1})"
            else:
                return f"{self.op} {self.rs2}, {self.imm}({self.rs1})"
        elif self.op in B_TYPE_INSTRS:
            return f"{self.op} {self.rs1}, {self.rs2}, {self.immediate}"
        elif self.op == "J":
            return f"{self.op} {self.immediate}"
        elif self.op == "JAL":
            return f"{self.op} {self.rd}, {self.immediate}"
        elif self.op == "JR":
            return f"{self.op} {self.rs1}"
        elif self.op in V_TYPE_INSTRS:
            if self.op == "VSTORE":
                return f"{self.op} {self.vidx}, {self.rd}"
            elif self.op == "VINIT":
                return f"{self.op}"
            elif self.op == "HBLOCK":
                return f"{self.op} {self.rd}"
            elif self.op in {"HMULK", "HMODP", "HFINAL"}:
                return f"{self.op} {self.rd}"
            elif self.op == "VSIGN":
                return f"{self.op} {self.rd}, {self.vidx}"
            elif self.op == "VVERIF":
                return f"{self.op} {self.vidx}, {self.rd}"
        elif self.op == "HBLOCK":
            return f"{self.op} {self.rs1}"
        elif self.op in {"HMULK", "HMODP"}:
            return f"{self.op} {self.rd}, {self.rs1}"
        elif self.op == "HFINAL":
            return f"{self.op} {self.rd}"
        elif self.op == "VSIGN":
            return f"{self.op} {self.rd}, {self.vidx}"
        elif self.op == "VVERIF":
            return f"{self.op} {self.rs}, {self.vidx}"
        else:
            return "INVALID INSTRUCTION"

def parse_instructions(lines: str):
    instr_list = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.endswith(':'):
            continue
        instr = Instruction(line)
        instr_list.append(instr)
    return instr_list
