# CPUTest.py
# CPU de prueba + vault + toy-hash (ToyMDMA) + signature ops

class RegisterFile:
    def __init__(self, num_registers=32):
        self._registers = [0] * num_registers  # 64-bit registers

    def read(self, idx):
        if idx == 0:
            return 0
        return self._registers[idx]

    def write(self, idx, value):
        if idx != 0:
            self._registers[idx] = value & 0xFFFFFFFFFFFFFFFF

class Memory:
    def __init__(self, size=1024*8):
        self.memory = bytearray(size)

    def write_word(self, addr, value):
        # addr is byte address
        for i in range(8):
            self.memory[addr + i] = (value >> (8 * i)) & 0xFF

    def read_word(self, addr):
        val = 0
        for i in range(8):
            val |= self.memory[addr + i] << (8 * i)
        return val

def rol64(x, n):
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x << n) | (x >> (64 - n))) & 0xFFFFFFFFFFFFFFFF

class CPU:
    def __init__(self):
        self.register_file = RegisterFile()
        self.memory = Memory()
        self.halted = False

        # Secure vault (VAULT[0..3]) and INIT[0..3]
        self.VAULT = [0]*4
        self.INIT = [0]*4

        # Hash state HS_A..HS_D
        self.HS = {
            'A': 0,
            'B': 0,
            'C': 0,
            'D': 0
        }

    def _debug_regs(self):
        # small helper
        regs = [self.register_file.read(i) for i in range(8)]
        print(" Regs[0..7]:", regs)

    def execute(self, opcode, rs1, rs2, rd, imm):
        print(f"[CPU] Ejecutando opcode={opcode:02X}, rs1=R{rs1}, rs2=R{rs2}, rd=R{rd}, imm={imm}")

        # --- Arithmetic / R-type (opcode 0x00, 0x01, 0x02 grouped by funct) ---
        if opcode == 0x00:  # ADD family (funct determines which)
            # For simplicity we assume funct==ADD here (we don't decode funct in this test CPU)
            val = self.register_file.read(rs1) + self.register_file.read(rs2)
            self.register_file.write(rd, val)
            print(f" [ADD] R{rd} = R{rs1} + R{rs2} = {val}")

        elif opcode == 0x01:  # logical family
            val = self.register_file.read(rs1) & self.register_file.read(rs2)
            self.register_file.write(rd, val)
            print(f" [AND] R{rd} = R{rs1} & R{rs2} = {val}")

        elif opcode == 0x02:
            # shift family (treat as SLL for test)
            val = (self.register_file.read(rs1) << (self.register_file.read(rs2) & 0x3F)) & 0xFFFFFFFFFFFFFFFF
            self.register_file.write(rd, val)
            print(f" [SLL] R{rd} = R{rs1} << R{rs2} = {val}")

        # --- I-type: LUI / ADDI (opcode 0x03) ---
        elif opcode == 0x03:
            # heuristic: if rs1==0 -> LUI else ADDI
            if rs1 == 0:
                val = (imm & 0xFFFF) << 48
                self.register_file.write(rd, val)
                print(f" [LUI] R{rd} = {hex(val)}")
            else:
                val = (self.register_file.read(rs1) + (imm & 0xFFFF)) & 0xFFFFFFFFFFFFFFFF
                self.register_file.write(rd, val)
                print(f" [ADDI] R{rd} = R{rs1} + {imm} = {val}")

        # --- Load / Store ---
        elif opcode == 0x04:  # LD
            base = self.register_file.read(rs1)
            addr = (base + imm) & 0xFFFFFFFFFFFFFFFF
            val = self.memory.read_word(addr)
            self.register_file.write(rd, val)
            print(f" [LD] R{rd} = MEM[{addr}] ({val})")

        elif opcode == 0x05:  # SD
            base = self.register_file.read(rs1)
            addr = (base + imm) & 0xFFFFFFFFFFFFFFFF
            val = self.register_file.read(rs2)
            self.memory.write_word(addr, val)
            print(f" [SD] MEM[{addr}] = R{rs2} ({val})")

        # --- Branches (simple stubs) ---
        elif opcode == 0x06:
            a = self.register_file.read(rs1)
            b = self.register_file.read(rs2)
            # for this simple CPU, just print
            print(f" [BRANCH] compare R{rs1}({a}) vs R{rs2}({b}), offset {imm} (not taken in test CPU)")

        # --- Jumps ---
        elif opcode == 0x07 or opcode == 0x08:
            print(" [JUMP] (not implemented in test CPU, simulator handles PC)")

        # --- Vault operations (opcode 0x10) ---
        elif opcode == 0x10:
            # We expect simulator to pack vidx in rs1, reg in rs2
            vidx = rs1 & 0x1F
            regn = rs2 & 0x1F
            # Distinguish VINIT (vidx used for INIT load) and VSTORE
            # If regn==0 meaning VINIT (simulator encodes differently); try to detect:
            if regn == 0:
                # VINIT: load INIT values to HS
                idx = vidx
                # for convenience, load INIT[0..3] -> HS_A..D
                self.HS['A'] = self.INIT[0]
                self.HS['B'] = self.INIT[1]
                self.HS['C'] = self.INIT[2]
                self.HS['D'] = self.INIT[3]
                print(f" [VINIT] Inicializó HS con INIT[0..3] = {self.INIT}")
            else:
                # VSTORE: store register value into vault slot (if vidx < 4)
                if 0 <= vidx < 4:
                    val = self.register_file.read(regn)
                    self.VAULT[vidx] = val & 0xFFFFFFFFFFFFFFFF
                    print(f" [VSTORE] VAULT[{vidx}] = R{regn} ({hex(val)})")
                else:
                    print(f" [VSTORE] vidx fuera de rango: {vidx}")

        # --- Hash family (opcode 0x11) ---
        elif opcode == 0x11:
            # Distinguish by presence of fields:
            # HBLOCK: rs1 holds register with 64-bit block
            # HMULK: rd, rs1 pattern
            # HMODP: rd, rs1 pattern
            # HFINAL: rd
            # To identify: if rd==0 and rs2==0 -> HBLOCK (we rely on simulator packing)
            if rd == 0 and rs2 == 0:
                # HBLOCK: process 64-bit value in register rs1
                block = self.register_file.read(rs1) & 0xFFFFFFFFFFFFFFFF
                # ToyMDMA as in ISA
                A = self.HS['A']; B = self.HS['B']; C = self.HS['C']; D = self.HS['D']
                f = (A & B) | ((~A) & C)
                g = (B & C) | ((~B) & D)
                h = A ^ B ^ C ^ D
                mul = (block * 0x9e3779b97f4a7c15) & 0xFFFFFFFFFFFFFFFF
                A = (rol64((A + f + mul) & 0xFFFFFFFFFFFFFFFF, 7) + B) & 0xFFFFFFFFFFFFFFFF
                B = (rol64((B + g + block) & 0xFFFFFFFFFFFFFFFF, 11) + (C * 3)) & 0xFFFFFFFFFFFFFFFF
                C = (rol64((C + h + mul) & 0xFFFFFFFFFFFFFFFF, 17) + (D % 0xFFFFFFFB)) & 0xFFFFFFFFFFFFFFFF
                D = (rol64((D + A + block) & 0xFFFFFFFFFFFFFFFF, 19) ^ ((f * 5) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
                self.HS['A'], self.HS['B'], self.HS['C'], self.HS['D'] = A, B, C, D
                print(f" [HBLOCK] Procesó bloque {hex(block)} -> HS_A..D = {[hex(A),hex(B),hex(C),hex(D)]}")
            else:
                # HMULK / HMODP / HFINAL: we detect HFINAL when rs1==0 and rd != 0?
                # For our assembler we used: HMULK rd, rs1 ; HMODP rd, rs1 ; HFINAL rd
                # We'll use rd!=0 and rs1!=0 -> HMULK/HMODP; HFINAL: rd !=0 and rs1==0
                if rs1 != 0 and rd != 0:
                    # Without funct decoding we can't separate HMULK/HMODP precisely — but assembler won't put them ambiguous.
                    # We'll use a simple heuristic: if operation placed rs1 in rs1 and rd in rd, HMULK multiplies rs1 by constant; HMODP modulo prime.
                    # We'll implement HMULK behavior (multiply by golden constant) when rs1 != 0
                    val = self.register_file.read(rs1)
                    # Try HMULK: rd = val * CONST
                    CONST = 0x9e3779b97f4a7c15 & 0xFFFFFFFFFFFFFFFF
                    res = (val * CONST) & 0xFFFFFFFFFFFFFFFF
                    self.register_file.write(rd, res)
                    print(f" [HMULK] R{rd} = R{rs1} * CONST = {hex(res)}")
                elif rs1 == 0 and rd != 0:
                    # HFINAL: extract HS to consecutive regs starting at rd
                    # rd -> HS_A, rd+1 -> HS_B, ...
                    a,b,c,d = self.HS['A'], self.HS['B'], self.HS['C'], self.HS['D']
                    self.register_file.write(rd, a)
                    self.register_file.write((rd+1)&0x1F, b)
                    self.register_file.write((rd+2)&0x1F, c)
                    self.register_file.write((rd+3)&0x1F, d)
                    print(f" [HFINAL] Escritura HS_A..D en R{rd}..R{(rd+3)&0x1F}")

        # --- Signature (opcode 0x12) ---
        elif opcode == 0x12:
            # VSIGN rd, vidx  -> vidx in rs1, rd in rd (simulator sets rs1=vidx, rs2=rd)
            vidx = rs1 & 0x1F
            target = rs2 & 0x1F
            # For VSIGN we expect register rd where to put signature; assembler used rd field in bits [20:16]
            # We'll support both: if target==0 then maybe rd was in rd field -> fallback to rd param
            if target != 0:
                rd_out = target
            else:
                rd_out = rd
            # Compose signature: XOR HS words with VAULT[vidx]
            if 0 <= vidx < len(self.VAULT):
                k = self.VAULT[vidx]
                a = self.HS['A'] ^ k
                b = self.HS['B'] ^ k
                c = self.HS['C'] ^ k
                d = self.HS['D'] ^ k
                # Store into rd_out .. rd_out+3
                self.register_file.write(rd_out, a)
                self.register_file.write((rd_out+1)&0x1F, b)
                self.register_file.write((rd_out+2)&0x1F, c)
                self.register_file.write((rd_out+3)&0x1F, d)
                print(f" [VSIGN] Firma en R{rd_out}..R{(rd_out+3)&0x1F} con VAULT[{vidx}]")
            else:
                print(f" [VSIGN] vidx fuera de rango: {vidx}")

        elif opcode == 0x3F:
            print(" [HALT] CPU detenida.")
            self.halted = True
            return True

        else:
            print(f"[WARN] Opcode {opcode:02X} no implementado")

        return self.halted
