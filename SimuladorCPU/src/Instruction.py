R_TYPE_INSTRS = {"ADD", "SUB", "MUL", "DIV", "MOD", "AND", "OR", "XOR", "NOT", "SLL", "SRL", "ROL"}
I_TYPE_INSTRS = {"ADDI", "SUBI", "ANDI", "ORI", "XORI", "SLLI", "LUI"}
S_TYPE_INSTRS = {"LD", "SD"}
B_TYPE_INSTRS = {"BEQ", "BNE", "BLT", "BGE"}
VAULT_INSTRS = {"VSTORE", "VINIT"}
SYSTEM_TYPE_INSTRS = {"NOP", "HALT"}

class Instruction:
  def __init__(self, instr_str: str):
    tokens = instr_str.replace(',', ' ').strip().split()

    self.op = tokens[0].upper()

    # Operands
    self.rs1 = None
    self.rs2 = None
    self.rd = None
    self.immediate = None
    self.vidx = None
    self.rs = None

    if self.op in R_TYPE_INSTRS:
      # INSTR FORMAT: OP RD, RS1, RS2
      self.rd = tokens[1].strip()
      self.rs1 = tokens[2].strip(',')
      if self.op != "NOT":
        # NOT is a special case with only one source register
        self.rs2 = tokens[3].strip()
    
    elif self.op in I_TYPE_INSTRS:
      # INSTR FORMAT: OP RD, RS1, IMM
      self.rd = tokens[1].strip()
      self.rs1 = tokens[2].strip(',')
      self.immediate = int(tokens[3].strip())

    elif self.op in S_TYPE_INSTRS:
      # INSTR FORMAT: OP RS2, OFFSET(RS1) or OP RD, OFFSET(RS1)
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

    elif self.op in B_TYPE_INSTRS:
      # INSTR FORMAT: OP RS1, RS2, OFFSET
      self.rs1 = tokens[1].strip(',')
      self.rs2 = tokens[2].strip(',')
      self.immediate = int(tokens[3].strip())

    # Jump instructions
    elif self.op == "J":
      # INSTR FORMAT: J ADDR
      self.immediate = int(tokens[1].strip())

    elif self.op == "JAL":
      # INSTR FORMAT: JAL RD, ADDR
      self.rd = tokens[1].strip(',')
      self.immediate = int(tokens[2].strip())

    elif self.op == "JR":
      # INSTR FORMAT: JR RS1
      self.rs1 = tokens[1].strip()

    # System instructions
    elif self.op in SYSTEM_TYPE_INSTRS:
      # NOP and HALT have no operands
      pass

    # Vault/Hash/Signature instructions
    elif self.op in VAULT_INSTRS:
      # INSTR FORMAT: VSTORE VIDX
      self.vidx = int(tokens[1].strip())
      if self.op == "VSTORE":
        # INSTR FORMAT: VSTORE VIDX, RS1
        self.rs1 = tokens[2].strip()

    elif self.op == "HBLOCK":
      # INSTR FORMAT: HBLOCK RS1
      self.rs1 = tokens[1].strip()

    elif self.op == "HMULK" or self.op == "HMODP":
      # INSTR FORMAT: OP RD, RS1
      self.rd = tokens[1].strip(',')
      self.rs1 = tokens[2].strip()

    elif self.op == "HFINAL":
      # INSTR FORMAT: HFINAL RD
      self.rd = tokens[1].strip()

    elif self.op == "VSIGN":
      # INSTR FORMAT: VSIGN RD, VIDX
      self.rd = tokens[1].strip(',')
      self.vidx = int(tokens[2].strip())

    elif self.op == "VVERIF":
      # INSTR FORMAT: VVERIF RS, VIDX
      self.rs = tokens[1].strip(',')
      self.vidx = int(tokens[2].strip())

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
        return f"{self.op} {self.rd}, {self.immediate}({self.rs1})"
      return f"{self.op} {self.rs2}, {self.immediate}({self.rs1})"
    
    elif self.op in B_TYPE_INSTRS:
      return f"{self.op} {self.rs1}, {self.rs2}, {self.immediate}"
    
    elif self.op == "J":
      return f"{self.op} {self.immediate}"
    
    elif self.op == "JAL":
      return f"{self.op} {self.rd}, {self.immediate}"
    
    elif self.op == "JR":
      return f"{self.op} {self.rs1}"
    
    elif self.op in VAULT_INSTRS:
      if self.op == "VSTORE":
        return f"{self.op} {self.vidx}, {self.rs1}"
      return f"{self.op} {self.vidx}"
    
    elif self.op == "HBLOCK":
      return f"{self.op} {self.rs1}"
    
    elif self.op == "HMULK" or self.op == "HMODP":
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
    if not line or line.startswith('#'):  # Ignore empty lines and comments
      continue
    if line.endswith(':'):                # Ignore labels
      continue

    instr = Instruction(line)
    instr_list.append(instr)
  return instr_list