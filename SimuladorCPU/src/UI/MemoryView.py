import tkinter as tk
from tkinter import ttk


# Constants
ROW_SIZE = 16                         # 16 bytes per row
WORD_SIZE = 4                         # 4 bytes per word
COL_PER_ROW = ROW_SIZE // WORD_SIZE   # 4 words per row

class MemoryView(ttk.Frame):
  def __init__(self, parent: ttk.Frame, main_app: tk.Tk):
    super().__init__(parent)
    self.main_app = main_app
    self._create_widgets()
  
  def _create_widgets(self) -> None:
    """
    Creates the main widgets for the memory view.
    """
    # Treeview style
    style = ttk.Style()
    style.configure("Treeview", rowheight=35)

    # Treeview columns
    cols = ["Address"] + [f"Addr+{i}" for i in range(4)]

    # Treeview
    self.treeView = ttk.Treeview(self, columns=cols, show="headings", height=20)
    
    # Column headings and config
    self.treeView.heading("Address", text="Base Address")
    self.treeView.column("Address", width=100, anchor=tk.CENTER)
    for i in range(4):
      self.treeView.heading(f"Addr+{i}", text=f"[+{i}]")
      self.treeView.column(f"Addr+{i}", width=80, anchor=tk.CENTER)

    # Scrollbar
    scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeView.yview)
    scrollbar.pack(side="right", fill="y")
    self.treeView.configure(yscrollcommand=scrollbar.set)

    # Insert initial data
    self._load_memory_data()

    self.treeView.pack(fill="both", expand=True)

  def _load_memory_data(self) -> None:
    """
    Loads memory data into the treeview.
    """
    mem = self.main_app.pipeline.memory.mem
    size = len(mem)
    # Show memory in groups of 4 words (addresses)
    for base in range(0, min(size, 256), 4):  # Show first 256 addresses, 4 per row
      address = f"0x{base:08X}"
      words = []
      for col in range(4):
        a = base + col
        if a < size:
          # Each memory location contains a single integer value
          word = mem[a]
          words.append(f"{word:08X}")
        else:
          words.append("00000000")
      self.treeView.insert("", "end", values=[address] + words)

  def refresh(self) -> None:
    """
    Refreshes the memory values displayed in the UI.
    """
    # Clear existing data
    for item in self.treeView.get_children():
      self.treeView.delete(item)
    
    # Reload memory data
    self._load_memory_data()