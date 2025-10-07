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
    cols = ["Address"] + [f"Byte {i}" for i in range(4)]

    # Treeview
    self.treeView = ttk.Treeview(self, columns=cols, show="headings", height=20)
    
    # Column headings and config
    self.treeView.heading("Address", text="Address")
    self.treeView.column("Address", width=90, anchor=tk.CENTER)
    for i in range(4):
      self.treeView.heading(f"Byte {i}", text=f"Word {i} (4 bytes)")
      self.treeView.column(f"Byte {i}", width=60, anchor=tk.CENTER)

    # Scrollbar
    scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.treeView.yview)
    scrollbar.pack(side="right", fill="y")
    self.treeView.configure(yscrollcommand=scrollbar.set)

    # Insert data
    mem = self.main_app.pipeline.memory.mem
    size = len(mem)
    for base in range(0, size, ROW_SIZE):
      address = f"0x{base:08X}"
      words = []
      for col in range(COL_PER_ROW):
        a = base + col * WORD_SIZE
        if a + WORD_SIZE <= size:
          word = int.from_bytes(mem[a:a+WORD_SIZE], "little", signed=False)
          words.append(f"{word:08X}")
        else:
          words.append(" " * 8)
      self.treeView.insert("", "end", values=[address] + words)

    self.treeView.pack(fill="both", expand=True)