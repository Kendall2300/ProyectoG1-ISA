import tkinter as tk
from tkinter import ttk


class TextEditor(ttk.Frame):
  def __init__(
      self, parent: ttk.Frame, 
      on_run_callback: callable, 
      on_compile_callback: callable,
      on_load_callback):
    super().__init__(parent)
    self.on_run_callback = on_run_callback
    self.on_compile_callback = on_compile_callback
    self.on_load_callback = on_load_callback
    self._create_widgets()
    self._bind_events()

  def _create_widgets(self) -> None:
    """
    Creates the main widgets for the text editor.
    """
    # Toolbar
    toolbar = ttk.Frame(self, relief="raised", borderwidth=2)
    toolbar.pack(side="top", fill="x")

    # Load File Button
    load_button = ttk.Button(toolbar, text="Load File", command=self.on_load_callback)
    load_button.pack(side="left", pady=10, padx=10)

    # Run Button (initially disabled)
    self.run_button = ttk.Button(toolbar, text="Run", command=self.on_run_callback, state="disabled")
    self.run_button.pack(side="left", pady=10)

    # Compile Button
    self.compile_button = ttk.Button(toolbar, text="Compile", command=self.on_compile_callback)
    self.compile_button.pack(side="left", pady=10, padx=10)

    # Main Container
    main_container = ttk.Frame(self)
    main_container.pack(fill="both", expand=True)

    # Line Numbers
    self.linenum = tk.Canvas(main_container, width=40, highlightthickness=0)
    self.linenum.pack(side="left", fill="y")

    # Text
    self.text = tk.Text(
      main_container, 
      wrap="none",
      undo=True,
      font=("TkFixedFont", 12)
    )
    self.text.pack(side="right", fill="both", expand=True)

    self.update_linenumbers()

  def _bind_events(self) -> None:
    """
    Binds necessary events to the text widget for updating line numbers.
    """
    self.text.bind("<KeyRelease>", self._on_text_changed)
    self.text.bind("<MouseWheel>", self.update_linenumbers)
    self.text.bind("<Configure>", self.update_linenumbers)
    self.text.config(yscrollcommand=self._on_text_scroll)
    self.linenum.bind("<MouseWheel>", self._on_linenum_scroll)
    
  def _on_text_changed(self, event: tk.Event = None) -> None:
    """
    Handles text changes and disables Run button when code is modified.
    """
    self.update_linenumbers(event)
    # Disable Run button when text is modified (needs recompilation)
    self.disable_run_button()

  def _on_text_scroll(self, *args) -> None:
    """
    Synchronizes the line number canvas with the text widget's vertical scrolling.
    Args:
        *args: Arguments from the text widget's yscrollcommand.
    """
    self.linenum.yview_moveto(args[0])
    self.update_linenumbers()

  def _on_linenum_scroll(self, event: tk.Event) -> None:
    """
    Handles mouse wheel scrolling on the line number canvas.
    
    Args:
        event (tk.Event): The mouse wheel event.
    """
    self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
    self._update_linenumbers()

  def update_linenumbers(self, event: tk.Event = None) -> None:
    """
    Updates the line numbers displayed in the line number canvas.
    Args:
        event (tk.Event, optional): The event that triggered the update. Defaults to None.
    """
    self.linenum.delete("all")

    i = self.text.index("@0,0")

    while True:
      dline = self.text.dlineinfo(i) 
      if dline is None:
        break
      y = dline[1] 

      linenum = str(int(float(i)))                                
      self.linenum.create_text(35, y, anchor="ne", text=linenum)  
      i = self.text.index("%s+1line" % i)    
    
  def get_code(self) -> str:
    """
    Retrieves the current code from the text widget.
    
    Returns:
        str: The code as a string.
    """
    return self.text.get("1.0", "end-1c")
  
  def enable_run_button(self) -> None:
    """
    Enables the Run button.
    """
    self.run_button.config(state="normal")
  
  def disable_run_button(self) -> None:
    """
    Disables the Run button.
    """
    self.run_button.config(state="disabled")