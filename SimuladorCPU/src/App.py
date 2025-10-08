import tkinter as tk
from tkinter import ttk
from UI.RegisterView import RegisterView
from UI.MemoryView import MemoryView
from UI.TextEditor import TextEditor
from UI.Console import Console
from Pipeline import Pipeline
from Instruction import parse_instructions


class App(tk.Tk):
  def __init__(self):
    super().__init__()

    # Initialize pipeline 
    self.pipeline = Pipeline()
    
    # Set up pipeline callback for UI updates
    self.pipeline.on_cycle = lambda pipeline: self.register_view.refresh()

    # Main window settings
    self.title("Simulador de CPU")
    self.minsize(1000, 600)
    self._create_widgets()

    # Set console for pipeline logging
    self.pipeline.set_console(self.console)

  def _create_widgets(self) -> None:
    """
    Creates the main application widgets.
    """
    # Main container that divides the window vertically
    main_container = ttk.Frame(self)
    main_container.pack(fill="both", expand=True)
    
    # Top section (Register View + Notebook)
    top_section = ttk.Frame(main_container)
    top_section.pack(side="top", fill="both", expand=True)
    
    # Register View (Left side of top section)
    self.register_view = RegisterView(top_section, self)
    self.register_view.pack(side="left", fill="y")

    # Notebook (Right side of top section)
    notebook = ttk.Notebook(top_section)
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

    # Console (Bottom section - spans the entire width)
    self.console = Console(main_container)
    self.console.pack(side="bottom", fill="x", pady=(5, 0))

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
      
      # Log execution history to console
      self.console.log("=== EXECUTION HISTORY ===")
      for cycle, cycle_info in enumerate(self.pipeline.execution_history, 1):
        self.console.log(f"Cycle {cycle}:")
        self.console.log(f"  IF: {cycle_info['IF']}")
        self.console.log(f"  ID: {cycle_info['ID']}")
        self.console.log(f"  EX: {cycle_info['EX']}")
        self.console.log(f"  MEM: {cycle_info['MEM']}")
        self.console.log(f"  WB: {cycle_info['WB']}")
        self.console.log("")
      
      self.console.log("=== EXECUTION COMPLETED ===")
      return
    
    self.pipeline.step()
    self.after(50, self._step_loop)