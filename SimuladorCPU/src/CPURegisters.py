from bitarray import bitarray

GPR_NUM_REGS = 32                     # Number of general purpose registers
HASH_VALUES = ['A', 'B', 'C', 'D']    # Initial hash values for the hash function
VAULT_NUM_KEYS = 4                    # Number of keys in the vault

class CPURegisters:
  def __init__(self):
    # General purpose registers R0-R31
    self._registers = {f'R{i}': bitarray('0' * 64) for i in range(GPR_NUM_REGS)}

    # Special registers
    self._PC = bitarray('0' * 64)      # Program Counter
    self._FLAGS = bitarray('0' * 8)    # Flags register

    # Secure Vault registers
    self._VAULT = {f'KEY{i}': bitarray('0' * 64) for i in range(VAULT_NUM_KEYS)}   # Vault register
    self._INIT = {f'{value}': bitarray('0' * 64) for value in HASH_VALUES}         # Init values of the hash function

    # Internal Hash State registers
    self._HS_A = bitarray('0' * 64)
    self._HS_B = bitarray('0' * 64)
    self._HS_C = bitarray('0' * 64)
    self._HS_D = bitarray('0' * 64)
