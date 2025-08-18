import tkinter as tk
from tkinter import filedialog, ttk
import analysis
import utils
import os
import glob


class FitWizard:
    def __init__(self, master):
        self.master = master
        
        self.selected_project: str = None
        self.fit_btn = None

    def start(self):
        new_window = tk.Toplevel(self.master)
        new_window.title("Fit Wizard")
        new_window.geometry("500x400")
        new_window.minsize(500, 400)
        new_window.iconbitmap(utils.IMAGES_PATH + "icon.ico")

        # tk.Label(new_window, text="Select a project folder.").pack(pady=10)

        # Frame for folder selection
        folder_frame = tk.Frame(new_window)
        folder_frame.pack(pady=10, fill="x", padx=20)

        tk.Label(folder_frame, text="Project folder:").grid(row=0, column=0, sticky="w")
        # self.folder_entry = tk.Label(folder_frame, width=50)
        # self.folder_entry.grid(row=0, column=1, padx=5)

        browse_btn = tk.Button(folder_frame, text="Browse", command=self.browse_folder)
        browse_btn.grid(row=0, column=2, padx=5)

        # Treeview for showing folder-element pairs
        self.tree = ttk.Treeview(new_window, columns=("Measurement", "Element"), show="headings", selectmode="browse")
        self.tree.heading("Measurement", text="Measurement")
        self.tree.heading("Element", text="Element")
        self.tree.pack(pady=20, fill="both", expand=True)

        # Fit button
        self.fit_btn = tk.Button(new_window, text="Start Fit", command=self.start_fit)
        self.fit_btn["state"] = "disabled"
        self.fit_btn.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()

        if not folder:
            # user canceled
            return 

        if not os.path.exists(folder):
            raise FileNotFoundError(f"Porject folder `{folder}` not found.")
        
        self.selected_project = folder

        self.tree.delete(*self.tree.get_children())

        # scan folder for subdirectories
        subfolders = [f.path for f in os.scandir(folder) if f.is_dir() and not "raw" in f.path[0]] # TODO: `in` aanpassen
        
        if len(subfolders) == 0:
            raise ValueError("The selected folder did not contain any subfolders. Be sure to select a project folder.")
        
        for subfolder in subfolders:
            # Search lst file
            if len(glob.glob(subfolder+"/*.lst")) == 0:
                raise FileNotFoundError("No .lst file found in the subfolder.")
            # search polygon cut
            if not os.path.exists(subfolder+"/Cut-files"):
                raise FileNotFoundError(subfolder + " did not contain a `Cut-files` folder.")
            cut_files = glob.glob(subfolder+"/Cut-files/*.*")
            if len(cut_files) == 0:
                raise FileNotFoundError(f"No cut files found in `{subfolder}/Cut-files/`.")
            elif len(cut_files) > 1:
                raise FileNotFoundError(f"More than one cut file found in `{subfolder}/Cut-files/`.")
            
            measurement = subfolder.split('/')[-1].split('\\')[-1]
            element = cut_files[0].split('.')[-1]
            self.tree.insert("", tk.END, values=(measurement, element))

        # Need at least two points to fit        
        if len(self.tree.get_children()) >= 2:
            # enable fit button
            self.fit_btn["state"] = "normal"

    
    def start_fit(self):
        analysis.generate_a_params(self.selected_project)
