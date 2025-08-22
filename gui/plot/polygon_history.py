import tkinter as tk
from tkinter import ttk
import utils

class PolygonHistory:
    def __init__(self, master, filehandler, callback: callable):
        self.callback = callback
        self.filehandler = filehandler
        self.master = master
        self.open_polygon_btn = None
        self.tree = None
        self.window = None

    def start(self):
        self.window = tk.Toplevel(self.master)
        self.window.title("pyPrepERD - Polygon history")
        self.window.geometry("500x400")
        self.window.minsize(500, 400)
        self.window.iconbitmap(utils.IMAGES_PATH / "icon.ico")

        # Frame for folder selection (not used yet but useful for expansion)
        selection_frame = tk.Frame(self.window)
        selection_frame.pack(pady=10, fill="x", padx=20)

        # Treeview for showing folder-element pairs
        self.tree = ttk.Treeview(
            self.window, 
            columns=("Measurement", "Element"), 
            show="headings", 
            selectmode="browse"
        )
        self.tree.heading("Measurement", text="Measurement")
        self.tree.heading("Element", text="Element")
        self.tree.pack(pady=20, fill="both", expand=True)

        # Enable selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Open button
        self.open_polygon_btn = tk.Button(self.window, text="Open polygon", command=self._open_selected_polygon)
        self.open_polygon_btn["state"] = "disabled"
        self.open_polygon_btn.pack(pady=5)

        self.load_history()
    
    def load_history(self):
        history = utils.Config.get_polygon_history()

        # Clear old entries
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insert new ones
        for _, data in history.items():
            path = data["dir"]
            element = data.get("atom", "")
            polygon = data.get("polygon", [])

            # Insert row and stash polygon data in tags
            iid = self.tree.insert("", "end", values=(path, element))
            self.tree.item(iid, tags=(str(polygon),))  # store polygon safely as string

    def _on_select(self, event):
        if self.tree.selection():
            self.open_polygon_btn["state"] = "normal"
        else:
            self.open_polygon_btn["state"] = "disabled"

    def _open_selected_polygon(self):
        print("selecting")
        selection = self.tree.selection()
        if not selection:
            return
        iid = selection[0]
        polygon_str = self.tree.item(iid, "tags")[0]
        polygon = eval(polygon_str)  # turn back into list (safe since you control the data)

        if self.callback:
            self.callback(polygon)
            self.window.destroy()