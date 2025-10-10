from CPU.RegisterFile import RegisterFile
from CPU.Memory import Memory
from CPU.HazardUnit import HazardUnit


class Pipeline:
  def __init__(self):
    # Components
    self.registers = RegisterFile()
    self.memory = Memory()
    self.hazard_unit = HazardUnit()
    
    # Console for UI logging
    self.console = None

    # Instructions and Labels
    self.instructions: list[int] = []
    self.labels: dict[str, int] = {}

    # Pipeline registers
    self.IF_ID = {"instr": None}
    self.ID_EX = {"instr": None}
    self.EX_MEM = {"instr": None}
    self.MEM_WB = {"instr": None}

    # Program Counter
    self.PC = 0

    # Metrics
    self.cycle_count = 0
    self.metrics = {
        "Cycles": 0,
        "RAW": 0,
        "WAR": 0,
        "WAW": 0,
        "Control Hazards": 0,
        "Branches": 0,
    }
    self.execution_history = []
    self.cycle_logs = []  # Logs para el ciclo actual
    self.on_cycle = None

  def load_instructions(self, bin_path: str) -> None:
    """
    Loads a binary file into the instruction memory.
    
    Args:
        bin_path (str): Path to the binary file.
    """
    with open(bin_path, 'r') as f:
      lines = f.readlines()
    self.instructions = [int(line.strip(), 2) for line in lines if line.strip()]

  def _log(self, message: str) -> None:
    """
    Logs a message to the UI console if available, otherwise prints to terminal.
    """
    if self.console:
      self.console.log(message)
    else:
      print(message)
  
  def fetch(self) -> None:
    """ 
    Fetches the next instruction from memory.
    """
    if self.PC < len(self.instructions):
      self.IF_ID["instr"] = self.instructions[self.PC]
      self.PC += 1
    else:
      self.IF_ID["instr"] = None

  def decode(self) -> None:
    """ 
    Decodes the instruction in the ID stage.
    """
    raw_instr = self.IF_ID["instr"]
    if raw_instr is not None:
      # Create decoded instruction structure
      decoded_instr = {
        'raw': raw_instr,
        'opcode': (raw_instr >> 26) & 0x3F,
        'rs1': 0,
        'rs2': 0, 
        'rd': 0,
        'imm': 0,
        'rs1_val': 0,
        'rs2_val': 0,
        'result': None,
        'address': None,
        'loaded_value': None,
        'instruction_type': None,
        'mnemonic': 'UNKNOWN'
      }
      
      opcode = decoded_instr['opcode']
      
      # Decode based on opcode
      if opcode in {0x00, 0x01, 0x02}:  # R-type
        decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F
        decoded_instr['rs2'] = (raw_instr >> 16) & 0x1F  
        decoded_instr['rd'] = (raw_instr >> 11) & 0x1F
        decoded_instr['instruction_type'] = 'R'
        
        # Determine specific R-type operation from func field
        func = raw_instr & 0x3F
        if opcode == 0x00:  # ALU operations
          if func == 0x00: decoded_instr['mnemonic'] = 'ADD'
          elif func == 0x01: decoded_instr['mnemonic'] = 'SUB'
          elif func == 0x02: decoded_instr['mnemonic'] = 'MUL'
          elif func == 0x03: decoded_instr['mnemonic'] = 'DIV'
          elif func == 0x04: decoded_instr['mnemonic'] = 'MOD'
        elif opcode == 0x01:  # Logic operations
          if func == 0x00: decoded_instr['mnemonic'] = 'AND'
          elif func == 0x01: decoded_instr['mnemonic'] = 'OR'
          elif func == 0x02: decoded_instr['mnemonic'] = 'XOR'
          elif func == 0x03: decoded_instr['mnemonic'] = 'NOT'
        elif opcode == 0x02:  # Shift operations
          if func == 0x00: decoded_instr['mnemonic'] = 'SLL'
          elif func == 0x01: decoded_instr['mnemonic'] = 'SRL'
          elif func == 0x02: decoded_instr['mnemonic'] = 'ROL'

      elif opcode == 0x03:  # I-type
        decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F
        decoded_instr['rd'] = (raw_instr >> 16) & 0x1F
        decoded_instr['imm'] = raw_instr & 0xFFFF
        decoded_instr['instruction_type'] = 'I'
        
        # For I-type with opcode 0x03, we need to distinguish by examining the instruction pattern
        # Since the assembler uses the same opcode for all I-type arithmetic, we need another way
        # Looking at the actual instruction patterns or use a different encoding
        # For now, assume all 0x03 opcodes are ADDI (this needs to be fixed in assembler)
        decoded_instr['mnemonic'] = 'ADDI'

      elif opcode == 0x04:  # LD
        decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F
        decoded_instr['rd'] = (raw_instr >> 16) & 0x1F
        decoded_instr['imm'] = raw_instr & 0xFFFF
        decoded_instr['instruction_type'] = 'I'
        decoded_instr['mnemonic'] = 'LD'

      elif opcode == 0x05:  # SD
        decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F
        decoded_instr['rs2'] = (raw_instr >> 16) & 0x1F
        decoded_instr['imm'] = raw_instr & 0xFFFF
        decoded_instr['instruction_type'] = 'S'
        decoded_instr['mnemonic'] = 'SD'

      elif opcode == 0x06:  # B-type CHECK
        decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F
        decoded_instr['rs2'] = (raw_instr >> 16) & 0x1F
        decoded_instr['imm'] = raw_instr & 0xFFFF
        decoded_instr['instruction_type'] = 'B'
        
        func = (raw_instr >> 11) & 0x1F
        if func == 0x00: decoded_instr['mnemonic'] = 'BEQ'
        elif func == 0x01: decoded_instr['mnemonic'] = 'BNE'
        elif func == 0x02: decoded_instr['mnemonic'] = 'BLT'
        elif func == 0x03: decoded_instr['mnemonic'] = 'BGE'

      elif opcode in {0x07, 0x08}:  # J-type CHECK
        decoded_instr['imm'] = raw_instr & 0x3FFFFFF
        decoded_instr['instruction_type'] = 'J'
        if opcode == 0x07: decoded_instr['mnemonic'] = 'J'
        elif opcode == 0x08: 
          decoded_instr['mnemonic'] = 'JR'
          decoded_instr['rs1'] = (raw_instr >> 21) & 0x1F

      elif opcode == 0x3F:  # System (HALT/NOP)
        decoded_instr['instruction_type'] = 'SYS'
        # For HALT, all lower bits should be 0. For NOP, check pattern.
        if raw_instr == 0xFC000000:  # HALT pattern from assembler
          decoded_instr['mnemonic'] = 'HALT'
        else:
          decoded_instr['mnemonic'] = 'NOP'

      # Read register values with forwarding
      if decoded_instr['rs1'] != 0:
        decoded_instr['rs1_val'] = self._get_register_value_with_forwarding(decoded_instr['rs1'])

      if decoded_instr['rs2'] != 0:
        decoded_instr['rs2_val'] = self._get_register_value_with_forwarding(decoded_instr['rs2'])
      
      self.ID_EX["instr"] = decoded_instr

    else:
      self.ID_EX["instr"] = None
  
  def _get_register_value_with_forwarding(self, reg_num: int) -> int:
    """
    Gets register value with forwarding from later pipeline stages.
    """
    # Register 0 is always 0
    if reg_num == 0:
      return 0
      
    # Check if we can forward from EX/MEM stage
    if (self.EX_MEM["instr"] and self.EX_MEM["instr"]['rd'] == reg_num and 
        self.EX_MEM["instr"]['result'] is not None):
      return self.EX_MEM["instr"]['result']
    
    # Check if we can forward from MEM/WB stage  
    if (self.MEM_WB["instr"] and self.MEM_WB["instr"]['rd'] == reg_num):
      if self.MEM_WB["instr"]['result'] is not None:
        return self.MEM_WB["instr"]['result']
      elif self.MEM_WB["instr"]['loaded_value'] is not None:
        return self.MEM_WB["instr"]['loaded_value']
    
    # Default: read from register file
    return self.registers.read(f"R{reg_num}")

  def execute(self):
    """ 
    Executes the instruction in the EX stage.
    """
    instr = self.ID_EX["instr"]
    if instr:
      mnemonic = instr['mnemonic']
      
      # ALU Operations (R-type and I-type)
      if mnemonic == "ADD":
        instr['result'] = instr['rs1_val'] + instr['rs2_val']
        self.registers.update_flags(instr['result'], instr['rs1_val'], instr['rs2_val'], 'add')
      elif mnemonic == "SUB":
        instr['result'] = instr['rs1_val'] - instr['rs2_val']
        self.registers.update_flags(instr['result'], instr['rs1_val'], instr['rs2_val'], 'sub')
      elif mnemonic == "MUL":
        instr['result'] = instr['rs1_val'] * instr['rs2_val']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "DIV":
        instr['result'] = instr['rs1_val'] // instr['rs2_val'] if instr['rs2_val'] != 0 else 0
        self.registers.update_flags(instr['result'])
      elif mnemonic == "MOD":
        instr['result'] = instr['rs1_val'] % instr['rs2_val'] if instr['rs2_val'] != 0 else 0
        self.registers.update_flags(instr['result'])

      # Logic Operations
      elif mnemonic == "AND":
        instr['result'] = instr['rs1_val'] & instr['rs2_val']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "OR":
        instr['result'] = instr['rs1_val'] | instr['rs2_val']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "XOR":
        instr['result'] = instr['rs1_val'] ^ instr['rs2_val']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "NOT":
        instr['result'] = ~instr['rs1_val'] & 0xFFFFFFFF
        self.registers.update_flags(instr['result'])

      # Shift Operations
      elif mnemonic == "SLL":
        instr['result'] = (instr['rs1_val'] << instr['rs2_val']) & 0xFFFFFFFF
        self.registers.update_flags(instr['result'])
      elif mnemonic == "SRL":
        instr['result'] = instr['rs1_val'] >> instr['rs2_val']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "ROL":
        shift = instr['rs2_val'] & 0x1F  # Only use bottom 5 bits
        instr['result'] = ((instr['rs1_val'] << shift) | (instr['rs1_val'] >> (32 - shift))) & 0xFFFFFFFF
        self.registers.update_flags(instr['result'])

      # Immediate Operations
      elif mnemonic == "ADDI":
        instr['result'] = instr['rs1_val'] + instr['imm']
        self.registers.update_flags(instr['result'], instr['rs1_val'], instr['imm'], 'addi')
      elif mnemonic == "SUBI":
        instr['result'] = instr['rs1_val'] - instr['imm']
        self.registers.update_flags(instr['result'], instr['rs1_val'], instr['imm'], 'subi')
      elif mnemonic == "ANDI":
        instr['result'] = instr['rs1_val'] & instr['imm']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "ORI":
        instr['result'] = instr['rs1_val'] | instr['imm']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "XORI":
        instr['result'] = instr['rs1_val'] ^ instr['imm']
        self.registers.update_flags(instr['result'])
      elif mnemonic == "SLLI":
        instr['result'] = (instr['rs1_val'] << instr['imm']) & 0xFFFFFFFF
        self.registers.update_flags(instr['result'])
      elif mnemonic == "LUI":
        instr['result'] = (instr['imm'] << 16) & 0xFFFFFFFF
        self.registers.update_flags(instr['result'])

      # Memory Operations
      elif mnemonic == "LD":
        instr['address'] = instr['rs1_val'] + instr['imm']
      elif mnemonic == "SD":
        instr['address'] = instr['rs1_val'] + instr['imm']

      # Branch Operations
      elif mnemonic in {"BEQ", "BNE", "BLT", "BGE"}:
        taken = False
        if mnemonic == "BGE":
          taken = (instr['rs1_val'] >= instr['rs2_val'])
        elif mnemonic == "BLT":
          taken = (instr['rs1_val'] < instr['rs2_val'])
        elif mnemonic == "BNE":
          taken = (instr['rs1_val'] != instr['rs2_val'])
        elif mnemonic == "BEQ":
          taken = (instr['rs1_val'] == instr['rs2_val'])

        predicted = False
        self.hazard_unit.update_control_hazard(taken, predicted)

        if taken:
          # Branch target is PC-relative
          self.PC = self.PC + instr['imm'] - 1  # -1 because PC will be incremented in fetch

      # Jump Operations
      elif mnemonic == "J":
        self.PC = instr['imm']
      elif mnemonic == "JAL":
        instr['result'] = self.PC + 4  # Store return address
        self.PC = instr['imm']
      elif mnemonic == "JR":
        self.PC = instr['rs1_val']

      # System Operations
      elif mnemonic == "HALT":
        self._log("[EXECUTE] HALT instruction executed")
        # Could set a halt flag here
        
      elif mnemonic == "NOP":
        pass  # Do nothing

      self.EX_MEM["instr"] = instr 
    else:
      self.EX_MEM["instr"] = None

  def memory_access(self):
    """
    Accesses memory for load and store instructions.
    """
    instr = self.EX_MEM["instr"]
    if instr:
      mnemonic = instr['mnemonic']
      
      if mnemonic == "LD":
        instr['loaded_value'] = self.memory.load_word(instr['address'])

      elif mnemonic == "SD":
        self.memory.store_word(instr['address'], instr['rs2_val'])
        
      self.MEM_WB["instr"] = instr
    else:
      self.MEM_WB["instr"] = None

  def write_back(self):
    """
    Writes the result of the instruction back to the register file.
    """
    instr = self.MEM_WB["instr"]
    if instr:
      try:
        mnemonic = instr['mnemonic']
        rd = instr['rd']
        
        # Only write to register if rd != 0 (register 0 is always 0)
        if rd != 0:
          if instr['instruction_type'] in ['R', 'I'] and instr['result'] is not None:
            self.registers.write(f"R{rd}", instr['result'])
            
          elif mnemonic == "LD" and instr['loaded_value'] is not None:
            self.registers.write(f"R{rd}", instr['loaded_value'])
            
          elif mnemonic == "JAL" and instr['result'] is not None:
            self.registers.write(f"R{rd}", instr['result'])
          
      except Exception as e:
        self._log(f"[ERROR WB] Instruction: {instr}, Error: {e}")

    self.MEM_WB["old_instr"] = self.MEM_WB["instr"]

    # Update metrics
    self.metrics["Cycles"] = self.cycle_count
    self.metrics["RAW"] = self.hazard_unit.RAW
    self.metrics["WAR"] = self.hazard_unit.WAR
    self.metrics["WAW"] = self.hazard_unit.WAW
    self.metrics["Control Hazards"] = self.hazard_unit.control
    self.metrics["Branches"] = self.hazard_unit.get_branch_accuracy()

  def step(self):
    """
    Executes one cycle of the pipeline.
    """
    self.cycle_count += 1
    self.active_stages = []

    self.write_back()
    if self.MEM_WB["instr"]:
      self.active_stages.append("WB")

    self.memory_access()
    if self.EX_MEM["instr"]:
      self.active_stages.append("MEM")

    self.execute()
    if self.ID_EX["instr"]:
      self.active_stages.append("EX")

    self.decode()
    if self.IF_ID["instr"]:
      self.active_stages.append("ID")

    self.fetch()
    if self.PC < len(self.instructions):
      self.active_stages.append("IF")

    # Create readable cycle info for history
    def format_instr_for_display(instr):
      if instr is None:
        return None
      
      elif isinstance(instr, dict):
        mnemonic = instr['mnemonic']
        
        # Format instruction with full operands
        if instr['instruction_type'] == 'R':
          if mnemonic == 'NOT':
            formatted = f"{mnemonic} R{instr['rd']}, R{instr['rs1']}"
          else:
            formatted = f"{mnemonic} R{instr['rd']}, R{instr['rs1']}, R{instr['rs2']}"
            
        elif instr['instruction_type'] == 'I':
          if mnemonic == 'LD':
            formatted = f"{mnemonic} R{instr['rd']}, {instr['imm']}(R{instr['rs1']})"
          else:
            formatted = f"{mnemonic} R{instr['rd']}, R{instr['rs1']}, {instr['imm']}"
            
        elif instr['instruction_type'] == 'S':
          formatted = f"{mnemonic} R{instr['rs2']}, {instr['imm']}(R{instr['rs1']})"
          
        elif instr['instruction_type'] == 'B':
          formatted = f"{mnemonic} R{instr['rs1']}, R{instr['rs2']}, {instr['imm']}"
          
        elif instr['instruction_type'] == 'J':
          if mnemonic == 'JAL':
            formatted = f"{mnemonic} R{instr['rd']}, {instr['imm']}"
          elif mnemonic == 'JR':
            formatted = f"{mnemonic} R{instr['rs1']}"
          else:  # J
            formatted = f"{mnemonic} {instr['imm']}"
            
        elif instr['instruction_type'] == 'SYS':
          formatted = mnemonic  # HALT, NOP no tienen operandos
          
        else:
          formatted = mnemonic  # Fallback
          
        return f"{formatted} (0x{instr['raw']:08X})"
      else:
        return f"Raw: 0x{instr:08X}"
    
    cycle_info = {
        "cycle": self.cycle_count,
        "PC": self.PC,
        "IF": format_instr_for_display(self.IF_ID["instr"]),
        "ID": format_instr_for_display(self.ID_EX["instr"]),
        "EX": format_instr_for_display(self.EX_MEM["instr"]),
        "MEM": format_instr_for_display(self.MEM_WB["instr"]),
        "WB": format_instr_for_display(self.MEM_WB.get("old_instr")),
        "logs": self.cycle_logs.copy()  # Copia de los logs de este ciclo
    }
    self.execution_history.append(cycle_info)

    self.MEM_WB["old_instr"] = None

    if self.on_cycle:
      try:
        self.on_cycle(self)
      except Exception as e:
        self._log(f"[ERROR on_cycle callback] Error: {e}")
