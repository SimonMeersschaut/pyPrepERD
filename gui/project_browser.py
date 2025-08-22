import tkinter as tk
from tkinter import ttk
import os
from utils import Log


class ProjectBrowser:
    def __init__(self, parent, on_update: callable, root_dir="transfer_ERD"):
        self.on_update = on_update
        self.parent = parent
        self.root_dir = root_dir
    
    def _choose_folder(self):
        # Create popup window
        self.popup = tk.Toplevel(self.parent)
        self.popup.title("Select Project Folder")
        self.popup.geometry("400x400")

        # Treeview for folders
        self.tree = ttk.Treeview(self.popup)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewOpen>>", self.on_open)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

        # Populate root folders
        self.populate_tree(self.root_dir)

    def populate_tree(self, path, parent=""):
        for entry in sorted(os.listdir(path)):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                valid = self.is_valid(full_path)
                tag = "valid" if valid else "invalid"
                self.tree.insert(parent, "end", full_path, text=entry, tags=(tag,))
        # Configure colors
        self.tree.tag_configure("invalid", foreground="gray")
        self.tree.tag_configure("valid", foreground="black")

    def on_open(self, event):
        node = self.tree.focus()
        if not self.tree.get_children(node):
            self.populate_tree(node, node)

    def on_select(self, event):
        node = self.tree.focus()
        if self.is_valid(node):
            self.on_update(node)
            self.popup.destroy()  # Close popup after selection
        else:
            Log.warn("Invalid Folder", "This folder is invalid. Must contain .flt files.")

    def is_valid(self, folder_path):
        # Replace with your actual validity logic
        return any(f.endswith(".flt") for f in os.listdir(folder_path))