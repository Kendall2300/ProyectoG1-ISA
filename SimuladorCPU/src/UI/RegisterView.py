import tkinter as tk
from tkinter import ttk


class RegisterView(ttk.Frame):
  def __init__(self, parent: ttk.Frame, main_app: tk.Tk):
    super().__init__(parent, borderwidth=2, relief="groove")
    self.main_app = main_app
    self.value_labels = {}
    self._create_widgets()

  def _create_widgets(self) -> None:
    """
    Creates the main widgets for the register view.
    """
    # Vertical box
    self.vbox = ttk.Frame(self, borderwidth=2, relief="groove")
    self.vbox.pack(side="left", fill="y")

    # Scrollable frame
    self._create_scrollable_frame(self.vbox)

    # Render registers
    registers = self.main_app.pipeline.registers

    # GPR Registers
    for i in range(len(registers.regs)):
        value = registers.read(f'R{i}')
        self._create_register_box(self.inner_frame, f"R{i}", value)

    # Special Registers - FLAGS
    self._create_separator(self.inner_frame, "FLAGS REGISTER")
    flags_value = registers.read_flags()
    self._create_register_box(self.inner_frame, "FLAGS", flags_value)
    
    # Individual flags
    self._create_flag_box(self.inner_frame, "Z (Zero)", 0)
    self._create_flag_box(self.inner_frame, "N (Negative)", 1)
    self._create_flag_box(self.inner_frame, "C (Carry)", 2)
    self._create_flag_box(self.inner_frame, "V (Overflow)", 3)

    # Secure Vault Registers (accessed from Pipeline for security)
    pipeline = self.main_app.pipeline
    self._create_separator(self.inner_frame, "SECURE VAULT")
    for i in range(pipeline.VAULT_NUM_KEYS):
        value = pipeline.read_vault(f'KEY{i}')
        self._create_vault_register_box(self.inner_frame, f"KEY{i}", value)

    # Hash Init Values
    self._create_separator(self.inner_frame, "HASH INIT VALUES") 
    for reg in pipeline.HASH_VALUES:
        value = pipeline.read_init(f'{reg}')
        self._create_vault_register_box(self.inner_frame, f"INIT_{reg}", value)

    # Hash State Registers
    self._create_separator(self.inner_frame, "HASH STATE")
    for reg in pipeline.HASH_VALUES:
        value = pipeline.read_hash_state(f'HS_{reg}')
        self._create_vault_register_box(self.inner_frame, f"HS_{reg}", value)

  def _create_register_box(self, parent: ttk.Frame, label_text: str, value: int) -> None:
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
    value_hex = hex(value)[2:]
    reg_value = ttk.Label(hbox, text=f"{value_hex}", width=15, anchor="w")
    reg_value.pack(side="left", padx=(5, 0))

    self.value_labels[label_text] = reg_value

  def _create_separator(self, parent: ttk.Frame, label_text: str) -> None:
    """
    Creates a separator with label for grouping registers.
    
    Args:
        parent (ttk.Frame): The parent frame where the separator will be placed.
        label_text (str): The text for the separator label.
    """
    # Separator frame
    sep_frame = ttk.Frame(parent, padding=(5, 10, 5, 5))
    sep_frame.pack(fill="x", pady=(10, 5))
    
    # Label
    sep_label = ttk.Label(sep_frame, text=label_text, font=('TkDefaultFont', 9, 'bold'))
    sep_label.pack()
    
    # Horizontal line
    sep_line = ttk.Separator(sep_frame, orient="horizontal")
    sep_line.pack(fill="x", pady=(5, 0))

  def _create_flag_box(self, parent: ttk.Frame, label_text: str, flag_bit: int) -> None:
    """
    Creates a box for a single flag with its label and value.

    Args:
        parent (ttk.Frame): The parent frame where the flag box will be placed.
        label_text (str): The label text for the flag (e.g., 'Z (Zero)', 'N (Negative)', etc.).
        flag_bit (int): The bit position of the flag (0-7).
    """
    # Horizontal box
    hbox = ttk.Frame(parent, borderwidth=1, relief="solid", padding=(10, 3, 10, 3))
    hbox.pack(pady=2, fill="x", padx=5)

    # Flag label
    flag_label = ttk.Label(hbox, text=label_text, width=12, anchor="w", font=('TkDefaultFont', 8))
    flag_label.pack(side="left", padx=(0, 10))

    # Vertical separator
    sep = ttk.Separator(hbox, orient="vertical")
    sep.pack(side="left", fill="y", padx=5)

    # Flag value
    registers = self.main_app.pipeline.registers
    flag_value = "1" if registers.get_flag(flag_bit) else "0"
    flag_value_label = ttk.Label(hbox, text=flag_value, width=3, anchor="center", 
                                font=('TkDefaultFont', 8, 'bold'),
                                foreground="red" if flag_value == "1" else "gray")
    flag_value_label.pack(side="left", padx=(5, 0))

    self.value_labels[f"FLAG_{flag_bit}"] = flag_value_label

  def _create_vault_register_box(self, parent: ttk.Frame, label_text: str, value: int) -> None:
    """
    Creates a box for a vault register (64-bit) with its label and value.

    Args:
        parent (ttk.Frame): The parent frame where the register box will be placed.
        label_text (str): The label text for the register (e.g., 'KEY0', 'INIT_A', 'HS_A', etc.).
        value (int): The value of the register as an integer.
    """
    # Horizontal box
    hbox = ttk.Frame(parent, borderwidth=1, relief="solid", padding=(10, 4, 10, 4))
    hbox.pack(pady=3, fill="x", padx=5)

    # Register label
    reg_label = ttk.Label(hbox, text=label_text, width=10, anchor="w", font=('TkDefaultFont', 9))
    reg_label.pack(side="left", padx=(0, 10))

    # Vertical separator
    sep = ttk.Separator(hbox, orient="vertical")
    sep.pack(side="left", fill="y", padx=5)

    # Register value (64-bit hex)
    value_hex = f"0x{value:016X}"
    reg_value = ttk.Label(hbox, text=value_hex, width=18, anchor="w", 
                         font=('Courier', 8), foreground="blue")
    reg_value.pack(side="left", padx=(5, 0))

    self.value_labels[label_text] = reg_value

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

  def refresh(self) -> None:
    """
    Refreshes the register values displayed in the UI.
    """
    registers = self.main_app.pipeline.registers

    # GPR Registers
    for i in range(len(registers.regs)):
        value = registers.read(f'R{i}')
        label = self.value_labels.get(f'R{i}')
        if label:
            value_hex = hex(value)[2:]
            label.config(text=f"{value_hex}")

    # FLAGS Register
    flags_value = registers.read_flags()
    flags_label = self.value_labels.get("FLAGS")
    if flags_label:
        flags_hex = hex(flags_value)[2:].upper().zfill(2)
        flags_bin = format(flags_value, '08b')
        flags_label.config(text=f"0x{flags_hex} ({flags_bin})")

    # Individual Flags
    for flag_bit in range(4):  # Only show flags 0-3 (Z, N, C, V)
        flag_label = self.value_labels.get(f"FLAG_{flag_bit}")
        if flag_label:
            flag_value = "1" if registers.get_flag(flag_bit) else "0"
            flag_label.config(text=flag_value,
                            foreground="red" if flag_value == "1" else "gray")

    # Secure Vault Registers (accessed from Pipeline for security)
    pipeline = self.main_app.pipeline
    for i in range(pipeline.VAULT_NUM_KEYS):
        value = pipeline.read_vault(f'KEY{i}')
        label = self.value_labels.get(f'KEY{i}')
        if label:
            value_hex = f"0x{value:016X}"
            label.config(text=value_hex)

    # Hash Init Values
    for reg in pipeline.HASH_VALUES:
        value = pipeline.read_init(f'{reg}')
        label = self.value_labels.get(f'INIT_{reg}')
        if label:
            value_hex = f"0x{value:016X}"
            label.config(text=value_hex)

    # Hash State Registers
    for reg in pipeline.HASH_VALUES:
        value = pipeline.read_hash_state(f'HS_{reg}')
        label = self.value_labels.get(f'HS_{reg}')
        if label:
            value_hex = f"0x{value:016X}"
            label.config(text=value_hex)