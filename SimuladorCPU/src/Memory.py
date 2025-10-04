from typing import Literal


Endian = Literal['little', 'big']

class Memory:
  def __init__(self, size: int = 1024 * 1024, endian: Endian = 'little', require_alignment: bool = False):
    """
    Initialize memory with given size and endianness.
    
    Args:
        size (int): Size of the memory in bytes. Default is 1 MiB.
        endian (str): Endianness of the memory ('little' or 'big'). Default is 'little'.
        require_alignment (bool): If True, enforce alignment for multi-byte accesses. Default is False.
    """
    self._memory = bytearray(size)
    self._size = size
    self._endian = endian
    self._require_alignment = require_alignment

  def _check_range(self, addr: int, nbytes: int) -> None:
    """
    Check if the memory access is within the valid range.
    
    Args:
        addr (int): Starting address of the access.
        nbytes (int): Number of bytes to access.
    """
    if addr < 0 or addr + nbytes > self._size:
      raise IndexError(f"Memory access out of range: 0x{addr:X}...0x{addr + nbytes-1:X} (size={self._size})")
    
  def _check_alignment(self, addr: int, nbytes: int) -> None:
    """
    Check if the memory access is aligned if alignment is required.
    
    Args:
        addr (int): Starting address of the access.
        nbytes (int): Number of bytes to access.
    """
    if self._require_alignment and (addr % nbytes) != 0:
      raise ValueError(f"Unaligned access: address=0x{addr:X}, width={nbytes}")
    
  def read_bytes(self, addr: int, nbytes: int) -> bytes:
    """
    Read bytes from memory.
    
    Args:
        addr (int): Starting address to read from.
        nbytes (int): Number of bytes to read.  
    
    Returns:
        bytes: The bytes read from memory.
    """
    self._check_range(addr, nbytes)
    self._check_alignment(addr, nbytes)
    return bytes(self._memory[addr:addr + nbytes])
  
  def write_bytes(self, addr: int, data: bytes) -> None:
    """
    Write bytes to memory.

    Args:
        addr (int): Starting address to write to.
        data (bytes): Data to write.
    """
    nbytes = len(data)
    self._check_range(addr, nbytes)
    self._check_alignment(addr, nbytes)
    self._memory[addr:addr + nbytes] = data