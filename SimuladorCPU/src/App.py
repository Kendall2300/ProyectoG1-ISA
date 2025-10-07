import tkinter as tk
from tkinter import ttk
from UI.RegisterView import RegisterView
from UI.MemoryView import MemoryView
from UI.TextEditor import TextEditor
from Pipeline import Pipeline
from Instruction import parse_instructions


class App(tk.Tk):
  def __init__(self):
    super().__init__()

    # Pipeline
    self.pipeline = Pipeline()

    # Main window settings
    self.title("Simulador de CPU")
    self.minsize(1000, 600)
    self._create_widgets()

    # Update Widgets on cycle
    self.pipeline.on_cycle = lambda pipeline: self.register_view.refresh()

  def _create_widgets(self) -> None:
    """
    Creates the main application widgets.
    """
    # Register View (Left side)
    self.register_view = RegisterView(self, self)
    self.register_view.pack(side="left", fill="y")

    # Notebook (Center and Right side)
    notebook = ttk.Notebook(self)
    notebook.pack(side="right", fill="both", expand=True)

    # Text Editor Tab
    textEditorTab = ttk.Frame(notebook)
    notebook.add(textEditorTab, text="Text Editor")

    self.textEditor = TextEditor(textEditorTab, self._on_run_button_click)
    self.textEditor.pack(fill="both", expand=True)

    # Memory View Tab
    memoryTab = ttk.Frame(notebook)
    notebook.add(memoryTab, text="Memory View")

    memoryView = MemoryView(memoryTab, self)
    memoryView.pack(fill="both", expand=True)

  def run(self) -> None:
    """ 
    Starts the main application loop.
    """
    self.mainloop()

  def _on_run_button_click(self) -> None:
    """
    Handles the Run button click event.
    """
    # Get code from text editor
    code = (self.textEditor.get_code()).splitlines()

    # Instructions
    self.pipeline.instructions = parse_instructions(code)
    self.pipeline.labels = self.pipeline.map_labels(code)
    self.pipeline.PC = 0

    # Run pipeline
    self._step_loop()

  def _step_loop(self) -> None:
    """
    Steps through the pipeline until all instructions are processed.
    """
    stages_empty = (
      self.pipeline.IF_ID["instr"] is None and
      self.pipeline.ID_EX["instr"] is None and
      self.pipeline.EX_MEM["instr"] is None and
      self.pipeline.MEM_WB["instr"] is None
    )

    if self.pipeline.PC >= len(self.pipeline.instructions) and stages_empty:
      self.register_view.refresh()
      return
    
    self.pipeline.step()
    self.after(50, self._step_loop)