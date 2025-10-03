import tkinter as tk
from tkinter import ttk
import bitarray


class App(tk.Tk):
  def __init__(self, cpu) -> None:
    super().__init__()
    self.cpu = cpu

    self.title("Simulador de CPU")
    self.minsize(1000, 600)
    self._create_widgets()

  def _create_widgets(self) -> None:
    """
    Creates the main application widgets.
    """
    self._create_registers_view()

  def _create_register_box(self, parent: ttk.Frame, label_text: str, value: bitarray) -> None:
    """
    Creates a box for a single register with its label and value.

    Args:
        parent (ttk.Frame): The parent frame where the register box will be placed.
        label_text (str): The label text for the register (e.g., 'R0', 'PC', etc.).
        value (bitarray): The value of the register as a bitarray.
    """
    # Horizontal box
    hbox = ttk.Frame(parent, borderwidth=1, relief="solid", padding=(10, 5, 10, 5))
    hbox.pack(pady=5, fill="x", padx=5)

    # Register label
    reg_label = ttk.Label(hbox, text=label_text, width=8, anchor="w")
    reg_label.pack(side="left", padx=(0, 10))

    # Vertical separator
    sep = ttk.Separator(hbox, orient="vertical")
    sep.pack(side="left", fill="y", padx=5)

    # Register value
    value_hex = hex(int(value.to01(), 2))[2:]
    reg_value = ttk.Label(hbox, text=f"{value_hex}", width=10, anchor="w")
    reg_value.pack(side="left", padx=(5, 0))

  def _create_scrollable_frame(self, parent: ttk.Frame) -> None:
    """
    Creates a scrollable frame within the given parent frame.
    
    Args:
        parent (ttk.Frame): The parent frame where the scrollable frame will be placed.
    """
    # Canvas 
    self.canvas = tk.Canvas(parent)
    self.canvas.pack(side="left", fill="both", expand=True)

    # Vertical Scrollbar
    self.v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.canvas.yview)
    self.v_scrollbar.pack(side="right", fill="y")

    # Configure canvas and scrollbar
    self.canvas.configure(yscrollcommand=self.v_scrollbar.set)
    self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    # Inner frame
    self.inner_frame = ttk.Frame(self.canvas)
    self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"), width=e.width))
    self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

  def _create_registers_view(self):
    # Vertical box
    self.vbox = ttk.Frame(self, borderwidth=2, relief="groove")
    self.vbox.pack(side="left", fill="y")

    # Scrollable frame
    self._create_scrollable_frame(self.vbox)

    # GPR Registers
    for i in range(self.cpu.GPR_NUM_REGS):
        value = self.cpu.read_register(f'R{i}')
        self._create_register_box(self.inner_frame, f"R{i}", value)

    # Special Registers
    self._create_register_box(self.inner_frame, "PC", self.cpu.read_PC())
    self._create_register_box(self.inner_frame, "FLAGS", self.cpu.read_FLAGS())

    # Secure Vault Registers
    for i in range(self.cpu.VAULT_NUM_KEYS):
        value = self.cpu.read_vault(f'KEY{i}')
        self._create_register_box(self.inner_frame, f"KEY{i}", value)
    
    for reg in self.cpu.HASH_VALUES:
        value = self.cpu.read_init(f'{reg}')
        self._create_register_box(self.inner_frame, f"{reg}", value)

    # Hash State Registers
    for reg in self.cpu.HASH_VALUES:
        value = self.cpu.read_hash_state(f'HS_{reg}')
        self._create_register_box(self.inner_frame, f"HS {reg}", value)

  def run(self):
    self.mainloop()