from CPURegisters import CPURegisters
from App import App

if __name__ == "__main__":
  cpu = CPURegisters()
  cpu.write_register('R1', 42)
  cpu.write_PC(100)
  # print(f"PC: {cpu.read_PC()}")
  cpu.write_vault('KEY0', 123456789)
  # print(f"Vault KEY0: {cpu.read_vault('KEY0')}")
  cpu.write_init('A', 987654321)
  # print(f"Init A: {cpu.read_init('A')}")
  cpu.write_hash_state('HS_A', 555555555)
  # print(f"Hash State HS_A: {cpu.read_hash_state('HS_A')}")

  app = App(cpu)
  app.run()
