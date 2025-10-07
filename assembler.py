# assembler.py
# Versión 1.0 (binaria básica)

import re

class Assembler:
    def __init__(self):
        # Tabla de opcodes principales (según ISA.md)
        self.opcodes = {
            "ADD": 0x00, "SUB": 0x00, "MUL": 0x00, "DIV": 0x00, "MOD": 0x00,
            "AND": 0x01, "OR": 0x01, "XOR": 0x01, "NOT": 0x01,
            "ADDI": 0x03, "SUBI": 0x03, "ANDI": 0x03, "ORI": 0x03, "XORI": 0x03, "SLLI": 0x03, "LUI": 0x03,
            "LD": 0x04, "SD": 0x05,
            "BEQ": 0x06, "BNE": 0x06, "BLT": 0x06, "BGE": 0x06,
            "J": 0x07, "JAL": 0x07, "JR": 0x08,
            "NOP": 0x3F, "HALT": 0x3F
        }

        # Tabla funct para distinguir operaciones del mismo opcode
        self.funct = {
            "ADD": 0x00, "SUB": 0x01, "MUL": 0x02, "DIV": 0x03, "MOD": 0x04,
            "AND": 0x00, "OR": 0x01, "XOR": 0x02, "NOT": 0x03,
        }

    # ---------------------------
    # Utilidades de parsing
    # ---------------------------

    def reg_num(self, reg):
        """Convierte 'R5' -> 5"""
        return int(reg.strip().replace('R', ''))

    def imm_val(self, imm):
        """Convierte inmediato (decimal o hex) a int. Limpieza total."""
        imm = imm.strip().replace(",", "")
        # Quita cualquier carácter que no sea 0-9, A-F, x, X o -
        imm = re.sub(r"[^0-9A-Fa-fxX-]", "", imm)

        if imm.upper().startswith("-0X"):
            return -int(imm[3:], 16)
        elif imm.upper().startswith("0X"):
            return int(imm[2:], 16)
        else:
            return int(imm, 10)

    def assemble_line(self, line: str) -> int:
        """
        Ensambla una sola línea ASM -> instrucción de 32 bits.
        Retorna un entero (representa el binario).
        """
        # Eliminar comentarios y espacios
        line = line.split("#")[0].strip()
        if not line:
            return None

        # Dividir tokens y limpiar vacíos
        tokens = [t.strip() for t in re.split(r"[,\s]+", line) if t.strip()]
        mnemonic = tokens[0].upper()

        # Debug
        # if mnemonic == "LUI":
        #     print(f"[DEBUG] Tokens LUI -> {tokens}")

        if mnemonic not in self.opcodes:
            raise ValueError(f"Instrucción desconocida: {mnemonic}")

        opcode = self.opcodes[mnemonic]

        # Formatos simples: R, I, S, o System
        if mnemonic in ["ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "NOT"]:
            rd = self.reg_num(tokens[1])
            rs1 = self.reg_num(tokens[2])
            rs2 = self.reg_num(tokens[3]) if len(tokens) > 3 else 0
            funct = self.funct[mnemonic]
            binary = (opcode << 26) | (rs1 << 21) | (rs2 << 16) | (rd << 11) | (funct)
            return binary


        elif mnemonic in ["ADDI", "SUBI", "ANDI", "ORI", "XORI", "SLLI"]:
            rd = self.reg_num(tokens[1])
            rs1 = self.reg_num(tokens[2])
            imm = self.imm_val(tokens[3]) & 0xFFFF
            binary = (opcode << 26) | (rs1 << 21) | (rd << 16) | imm
            return binary

        elif mnemonic == "LUI":
            rd = self.reg_num(tokens[1])
            imm = self.imm_val(tokens[2]) & 0xFFFF
            binary = (self.opcodes["LUI"] << 26) | (rd << 16) | imm
            return binary

        elif mnemonic == "LD":
            rd = self.reg_num(tokens[1])
            # Formato tipo offset(base): 8(R1)
            offset, base = re.match(r"(\d+)\((R\d+)\)", tokens[2]).groups()
            rs1 = self.reg_num(base)
            offset_val = int(offset) & 0xFFFF
            binary = (opcode << 26) | (rs1 << 21) | (rd << 16) | offset_val
            return binary

        elif mnemonic == "SD":
            rs2 = self.reg_num(tokens[1])
            offset, base = re.match(r"(\d+)\((R\d+)\)", tokens[2]).groups()
            rs1 = self.reg_num(base)
            offset_val = int(offset) & 0xFFFF
            binary = (opcode << 26) | (rs1 << 21) | (rs2 << 16) | offset_val
            return binary

        elif mnemonic in ["HALT", "NOP"]:
            binary = (opcode << 26)
            return binary

        else:
            raise NotImplementedError(f"Instrucción {mnemonic} no soportada aún.")

    def assemble_file(self, filename: str) -> list[int]:
        """Ensambla un archivo completo (.asm)"""
        instructions = []
        with open(filename) as f:
            for line in f:
                try:
                    instr = self.assemble_line(line)
                    if instr is not None:
                        instructions.append(instr)
                except Exception as e:
                    print(f"Error en línea '{line.strip()}': {e}")
        return instructions

    def write_bin(self, instructions: list[int], outfile: str):
        """Guarda las instrucciones como texto binario"""
        with open(outfile, "w") as f:
            for instr in instructions:
                f.write(f"{instr:032b}\n")
        print(f"[OK] Archivo binario generado: {outfile}")

# ---------------------------
# Ejemplo de uso directo
# ---------------------------
if __name__ == "__main__":
    asm = Assembler()
    program = asm.assemble_file("testsASM/test1.asm")
    asm.write_bin(program, "out/test1.bin")
    print(f"Total de instrucciones ensambladas: {len(program)}")

