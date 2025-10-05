import tkinter as tk
from tkinter import ttk
from UI.RegisterView import RegisterView
from UI.MemoryView import MemoryView
from CPU import CPU


class App(tk.Tk):
  def __init__(self):
    super().__init__()

    # CPU instance
    self.cpu = CPU()

    # Main window settings
    self.title("Simulador de CPU")
    self.minsize(1000, 600)
    self._create_widgets()

  def _create_widgets(self) -> None:
    """
    Creates the main application widgets.
    """
    # Register View (Left side)
    self.register_view = RegisterView(self, self.cpu.register_file)
    self.register_view.pack(side="left", fill="y")

    # Notebook (Center and Right side)
    notebook = ttk.Notebook(self)
    notebook.pack(side="right", fill="both", expand=True)

    # Text Editor Tab
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text="Text Editor")

    label1 = ttk.Label(tab1, text="Text Editor Placeholder")
    label1.pack(pady=20)

    # Memory View Tab
    memoryTab = ttk.Frame(notebook)
    notebook.add(memoryTab, text="Memory View")

    memoryView = MemoryView(memoryTab, self.cpu.memory)
    memoryView.pack(fill="both", expand=True)

  def run(self) -> None:
    """ 
    Starts the main application loop.
    """
    self.mainloop()