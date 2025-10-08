from bitarray import bitarray


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
    # self._FLAGS = bitarray('0' * self.FLAGS_REG_SIZE)                                                      # Flags register

    # Secure Vault registers
    # self._VAULT = {f'KEY{i}': bitarray('0' * self.SECURE_VAULT_REG_SIZE) for i in range(self.VAULT_NUM_KEYS)}   # Vault register
    # self._INIT = {f'{value}': bitarray('0' * self.INIT_REG_SIZE) for value in self.HASH_VALUES}                 # Hash init values registers

    # # Internal Hash State registers
    # self._HASH_STATE = {f'HS_{value}': bitarray('0' * self.HASH_REG_SIZE) for value in self.HASH_VALUES}        # Hash state registers

  def read(self, reg_name: str) -> bitarray:                                                 
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