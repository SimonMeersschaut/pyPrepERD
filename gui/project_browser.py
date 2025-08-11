import tkinter as tk
from tkinter import ttk
import glob


def load_projects() -> list:
    folders = [folder.split('\\')[-1] for folder in glob.glob("W:\\transfer_ERD\\*")]
    return sorted(folders)


class ProjectBrowser:
    def __init__(self):
        """
        projects: dict of { project_name: [file1, file2, ...] }
        """
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
        self.file_dropdown.grid(row=0, column=3, sticky=tk.W)

    def _on_project_selected(self, event=None):
        """Update files dropdown when a project is selected."""
        project = self.selected_project.get()
        # print(f"Selected {project}")
        # files = self.projects.get(project, [])
        # self.file_dropdown["values"] = files
        # if files:
        #     self.selected_file.set(files[0])
        # else:
        #     self.selected_file.set("")