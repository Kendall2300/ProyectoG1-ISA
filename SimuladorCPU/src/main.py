from CPURegisters import CPURegisters


if __name__ == "__main__":
  cpu = CPURegisters()
  print(cpu.read_register('R1'))
  cpu.write_register('R1', 42)
  print(cpu.read_register('R1'))

  try:
    cpu.write_register('R0', 10)
  except ValueError as e:
    print(e)  # Should raise an error since R0 is read-only
