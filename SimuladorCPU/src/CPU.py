from RegisterFile import RegisterFile
from Memory import Memory

class CPU:
  def __init__(self):
    self.register_file = RegisterFile()
    self.memory = Memory(size=64)