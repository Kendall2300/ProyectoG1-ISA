# simulator.py
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

            # decode according to opcode family
            if opcode in {0x00, 0x01, 0x02}:  # R-type
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd  = (instr >> 11) & 0x1F
                imm = 0

            elif opcode == 0x03:  # I-type (ADDI, LUI, ...)
                rs1 = (instr >> 21) & 0x1F
                rd  = (instr >> 16) & 0x1F
                rs2 = 0
                imm = instr & 0xFFFF

            elif opcode in {0x04, 0x05}:  # S-type (LD, SD)
                rs1 = (instr >> 21) & 0x1F   # base
                rs2 = (instr >> 16) & 0x1F   # rt / source
                rd  = 0
                imm = instr & 0xFFFF

            elif opcode == 0x06:  # B-type
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd  = 0
                imm = instr & 0xFFFF

            elif opcode in {0x07, 0x08}:  # J-type
                rs1 = rs2 = rd = 0
                imm = instr & 0x3FFFFFF

            elif opcode == 0x10:  # Vault ops: VSTORE/VINIT
                # We encoded vidx in bits [25:21], reg in [20:16] for VSTORE
                vidx = (instr >> 21) & 0x1F
                reg  = (instr >> 16) & 0x1F
                # choose semantics: for simulator: rs1 = vidx, rs2 = reg
                rs1 = vidx
                rs2 = reg
                rd  = 0
                imm = 0

            elif opcode == 0x11:  # Hash family (HBLOCK, HMULK, HMODP, HFINAL)
                # HBLOCK uses rs1 in bits [25:21]
                rs1 = (instr >> 21) & 0x1F
                rs2 = (instr >> 16) & 0x1F
                rd  = (instr >> 16) & 0x1F
                imm = instr & 0xFFFF

            elif opcode == 0x12:  # Signature family (VSIGN, VVERIF)
                # VSIGN encoded vidx in [25:21], rd in [20:16]; VVERIF encoded vidx in [25:21], rs in [20:16]
                rs1 = (instr >> 21) & 0x1F   # vidx
                rs2 = (instr >> 16) & 0x1F   # payload reg or rd depending
                rd  = (instr >> 16) & 0x1F
                imm = 0

            elif opcode == 0x3F:  # System
                rs1 = rs2 = rd = imm = 0

            else:
                rs1 = rs2 = rd = imm = 0

            if debug:
                print(f"[PC={pc}] opcode={opcode:02X}, rs1=R{rs1}, rs2=R{rs2}, rd=R{rd}, imm={imm}")

            halted = self.cpu.execute(opcode, rs1, rs2, rd, imm)
            if halted:
                print("[HALT] Deteniendo simulación.")
                break

            pc += 1

if __name__ == "__main__":
    sim = Simulator("out/test2.bin")
    sim.run(debug=True)
