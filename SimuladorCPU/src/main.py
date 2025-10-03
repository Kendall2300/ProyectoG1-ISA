from CPURegisters import CPURegisters


if __name__ == "__main__":
  cpu = CPURegisters()
  cpu.write_PC(100)
  print(f"PC: {cpu.read_PC()}")
