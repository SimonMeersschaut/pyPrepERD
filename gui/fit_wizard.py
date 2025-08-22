import tkinter as tk
from tkinter import filedialog, ttk
import analysis
import os
import glob
from pathlib import Path
from utils import FileHandler
from utils import Log


class FitWizard:
    def __init__(self, master, filehandler: FileHandler):
        self.filehandler = filehandler
        self.master = master
        
        self.selected_project: str = None
        self.fit_btn = None

    def start(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("pyPrepERD - Fit Wizard")
        self.window.geometry("500x400")
        self.window.minsize(500, 400)
        self.window.iconbitmap(self.filehandler.images_path / "icon.ico")

        # Frame for folder selection
        folder_frame = tk.Frame(self.window)
        folder_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(folder_frame, text="Project folder:").grid(row=0, column=0, sticky="w")

        browse_btn = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=5)

        # Treeview for showing folder-element pairs
        self.tree = ttk.Treeview(self.window, columns=("Measurement", "Element"), show="headings", selectmode="browse")
        self.tree.heading("Measurement", text="Measurement")
        self.tree.heading("Element", text="Element")
        self.tree.pack(pady=20, fill="both", expand=True)

        # Fit button
        self.fit_btn = tk.Button(self.window, text="Start Fit", command=self.start_fit)
        self.fit_btn["state"] = "disabled"
        self.fit_btn.pack(pady=5)
        
        self.feedback_label = tk.Label(self.window, text="", fg='#ff0000')
        self.feedback_label.pack()

        self.browse_folder()

    def browse_folder(self):
        folder = filedialog.askdirectory(parent=self.window)

        if not folder:
            # user canceled
            return 

        if not os.path.exists(folder):
            raise FileNotFoundError(f"Project folder `{folder}` not found.")
        
        self.selected_project = folder

        self.tree.delete(*self.tree.get_children())

        # scan folder for subdirectories
        subfolders: list[Path] = [Path(f.path) for f in os.scandir(folder) if f.is_dir() and not "raw" in f.path[0]] # TODO: `in` aanpassen; Path
        
        if len(subfolders) == 0:
            raise ValueError("The selected folder did not contain any subfolders. Be sure to select a project folder.")
        
        for subfolder in subfolders:
            # search polygon cut
            if not os.path.exists(subfolder / "Cut-files"): # TODO: paths
                Log.warn("Invalid folder warning", str(subfolder) + " did not contain a `Cut-files` folder.")
                continue
            
            cut_files = [Path(file) for file in glob.glob(str(subfolder / "Cut-files" / "*.*")) if not ".json" in file] # TODO: paths
            if len(cut_files) == 0:
                Log.warn("Invalid folder warning", f"No cut files found in `{subfolder}/Cut-files/`.")
                continue
            elif len(cut_files) > 1:
                raise FileNotFoundError(f"More than one cut file found in `{subfolder}/Cut-files/`.") # TODO: paths
            cut_file = cut_files[0]
            
            measurement = subfolder.name
            element = cut_file.suffix[1:]
            self.tree.insert("", tk.END, values=(measurement, element))

        # Need at least two points to fit        
        if len(self.tree.get_children()) >= 2:
            # enable fit button
            self.fit_btn["state"] = "normal"
        else:
            self.feedback_label.config(text="You need at least two cuts to fit.")

    
    def start_fit(self):
        a_params = analysis.generate_a_params(self.filehandler, self.selected_project)
        m_params = analysis.generate_m_params(a_params)
        analysis.save_m_params(m_params, self.filehandler.mparams_path)
        Log.info("Success", "Sucessfully fitted Bparams.")