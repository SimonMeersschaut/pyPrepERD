import tkinter as tk
from tkinter import ttk
import glob


def load_projects() -> list:
    folders = [folder.split('\\')[-1] for folder in glob.glob("W:\\transfer_ERD\\*")]
    return sorted(folders)


class ProjectBrowser:
    def __init__(self, on_update:callable):
        """
        projects: dict of { project_name: [file1, file2, ...] }
        """
        self.on_update = on_update
        # load projects
        self.projects = load_projects()
        # print(len(self.projects))
        self.selected_project = tk.StringVar()
        self.selected_file = tk.StringVar()

    def render_frame(self, parent_frame):
        # Main container frame
        container = ttk.Frame(parent_frame, padding="10", style="DarkFrame.TFrame")
        container.pack(fill=tk.X, pady=5)

        # Project dropdown
        ttk.Label(container, text="Select Project:", style="TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        project_dropdown = ttk.Combobox(
            container,
            textvariable=self.selected_project,
            values=self.projects,
            state="readonly"
        )
        # Disable scrolling, as it crashed the application
        # Windows & OSX
        project_dropdown.unbind_class("TCombobox", "<MouseWheel>")

        # Linux and other *nix systems:
        project_dropdown.unbind_class("TCombobox", "<ButtonPress-4>")
        project_dropdown.unbind_class("TCombobox", "<ButtonPress-5>")

        project_dropdown.grid(row=0, column=1, sticky=tk.W, padx=(0, 10))
        project_dropdown.bind("<<ComboboxSelected>>", self._on_project_selected)

        # File dropdown
        ttk.Label(container, text="Select File:", style="TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.file_dropdown = ttk.Combobox(
            container,
            textvariable=self.selected_file,
            values=[],
            state="readonly"
        )
        self.file_dropdown.bind("<<ComboboxSelected>>", self._on_file_selected)
        self.file_dropdown.grid(row=0, column=3, sticky=tk.W)

    def _on_project_selected(self, event=None):
        """Update files dropdown when a project is selected."""
        project = self.selected_project.get()

        # Get all .flt files in the chosen folder
        files = glob.glob(f"W:\\transfer_ERD\\{project}\\*.flt")

        # Extract just the filenames (no path)
        file_names = [f.split("\\")[-1] for f in files]

        # remove _parking files
        file_names = [file for file in file_names if not file.endswith("_parking.flt")]

        # Update the second dropdown
        self.file_dropdown["values"] = file_names

        if file_names:
            # Select the first one by default
            self.selected_file.set(file_names[0])
            # Trigger update callback with full path
            self.on_update(files[0])
        else:
            self.selected_file.set("")


    def _on_file_selected(self, event=None):
        """Trigger update when a file is selected."""
        project = self.selected_project.get()
        file_name = self.selected_file.get()
        if project and file_name:
            full_path = f"W:\\transfer_ERD\\{project}\\{file_name}"
            self.on_update(full_path)
