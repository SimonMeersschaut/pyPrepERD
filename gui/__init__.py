import tkinter as tk
from tkinter import ttk
import analysis
from .graphs import Graph
from .project_browser import ProjectBrowser

import sys

if sys.platform.startswith("win"):
    try:
        from ctypes import windll
        # Windows 8.1+  (1 = system DPI aware)
        windll.shcore.SetProcessDpiAwareness(1)
        # For Windows 10 per-monitor DPI awareness:
        # windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"Could not set DPI awareness: {e}")


class DarkTheme:
    def __init__(self, root):
        style = ttk.Style(root)
        style.theme_use("clam")
        style.configure('DarkFrame.TFrame', background="#282c36")
        style.configure('Heading.TLabel', background="#282c36",
                        foreground="white", font=("Arial", 14, "bold"))
        style.configure('TLabel', background="#282c36", foreground="white")
        style.configure('TButton', background="#3c3f41",
                        foreground="white", borderwidth=0)
        style.map('TButton', background=[('active', '#505357')])


class TkinterUi:
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("pyPrepERD")
        self.root.geometry(f"{TkinterUi.MIN_WIDTH}x{TkinterUi.MIN_HEIGHT}")
        self.root.minsize(TkinterUi.MIN_WIDTH, TkinterUi.MIN_HEIGHT)
        self.root.configure(bg="#282c36")

        self.theme = DarkTheme(self.root)

    def initialize(self):
        main_frame = ttk.Frame(self.root, padding="10",
                               style='DarkFrame.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(main_frame, text="📊 Graph Display",
                  style='Heading.TLabel').pack(anchor=tk.NW, pady=(0, 10))

        # Show project browser
        project_browser_frame = ttk.Frame(
            main_frame, padding="10", style='DarkFrame.TFrame')
        project_browser_frame.pack(fill=tk.BOTH, expand=True)

        browser = ProjectBrowser()
        browser.render_frame(project_browser_frame)

        # Graph Frame
        graph_frame = ttk.Frame(main_frame, padding="10", style='DarkFrame.TFrame')
        graph_frame.pack(fill=tk.BOTH, expand=True)

        # Create and render graph
        extended_data = analysis.load_extended_file("tests/analysis/transform/ERD25_090_02A.ext")
        graph = Graph(extended_data[:,2][::20], extended_data[:,0][::20], "My Dark Graph", "graph.png")
        graph.render_frame(graph_frame)

    def run(self):
        self.root.mainloop()
