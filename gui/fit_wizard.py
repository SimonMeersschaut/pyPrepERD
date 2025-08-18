import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import utils
import os
import glob


class FitWizard:
    def __init__(self, master):
        self.master = master

    def start(self):
        new_window = tk.Toplevel(self.master)
        new_window.title("Fit Wizard")
        new_window.geometry("800x400")
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

        # Bind selection to populate entry fields for editing
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Fit button
        fit_btn = tk.Button(new_window, text="Start Fit", command=self.start_fit)
        fit_btn.pack(pady=5)

    def browse_folder(self):
        folder = filedialog.askdirectory()

        if not folder:
            # user canceled
            return 

        if not os.path.exists(folder):
            raise FileNotFoundError(f"Porject folder `{folder}` not found.")
        
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


    def add_or_update(self):
        # folder = self.folder_entry.get()
        element = self.element_combo.get()

        # if not folder:
        #     messagebox.showerror("Error", "Please select a folder")
        #     return
        if not element:
            messagebox.showerror("Error", "Please select an element")
            return

        # selected = self.tree.selection()
        # if selected:
            # Update existing item
            # self.tree.item(selected, values=(folder, element))
        # else:
            # Add new item
            # self.tree.insert("", tk.END, values=(folder, element))

        # self.folder_entry.delete(0, tk.END)
        # self.element_combo.set("")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            folder, element = self.tree.item(selected, "values")
            # self.folder_entry.delete(0, tk.END)
            # self.folder_entry.insert(0, folder)
            self.element_combo.set(element)
    
    def start_fit(self):
        print("Started fitting.")

    # def remove_selected(self):
    #     selected = self.tree.selection()
    #     if selected:
    #         self.tree.delete(selected)
