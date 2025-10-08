import tkinter as tk
from tkinter import ttk


class Console(ttk.Frame):
  def __init__(self, parent: ttk.Frame):
    super().__init__(parent, borderwidth=2, relief="groove")
    self._create_widgets()

  def _create_widgets(self):
    self.text_area = tk.Text(self, wrap="word", height=10, bg="black", fg="white")
    self.text_area.pack(expand=True, fill="both")


  def log(self, message: str) -> None:
    self.text_area.insert(tk.END, message + "\n")
    self.text_area.see(tk.END)
