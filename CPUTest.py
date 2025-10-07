class RegisterFile:
    def __init__(self, num_registers=32):
        self._registers = [0] * num_registers  # 64-bit registers

    def read(self, idx):
        if idx == 0:
            return 0  # R0 = 0 permanente
        return self._registers[idx]

    def write(self, idx, value):
        if idx != 0:
            self._registers[idx] = value & 0xFFFFFFFFFFFFFFFF  # 64-bit limit


class Memory:
    def __init__(self, size=1024):
        self.memory = bytearray(size)

    def write_word(self, addr, value):
        for i in range(8):
            self.memory[addr + i] = (value >> (8 * i)) & 0xFF

    def read_word(self, addr):
        val = 0
        for i in range(8):
            val |= self.memory[addr + i] << (8 * i)
        return val


class CPU:
    def __init__(self):
        self.register_file = RegisterFile()
        self.memory = Memory()
        self.pc = 0
        self.halted = False

    def execute(self, opcode, rs1, rs2, rd, imm):
        """
        CPU de prueba alineado con ISA del ensamblador:
        Opcode:
        0x00 = ADD
        0x03 = LUI / ADDI (tipo I simplificado)
        0x05 = SD
        0x3F = HALT
        """
        print(f"[CPU] Ejecutando opcode={opcode:02X}, rs1=R{rs1}, rs2=R{rs2}, rd=R{rd}, imm={imm}")

        # LUI o ADDI (comparten 0x03)
        if opcode == 0x03:
            # Heurística: si rs1 == 0 → es LUI, si no → es ADDI
            if rs1 == 0:
                val = imm << 48
                self.register_file.write(rd, val)
                print(f" [LUI] R{rd} = {hex(val)}")
            else:
                val = self.register_file.read(rs1) + imm
                self.register_file.write(rd, val)
                print(f" [ADDI] R{rd} = R{rs1} + {imm} = {val}")

        elif opcode == 0x00:  # ADD
            val = self.register_file.read(rs1) + self.register_file.read(rs2)
            self.register_file.write(rd, val)
            print(f" [ADD] R{rd} = R{rs1} + R{rs2} = {val}")

        elif opcode == 0x05:  # SD
            base = self.register_file.read(rs1)
            addr = base + imm
            val = self.register_file.read(rs2)
            self.memory.write_word(addr, val)
            print(f" [SD] MEM[{addr}] = R{rs2} ({val})")

        elif opcode == 0x3F:  # HALT
            print(" [HALT] CPU detenida.")
            self.halted = True
            return True

        else:
            print(f"[WARN] Opcode {opcode:02X} no implementado")

        return self.halted
