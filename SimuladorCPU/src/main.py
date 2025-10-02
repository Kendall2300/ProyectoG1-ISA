from CPURegisters import CPURegisters


if __name__ == "__main__":
  cpu = CPURegisters()
  print("CPU Registers initialized.")
  print(f"Register R1: {cpu.registers['R1']}")
  print(f"Program Counter (PC): {cpu.PC}")  
  print(f"Flags Register: {cpu.FLAGS}")
  print(f"Vault Key 0: {cpu.VAULT['KEY0']}")
  print(f"Hash Init A: {cpu.INIT['A']}")
  print(f"Hash State A: {cpu.HS_A}")
  print(f"Hash State B: {cpu.HS_B}")
  print(f"Hash State C: {cpu.HS_C}")
  print(f"Hash State D: {cpu.HS_D}")