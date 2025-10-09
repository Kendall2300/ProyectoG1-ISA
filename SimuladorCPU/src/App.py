import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from UI.RegisterView import RegisterView
from UI.MemoryView import MemoryView
from UI.TextEditor import TextEditor
from UI.Console import Console
from CPU.Pipeline import Pipeline
from Instruction import parse_instructions
from assembler import assemble
import os


class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.output_directory = "SimuladorCPU/out"

    # Initialize pipeline 
    self.pipeline = Pipeline()

    # Main window settings
    self.title("Simulador de CPU")
    self.minsize(1000, 600)
    self._create_widgets()

  def _create_widgets(self) -> None:
    """
    Creates the main application widgets.
    """
    # Main container
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

    self.textEditor = TextEditor(
      textEditorTab, 
      on_run_callback=self._on_run_button_click, 
      on_compile_callback=self._on_compile_button_click,
      on_load_callback=self._on_load_button_click
    )
    self.textEditor.pack(fill="both", expand=True)

    # Memory View Tab
    memoryTab = ttk.Frame(notebook)
    notebook.add(memoryTab, text="Memory View")

    self.memory_view = MemoryView(memoryTab, self)
    self.memory_view.pack(fill="both", expand=True)

    # Console (Bottom section - spans the entire width)
    self.console = Console(main_container)
    self.console.pack(side="bottom", fill="x", pady=(5, 0))
    
    # Set console for pipeline logging
    self.pipeline.console = self.console
    
    # Set up pipeline callback for UI updates 
    self.pipeline.on_cycle = lambda pipeline: self._update_views()

  def run(self) -> None:
    """ 
    Starts the main application loop.
    """
    self.mainloop()

  def _update_views(self) -> None:
    """
    Updates all views in the UI.
    """
    self.register_view.refresh()
    self.memory_view.refresh()

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
  
  def _on_compile_button_click(self):
    # Create ASM file
    code = self.textEditor.get_code()
    asmFilepath = self._create_asm_file(code)

    # Assemble code
    outputFilePath = os.path.join(self.output_directory, "program.bin")
    assemble(asmFilepath, outputFilePath)

  def _create_asm_file(self, code: str, filename: str = "program.asm") -> str:
    """
    Creates an ASM file with the given code.

    Args:
        code (str): The assembly code to write to the file.
        filename (str): The name of the ASM file. Defaults to "program.asm".
        directory (str): The directory where the ASM file will be saved. Defaults to "out".

    Returns:
        str: The path to the created ASM file.
    """
    try:
      # Create directory
      os.makedirs(self.output_directory, exist_ok=True)
      filepath = os.path.join(self.output_directory, filename)

      # Create ASM file
      with open(filepath, "w", encoding="utf-8") as file:
        file.write(code)
      return filepath
    
    except Exception as e:
      self.console.log(f"Error saving file: {e}")

  def _on_load_button_click(self):
    """
    Handles the Load button click event.
    Opens a file dialog to select an ASM file and loads its content into the text editor.
    """
    # Open file explorer dialog
    filepath = filedialog.askopenfilename(
      filetypes=[("Archivos ASM", "*.asm")],
      title="Seleccionar archivo ASM"
    )

    # Load file content into text editor
    if filepath:
      try:
        with open(filepath, "r", encoding="utf-8") as file:
          content = file.read()

          # Clear Text Editor
          self.textEditor.text.delete("1.0", tk.END)

          # Insert text
          self.textEditor.text.insert(tk.END, content)
          self.textEditor.update_linenumbers()
      except Exception as e:
        self.console.log(f"Error reading file: {e}")