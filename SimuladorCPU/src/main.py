from RegisterFile import RegisterFile
from Memory import Memory
from App import App

if __name__ == "__main__":
  register_file = RegisterFile()
  memory = Memory()

  print("Memory: ")
  print(memory.read_bytes(0, 4))

  memory.write_bytes(0, b'\x01\x02\x03\x04')
  print(memory.read_bytes(0, 4))

  # register_file.write_register('R1', 42)
  # register_file.write_PC(100)

  # register_file.write_vault('KEY0', 123456789)

  # register_file.write_init('A', 987654321)

  # register_file.write_hash_state('HS_A', 555555555)

  # app = App(register_file)
  # app.run()
