from RegisterFile import RegisterFile
from Memory import Memory
from HazardUnit import HazardUnit
from Instruction import Instruction, parse_instructions

class Pipeline:
  def __init__(self):
    # Components
    self.registers = RegisterFile()
    self.memory = Memory()
    self.hazard_unit = HazardUnit()
    
    # Console for UI logging
    self.console = None

    # Instructions and Labels
    self.instructions: list[Instruction] = []
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
    self.on_cycle = None

  def set_console(self, console) -> None:
    """
    Sets the console for logging messages.
    """
    self.console = console

  def _log(self, message: str) -> None:
    """
    Logs a message to the UI console if available, otherwise prints to stdout.
    """
    if self.console:
      self.console.log(message)
    else:
      print(message)

  def map_labels(self, lines: str) -> dict[str, int]:
    """
    Maps labels to their corresponding instruction indices.
    
    Args:
        lines (str): List of instruction lines.

    Returns:
        dict[str, int]: A dictionary mapping labels to instruction indices.
    """
    labels = {}
    instr_list = []
    idx = 0
    for line in lines:
      line = line.strip()
      if not line or line.startswith('#'):  # Ignore empty lines and comments
        continue
      if line.endswith(':'):                # Add label
        label = line[:-1].strip()
        labels[label] = idx
      else:                                 # Add instruction
        instr_list.append(line)
        idx += 1
    self.instructions = parse_instructions(instr_list)
    return labels
  
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
    instr = self.IF_ID["instr"]
    if instr:
      # Read register values with forwarding
      if instr.rs1:
        instr.rs1_val = self._get_register_value_with_forwarding(instr.rs1)

      if instr.rs2:
        instr.rs2_val = self._get_register_value_with_forwarding(instr.rs2)

      # Only check for load-use hazards (most critical)
      if (self.ID_EX["instr"] and self.ID_EX["instr"].op == "LD" and 
          ((instr.rs1 and self.ID_EX["instr"].rd == instr.rs1) or 
           (instr.rs2 and self.ID_EX["instr"].rd == instr.rs2))):
        self._log(f"[HAZARD] Load-use hazard: {instr} depends on load {self.ID_EX['instr']} - stalling")
        self.ID_EX["instr"] = None
        return
        
      # Check for other hazards (for metrics only, don't stall)
      if self.EX_MEM["instr"]:
        hazard = self.hazard_unit.detect_hazard_waw_war(instr, self.EX_MEM["instr"])
        if hazard == "WAW":
          self.metrics["WAW"] += 1
        elif hazard == "WAR":
          self.metrics["WAR"] += 1
          
      self.ID_EX["instr"] = instr

    else:
      self.ID_EX["instr"] = None
  
  def _get_register_value_with_forwarding(self, reg_name: str) -> int:
    """
    Gets register value with forwarding from later pipeline stages.
    """
    # Check if we can forward from MEM stage
    if (self.EX_MEM["instr"] and self.EX_MEM["instr"].rd == reg_name and 
        hasattr(self.EX_MEM["instr"], 'result') and self.EX_MEM["instr"].result is not None):
      self._log(f"[FORWARD] Forwarding {self.EX_MEM['instr'].result} from EX/MEM stage for {reg_name}")
      return self.EX_MEM["instr"].result
    
    # Check if we can forward from WB stage  
    if (self.MEM_WB["instr"] and self.MEM_WB["instr"].rd == reg_name):
      if hasattr(self.MEM_WB["instr"], 'result') and self.MEM_WB["instr"].result is not None:
        self._log(f"[FORWARD] Forwarding {self.MEM_WB['instr'].result} from MEM/WB stage for {reg_name}")
        return self.MEM_WB["instr"].result
      elif hasattr(self.MEM_WB["instr"], 'loaded_value') and self.MEM_WB["instr"].loaded_value is not None:
        self._log(f"[FORWARD] Forwarding loaded value {self.MEM_WB['instr'].loaded_value} from MEM/WB stage for {reg_name}")
        return self.MEM_WB["instr"].loaded_value
    
    # Default: read from register file
    return self.registers.read(reg_name)

  def execute(self):
    """ 
    Executes the instruction in the EX stage.
    """
    instr = self.ID_EX["instr"]
    if instr:
      if instr.op == "ADD":
        instr.result = instr.rs1_val + instr.rs2_val
      elif instr.op == "SUB":
        instr.result = instr.rs1_val - instr.rs2_val
      elif instr.op == "MUL":
        instr.result = instr.rs1_val * instr.rs2_val
      elif instr.op == "DIV":
        instr.result = instr.rs1_val // instr.rs2_val
      elif instr.op == "MOD":
        instr.result = instr.rs1_val % instr.rs2_val

      elif instr.op == "AND":
        instr.result = instr.rs1_val & instr.rs2_val
      elif instr.op == "OR":
        instr.result = instr.rs1_val | instr.rs2_val
      elif instr.op == "XOR":
        instr.result = instr.rs1_val ^ instr.rs2_val
      elif instr.op == "NOT":
        instr.result = ~instr.rs1_val

      elif instr.op == "SLL":
        instr.result = instr.rs1_val << instr.rs2_val
      elif instr.op == "SRL":
        instr.result = instr.rs1_val >> instr.rs2_val
      elif instr.op == "ROL":
        instr.result = ((instr.rs1_val << instr.rs2_val) | (instr.rs1_val >> (32 - instr.rs2_val))) & 0xFFFFFFFF

      elif instr.op == "ADDI":
        instr.result = instr.rs1_val + instr.immediate
      elif instr.op == "SUBI":
        instr.result = instr.rs1_val - instr.immediate
      elif instr.op == "ANDI":
        instr.result = instr.rs1_val & instr.immediate
      elif instr.op == "ORI":
        instr.result = instr.rs1_val | instr.immediate
      elif instr.op == "XORI":
        instr.result = instr.rs1_val ^ instr.immediate
      elif instr.op == "SLLI":
        instr.result = instr.rs1_val << instr.immediate
      elif instr.op == "LUI":
        instr.result = instr.immediate << 48

      elif instr.op == "LD":
        instr.address = instr.rs1_val + instr.immediate
      elif instr.op == "SD":
        instr.address = instr.rs1_val + instr.immediate

      elif instr.op in {"BEQ", "BNE", "BLT", "BGE"}:
        taken = False
        if instr.op == "BGE":
          taken = (instr.rs1_val >= instr.rs2_val)
        elif instr.op == "BLT":
          taken = (instr.rs1_val < instr.rs2_val)
        elif instr.op == "BNE":
          taken = (instr.rs1_val != instr.rs2_val)
        elif instr.op == "BEQ":
          taken = (instr.rs1_val == instr.rs2_val)

        predicted = False
        self.hazard_unit.update_control_hazard(taken, predicted)

        if taken:
          target = instr.immediate
          if target in self.labels:
            self.PC = self.labels[target]
          else:
            self.PC += int(target)

      elif instr.op == "J":
        target = instr.immediate
        if target in self.labels:
          self.PC = self.labels[target]

      elif instr.op == "JAL":
        instr.result = self.PC + 4
        target = instr.immediate
        if target in self.labels:
          self.PC = self.labels[target]

      elif instr.op == "JR":
        target = instr.rs1_val
        if target in self.labels:
          self.PC = self.labels[target]
      
      # More instructions can be added here..

      self.EX_MEM["instr"] = instr 
    else:
      self.EX_MEM["instr"] = None

  def memory_access(self):
    """
    Accesses memory for load and store instructions.
    """
    instr = self.EX_MEM["instr"]
    if instr:
      if instr.op == "LD":
        instr.loaded_value = self.memory.load_word(instr.address)

      elif instr.op == "SD":
        self.memory.store_word(instr.address, instr.rs2_val)
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
        if instr.op in instr.R_TYPE_INSTRS and instr.rd is not None:
          self._log(f"[WB] Writing {instr.result} to {instr.rd} ({instr.op})")
          self.registers.write(instr.rd, instr.result)
        elif instr.op in instr.I_TYPE_INSTRS and instr.rd is not None:
          self._log(f"[WB] Writing {instr.result} to {instr.rd} ({instr.op})")
          self.registers.write(instr.rd, instr.result)
        elif instr.op == "LD" and instr.rd is not None:
          self._log(f"[WB] Loading {instr.loaded_value} to {instr.rd} (LD)")
          self.registers.write(instr.rd, instr.loaded_value)
        elif instr.op == "JAL" and instr.rd is not None:
          self._log(f"[WB] Writing {instr.result} to {instr.rd} (JAL)")
          self.registers.write(instr.rd, instr.result)
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

    cycle_info = {
        "IF": self.IF_ID["instr"],
        "ID": self.ID_EX["instr"],
        "EX": self.EX_MEM["instr"],
        "MEM": self.MEM_WB["instr"],
        "WB": self.MEM_WB.get("old_instr"),
    }
    self.execution_history.append(cycle_info)

    self.MEM_WB["old_instr"] = None

    if self.on_cycle:
      try:
        self.on_cycle(self)
      except Exception as e:
        self._log(f"[ERROR on_cycle callback] Error: {e}")


      
          


