from bitarray import bitarray

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
# --- Hash Function ---
HASH_VALUES = ['A', 'B', 'C', 'D']    # Initial hash values for the hash function
HASH_REG_SIZE = 64                    # Size of hash function registers in bits

class CPURegisters:
  def __init__(self):
    # General purpose registers R0-R31
    self._registers = {f'R{i}': bitarray('0' * GPR_REG_SIZE) for i in range(GPR_NUM_REGS)}

    # Special registers
    self._PC = bitarray('0' * 64)      # Program Counter
    self._FLAGS = bitarray('0' * 8)    # Flags register

    # Secure Vault registers
    self._VAULT = {f'KEY{i}': bitarray('0' * SECURE_VAULT_REG_SIZE) for i in range(VAULT_NUM_KEYS)}   # Vault register
    self._INIT = {f'{value}': bitarray('0' * SECURE_VAULT_REG_SIZE) for value in HASH_VALUES}         # Init values of the hash function

    # Internal Hash State registers
    self._HS_A = bitarray('0' * HASH_REG_SIZE)
    self._HS_B = bitarray('0' * HASH_REG_SIZE)
    self._HS_C = bitarray('0' * HASH_REG_SIZE)
    self._HS_D = bitarray('0' * HASH_REG_SIZE)

  def read_register(self, reg_name: str) -> bitarray: # Only read GPR registers
    """
    Reads the value of a specified GPR register.

    Args:
        reg_name (str): The name of the register to read (e.g., 'R0', 'R1', ..., 'R31').

    Returns:
        bitarray: The value of the specified register as a bitarray.

    Raises:
        ValueError: If the register name is invalid.
    """
    if reg_name not in self._registers:
      raise ValueError(f"Invalid register name: {reg_name}")
    
    return self._registers[reg_name]
  
  def write_register(self, reg_name: str, value: int) -> None: # Only write GPR registers
    """
    Writes a value to a specified GPR register.

    Args:
        reg_name (str): The name of the register to write to (e.g., 'R0', 'R1', ..., 'R31').
        value (int): The value to write to the register (must be a 64-bit unsigned integer).
        
    Raises:
        ValueError: If the register name is invalid or if trying to write to R0.
    """
    if reg_name not in self._registers:
      raise ValueError(f"Invalid register name: {reg_name}")
    
    if reg_name == 'R0':
      raise ValueError("Register R0 is read-only and always contains 0.")
    
    if not (0 <= value < 2**GPR_REG_SIZE):
      raise ValueError("Value must be a 64-bit unsigned integer.")
    
    self._registers[reg_name] = bitarray(f'{value:0{GPR_REG_SIZE}b}')
    
  def read_PC(self) -> bitarray:
    """Reads the value of the Program Counter (PC) register."""
    return self._PC
  
  def write_PC(self, value: int) -> None:
    """
    Writes a value to the Program Counter (PC) register.

    Args:
        value (int): The value to write to the PC (must be a 64-bit unsigned integer).
        
    Raises:
        ValueError: If the value is not a 64-bit unsigned integer.
    """
    if not (0 <= value < 2**PC_REG_SIZE):
      raise ValueError("Value must be a 64-bit unsigned integer.")
    
    self._PC = bitarray(f'{value:0{PC_REG_SIZE}b}')