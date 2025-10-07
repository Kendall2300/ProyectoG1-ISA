from CPUTest import CPU

class Simulator:
    def __init__(self, bin_path):
        self.cpu = CPU()
        self.program = self._load_bin(bin_path)

    def _load_bin(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()
        return [int(line.strip(), 2) for line in lines if line.strip()]

    def run(self, debug=True):
        pc = 0
        while pc < len(self.program):
            instr = self.program[pc]
            opcode = (instr >> 26) & 0x3F

            # --- Decodificación por tipo ---
            if opcode in {0x00, 0x01, 0x02}:  # Formato R
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd = (instr >> 11) & 0x1F
                imm = 0

            elif opcode == 0x03:  # Formato I (ADDI, LUI, etc.)
                rs1 = (instr >> 21) & 0x1F
                rd = (instr >> 16) & 0x1F
                imm = instr & 0xFFFF
                rs2 = 0  # no aplica

            elif opcode in {0x04, 0x05}:  # Formato S (LD, SD)
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd = 0
                imm = instr & 0xFFFF

            elif opcode in {0x06}:  # Formato B (BEQ, etc.)
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd = 0
                imm = instr & 0xFFFF

            elif opcode in {0x07, 0x08}:  # Formato J
                rs1 = rs2 = rd = 0
                imm = instr & 0x3FFFFFF

            elif opcode == 0x3F:  # NOP / HALT
                rs1 = rs2 = rd = imm = 0

            else:
                rs1 = rs2 = rd = imm = 0  # default

            if debug:
                print(f"[PC={pc}] opcode={opcode:02X}, rs1=R{rs1}, rs2=R{rs2}, rd=R{rd}, imm={imm}")

            halted = self.cpu.execute(opcode, rs1, rs2, rd, imm)
            if halted:
                print("[HALT] Deteniendo simulación.")
                break

            pc += 1


if __name__ == "__main__":
    sim = Simulator("out/test1.bin") # Binario de salida
    sim.run(debug=True)
