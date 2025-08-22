import tkinter as tk
from tkinter import ttk, filedialog
import os

last_visited = None

class ProjectBrowser:
    def __init__(self, on_update: callable):
        """
        on_update: callback that receives the full path to a selected .flt file.
        This version uses a single 'Open folder' button instead of dropdowns.
        """
        self.on_update = on_update
        self.selected_folder = tk.StringVar(value="") # TODO set initial value

    # def render_frame(self, parent_frame):
    #     # Main container frame
    #     container = ttk.Frame(parent_frame, padding="10", style="DarkFrame.TFrame")
    #     container.pack(fill=tk.X, pady=5)

    #     # Open folder button
    #     open_btn = ttk.Button(container, text="Open folder", command=self._choose_folder)
    #     open_btn.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

    #     # Read-only label to show chosen folder
    #     ttk.Label(container, textvariable=self.selected_folder, style="TLabel") \
    #         .grid(row=0, column=1, sticky=tk.W)

    #     # Make grid tidy
    #     container.columnconfigure(1, weight=1)

    def _choose_folder(self):
        global last_visited
        # Start in the old root if it exists; otherwise default
        initial_dir = last_visited+"/.." if last_visited else r"transfer_ERD" # TODO: deze komt niet overeen met de initial value die echt geopened wordt # TODO: via file_handler
        folder = filedialog.askdirectory(initialdir=initial_dir, title="Select project folder")
        if not folder:
            return  # user cancelled
        last_visited = folder
        # Normalize path for Windows
        folder = os.path.normpath(folder)
        self.selected_folder.set(folder)

        self.on_update(folder)