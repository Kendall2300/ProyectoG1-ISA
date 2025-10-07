class Memory:
  def __init__(self, size: int = 1024):
    """
    Initialize memory with given size and endianness.
    
    Args:
        size (int): Size of the memory in bytes. Default is 1 KB.
    """
    self.size = size
    self.mem = [0] * size

  def _check_range(self, addr: int) -> None:
    """
    Check if the memory access is within the valid range.
    
    Args:
        addr (int): Address to check.
    """
    if not 0 <= addr < self.size:
      raise IndexError(f"Memory access out of range.")
    
  def load_word(self, addr: int) -> int:
    """
    Read a word from memory.

    Args:
        addr (int): Address to read from.

    Returns:
        int: The word read from memory.
    """
    self._check_range(addr)
    return self.mem[addr]

  def store_bytes(self, addr: int, value: int) -> None:
    """
    Write a byte to memory.

    Args:
        addr (int): Address where to write.
        value (int): Value to write.
    """
    self._check_range(addr)
    self.mem[addr] = value