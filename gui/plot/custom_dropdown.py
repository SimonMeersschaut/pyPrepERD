import tkinter as tk
from tkinter import ttk

class CustomDropdown(tk.Frame):
    def __init__(self, parent, text, options, default_value, command, data_map):
        super().__init__(parent)
        self.command = command
        self.var = tk.StringVar(value=default_value)
        self.options = options
        self.data_map = data_map  # dict: option -> bool (True=has data, False=no data)

        # Entry to show the selected value
        self.entry = tk.Entry(self, textvariable=self.var, state="readonly", width=10)
        self.entry.pack(side=tk.LEFT, fill=tk.X)

        # Dropdown button
        self.button = ttk.Button(self, text="▼", width=2, command=self.toggle_listbox)
        self.button.pack(side=tk.LEFT)

        # Hidden Listbox with styling
        self.listbox = tk.Listbox(self, height=min(5, len(options)))
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        # Populate listbox with per-item styles
        for opt in options:
            self.listbox.insert(tk.END, opt)
            idx = self.listbox.size() - 1
            if self.data_map.get(opt, False):
                self.listbox.itemconfig(idx, fg="green")  # has data
            else:
                self.listbox.itemconfig(idx, fg="red")    # no data

    def toggle_listbox(self):
        if self.listbox.winfo_ismapped():
            self.listbox.pack_forget()
        else:
            self.listbox.pack(side=tk.BOTTOM, fill=tk.X)

    def on_select(self, event):
        selection = self.listbox.get(self.listbox.curselection())
        self.var.set(selection)
        self.listbox.pack_forget()
        if self.command:
            self.command(selection)


# Example usage replacing your _Dropdown
def _Dropdown(parent, text, options, default_value, command, data_map):
    return CustomDropdown(parent, text, options, default_value, command, data_map)


if __name__ == "__main__":
    root = tk.Tk()

    options = ["Option A", "Option B", "Option C"]
    data_map = {"Option A": True, "Option B": False, "Option C": True}

    def on_select(value):
        print("Selected:", value)

    dropdown = _Dropdown(root, "Choose", options, "Option A", on_select, data_map)
    dropdown.pack(pady=10)

    root.mainloop()
