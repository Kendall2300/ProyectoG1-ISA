class RegisterFile:
  # Constants:
  # --- General Purpose Registers (GPR) ---
  GPR_REG_SIZE = 64                     # Size of general purpose registers in bits
  GPR_NUM_REGS = 32                     # Number of general purpose registers
  # --- Special Registers ---
  PC_REG_SIZE = 64                      # Size of Program Counter register in bits
  FLAGS_REG_SIZE = 8                    # Size of Flags register in bits
  # --- Secure Vault ---
  VAULT_NUM_KEYS = 4                    # Number of keys in the vault
  SECURE_VAULT_REG_SIZE = 64            # Size of secure vault registers in bits
  INIT_REG_SIZE = 64                    # Size of init registers in bits
  # --- Hash Function ---
  HASH_VALUES = ['A', 'B', 'C', 'D']    # Initial hash values for the hash function
  HASH_REG_SIZE = 64                    # Size of hash function registers in bits

  def __init__(self):
    # General purpose registers R0-R31
    self.regs = list(range(self.GPR_NUM_REGS))                                                               # GPR registers
    self.regs[0] = 0            

    # Special registers
    # self._PC = bitarray('0' * self.PC_REG_SIZE)                                                            # Program Counter
    self._FLAGS = 0                                                                                          # Flags register (8-bit integer)

    # Secure Vault registers
    # self._VAULT = {f'KEY{i}': bitarray('0' * self.SECURE_VAULT_REG_SIZE) for i in range(self.VAULT_NUM_KEYS)}   # Vault register
    # self._INIT = {f'{value}': bitarray('0' * self.INIT_REG_SIZE) for value in self.HASH_VALUES}                 # Hash init values registers

    # # Internal Hash State registers
    # self._HASH_STATE = {f'HS_{value}': bitarray('0' * self.HASH_REG_SIZE) for value in self.HASH_VALUES}        # Hash state registers

  def read(self, reg_name: str):                                                 
    """
    Reads the value of a specified GPR register.

    Args:
        reg_name (str): The name of the register to read (e.g., 'R0', 'R1', ..., 'R31').

    Returns:
        int: The value of the specified register as an integer.
    """
    idx = int(reg_name.strip().lower().replace('r', ''))
    if idx == 0:
      return 0
    
    return self.regs[idx]
  
  def write(self, reg_name: str, value: int) -> None: 
    """
    Writes a value to a specified GPR register.

    Args:
        reg_name (str): The name of the register to write to (e.g., 'R0', 'R1', ..., 'R31').
        value (int): The value to write to the register.
    """
    idx = int(reg_name.strip().lower().replace('r', ''))
    if idx == 0:
      return

    self.regs[idx] = value

  # FLAGS register methods
  def read_flags(self) -> int:
    """
    Reads the value of the Flags register.
    
    Returns:
        int: The value of the Flags register as an 8-bit integer.
    """
    return self._FLAGS
  
  def write_flags(self, value: int) -> None:
    """
    Writes a value to the Flags register.

    Args:
        value (int): The value to write to the Flags register (must be an 8-bit unsigned integer).
        
    Raises:
        ValueError: If the value is not an 8-bit unsigned integer.
    """
    if not (0 <= value < 2**self.FLAGS_REG_SIZE):
      raise ValueError("Value must be an 8-bit unsigned integer.")
    
    self._FLAGS = value

  def get_flag(self, flag_bit: int) -> bool:
    """
    Gets the value of a specific flag bit.
    
    Args:
        flag_bit (int): The bit position (0-7)
                       0: Zero, 1: Negative, 2: Carry, 3: Overflow, 4-7: Reserved
    
    Returns:
        bool: True if the flag is set, False otherwise.
    """
    if not (0 <= flag_bit <= 7):
      raise ValueError("Flag bit must be between 0 and 7.")
    
    return bool(self._FLAGS & (1 << flag_bit))

  def set_flag(self, flag_bit: int, value: bool = True) -> None:
    """
    Sets or clears a specific flag bit.
    
    Args:
        flag_bit (int): The bit position (0-7)
                       0: Zero, 1: Negative, 2: Carry, 3: Overflow, 4-7: Reserved
        value (bool): True to set the flag, False to clear it.
    """
    if not (0 <= flag_bit <= 7):
      raise ValueError("Flag bit must be between 0 and 7.")
    
    if value:
      self._FLAGS |= (1 << flag_bit)  # Set bit
    else:
      self._FLAGS &= ~(1 << flag_bit)  # Clear bit

  def clear_flags(self) -> None:
    """
    Clears all flags (sets FLAGS register to 0).
    """
    self._FLAGS = 0

  # Flag convenience methods
  def get_zero_flag(self) -> bool:
    """Returns the Zero flag (bit 0)."""
    return self.get_flag(0)

  def set_zero_flag(self, value: bool = True) -> None:
    """Sets or clears the Zero flag (bit 0)."""
    self.set_flag(0, value)

  def get_negative_flag(self) -> bool:
    """Returns the Negative flag (bit 1)."""
    return self.get_flag(1)

  def set_negative_flag(self, value: bool = True) -> None:
    """Sets or clears the Negative flag (bit 1)."""
    self.set_flag(1, value)

  def get_carry_flag(self) -> bool:
    """Returns the Carry flag (bit 2)."""
    return self.get_flag(2)

  def set_carry_flag(self, value: bool = True) -> None:
    """Sets or clears the Carry flag (bit 2)."""
    self.set_flag(2, value)

  def get_overflow_flag(self) -> bool:
    """Returns the Overflow flag (bit 3)."""
    return self.get_flag(3)

  def set_overflow_flag(self, value: bool = True) -> None:
    """Sets or clears the Overflow flag (bit 3)."""
    self.set_flag(3, value)

  def update_flags(self, result: int, operand1: int = None, operand2: int = None, operation: str = None) -> None:
    """
    Updates flags based on operation result.
    
    Args:
        result (int): The result of the operation (32-bit)
        operand1 (int): First operand (for overflow detection)
        operand2 (int): Second operand (for overflow detection)  
        operation (str): Type of operation ('add', 'sub', etc.) for specific flag handling
    """
    # Ensure result is within 32-bit range
    result_32bit = result & 0xFFFFFFFF
    
    # Zero flag: set if result is 0
    self.set_zero_flag(result_32bit == 0)
    
    # Negative flag: set if result is negative (bit 31 set in 32-bit representation)
    self.set_negative_flag((result_32bit & 0x80000000) != 0)
    
    # Carry flag: set if result exceeds 32-bit range
    if operation in ['add', 'addi']:
      self.set_carry_flag(result > 0xFFFFFFFF)
    elif operation in ['sub', 'subi']:
      self.set_carry_flag(result < 0)
    
    # Overflow flag: set if signed arithmetic overflows
    if operand1 is not None and operand2 is not None:
      if operation in ['add', 'addi']:
        # Convert to signed 32-bit for overflow check
        op1_signed = operand1 if operand1 < 0x80000000 else operand1 - 0x100000000
        op2_signed = operand2 if operand2 < 0x80000000 else operand2 - 0x100000000
        result_signed = result_32bit if result_32bit < 0x80000000 else result_32bit - 0x100000000
        
        # Overflow occurs when both operands have same sign but result has different sign
        overflow = ((op1_signed >= 0 and op2_signed >= 0 and result_signed < 0) or 
                   (op1_signed < 0 and op2_signed < 0 and result_signed >= 0))
        self.set_overflow_flag(overflow)
      elif operation in ['sub', 'subi']:
        # Similar logic for subtraction
        op1_signed = operand1 if operand1 < 0x80000000 else operand1 - 0x100000000
        op2_signed = operand2 if operand2 < 0x80000000 else operand2 - 0x100000000
        result_signed = result_32bit if result_32bit < 0x80000000 else result_32bit - 0x100000000
        
        # Overflow in subtraction: different signs in operands, result has wrong sign
        overflow = ((op1_signed >= 0 and op2_signed < 0 and result_signed < 0) or 
                   (op1_signed < 0 and op2_signed >= 0 and result_signed >= 0))
        self.set_overflow_flag(overflow)

  # def read_PC(self) -> bitarray:
  #   """Reads the value of the Program Counter (PC) register."""
  #   return self._PC
  
  # def write_PC(self, value: int) -> None:
  #   """
  #   Writes a value to the Program Counter (PC) register.

  #   Args:
  #       value (int): The value to write to the PC (must be a 64-bit unsigned integer).
        
  #   Raises:
  #       ValueError: If the value is not a 64-bit unsigned integer.
  #   """
  #   if not (0 <= value < 2**self.PC_REG_SIZE):
  #     raise ValueError("Value must be a 64-bit unsigned integer.")
    
  #   self._PC = bitarray(f'{value:0{self.PC_REG_SIZE}b}')

  # def read_FLAGS(self) -> bitarray:
  #   """
  #   Reads the value of the Flags register.
    
  #   Returns:
  #       bitarray: The value of the Flags register as a bitarray.
  #   """
  #   return self._FLAGS
  
  # def write_FLAGS(self, value: int) -> None:
  #   """
  #   Writes a value to the Flags register.

  #   Args:
  #       value (int): The value to write to the Flags register (must be an 8-bit unsigned integer).
        
  #   Raises:
  #       ValueError: If the value is not an 8-bit unsigned integer.
  #   """
  #   if not (0 <= value < 2**self.FLAGS_REG_SIZE):
  #     raise ValueError("Value must be an 8-bit unsigned integer.")
    
  #   self._FLAGS = bitarray(f'{value:0{self.FLAGS_REG_SIZE}b}')

  # def read_vault(self, key_name: str) -> bitarray:
  #   """
  #   Reads the value of a specified vault key.

  #   Args:
  #       key_name (str): The name of the vault key to read (e.g., 'KEY0', 'KEY1', ..., 'KEY3').  
  #   Returns:
  #       bitarray: The value of the specified vault key as a bitarray.
  #   Raises:
  #       ValueError: If the vault key name is invalid.
  #   """
  #   if key_name not in self._VAULT:
  #     raise ValueError(f"Invalid vault key name: {key_name}")
    
  #   return self._VAULT[key_name]
    
  # def write_vault(self, key_name: str, value: int) -> None:
  #   """
  #   Writes a value to a specified vault key.

  #   Args:
  #       key_name (str): The name of the vault key to write to (e.g., 'KEY0', 'KEY1', ..., 'KEY3').
  #       value (int): The value to write to the vault key (must be a 64-bit unsigned integer).
        
  #   Raises:
  #       ValueError: If the vault key name is invalid.
  #   """
  #   if key_name not in self._VAULT:
  #     raise ValueError(f"Invalid vault key name: {key_name}")
    
  #   if not (0 <= value < 2**self.SECURE_VAULT_REG_SIZE):
  #     raise ValueError("Value must be a 64-bit unsigned integer.")
    
  #   self._VAULT[key_name] = bitarray(f'{value:0{self.SECURE_VAULT_REG_SIZE}b}')

  # def read_init(self, init_name: str) -> bitarray:
  #   """
  #   Reads the value of a specified init value.

  #   Args:
  #       init_name (str): The name of the init value to read (e.g., 'A', 'B', 'C', 'D').  
  #   Returns:
  #       bitarray: The value of the specified init value as a bitarray.
  #   Raises:
  #       ValueError: If the init value name is invalid.
  #   """
  #   if init_name not in self._INIT:
  #     raise ValueError(f"Invalid init value name: {init_name}")
    
  #   return self._INIT[init_name]
  
  # def write_init(self, init_name: str, value: int) -> None:
  #   """
  #   Writes a value to a specified init value.

  #   Args:
  #       init_name (str): The name of the init value to write to (e.g., 'A', 'B', 'C', 'D').
  #       value (int): The value to write to the init value (must be a 64-bit unsigned integer).
        
  #   Raises:
  #       ValueError: If the init value name is invalid.
  #   """
  #   if init_name not in self._INIT:
  #     raise ValueError(f"Invalid init value name: {init_name}")
    
  #   if not (0 <= value < 2**self.INIT_REG_SIZE):
  #     raise ValueError("Value must be a 64-bit unsigned integer.")
    
  #   self._INIT[init_name] = bitarray(f'{value:0{self.INIT_REG_SIZE}b}')  

  # def read_hash_state(self, hs_name: str) -> bitarray:
  #   """
  #   Reads the value of a specified hash state register.

  #   Args:
  #       hs_name (str): The name of the hash state register to read (e.g., 'HS_A', 'HS_B', 'HS_C', 'HS_D').  
  #   Returns:
  #       bitarray: The value of the specified hash state register as a bitarray.
  #   Raises:
  #       ValueError: If the hash state register name is invalid.
  #   """
  #   if hs_name not in self._HASH_STATE:
  #     raise ValueError(f"Invalid hash state register name: {hs_name}")
    
  #   return self._HASH_STATE[hs_name]
  
  # def write_hash_state(self, hs_name: str, value: int) -> None:
  #   """
  #   Writes a value to a specified hash state register.

  #   Args:
  #       hs_name (str): The name of the hash state register to write to (e.g., 'HS_A', 'HS_B', 'HS_C', 'HS_D').
  #       value (int): The value to write to the hash state register (must be a 64-bit unsigned integer).
        
  #   Raises:
  #       ValueError: If the hash state register name is invalid.
  #   """
  #   if hs_name not in self._HASH_STATE:
  #     raise ValueError(f"Invalid hash state register name: {hs_name}")
    
  #   if not (0 <= value < 2**self.HASH_REG_SIZE):
  #     raise ValueError("Value must be a 64-bit unsigned integer.")
    
  #   self._HASH_STATE[hs_name] = bitarray(f'{value:0{self.HASH_REG_SIZE}b}')