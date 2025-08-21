import tkinter as tk
import webbrowser

class CustomMenuBar(tk.Menu):
    def __init__(self, root, project_browser, fit_wizard):
        super().__init__(root)

        self.project_browser = project_browser
        self.fit_wizard = fit_wizard

        # File menu
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="Open", accelerator="Ctrl+O", command=lambda: self.project_browser._choose_folder())
        root.bind("<Control-o>", lambda _: self.project_browser._choose_folder())
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)
        self.add_cascade(label="File", menu=file_menu)

        # Fit menu
        edit_menu = tk.Menu(self, tearoff=0)
        edit_menu.add_command(label="Fit Wizard", accelerator="Ctrl+F", command= lambda : self.fit_wizard.start())
        root.bind("<Control-f>", lambda _: self.fit_wizard.start())
        self.add_cascade(label="Fit", menu=edit_menu)

        # Help menu
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", accelerator="Ctrl+H", command=lambda: webbrowser.open("https://github.com/SimonMeersschaut/pyPrepERD/blob/main/README.md"))
        root.bind("<Control-h>", lambda _: webbrowser.open("https://github.com/SimonMeersschaut/pyPrepERD/blob/main/README.md"))
        self.add_cascade(label="Help", menu=help_menu)
        
        self.fit_wizard.start()