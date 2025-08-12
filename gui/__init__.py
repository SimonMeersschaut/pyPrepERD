import tkinter as tk
from tkinter import ttk
import analysis
from .plot_frame import PlotFrame
from utils.plot import Plot
from .project_browser import ProjectBrowser
from utils.grid import create_grid
import sys
import signal

if sys.platform.startswith("win"):
    try:
        from ctypes import windll
        # Windows 8.1+  (1 = system DPI aware)
        windll.shcore.SetProcessDpiAwareness(1)
        # For Windows 10 per-monitor DPI awareness:
        # windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"Could not set DPI awareness: {e}")


class WhiteTheme:
    def __init__(self, root):
        style = ttk.Style(root)
        style.theme_use("clam")
        
        # Frame backgrounds
        style.configure('WhiteFrame.TFrame', background="#E0E0E0")
        
        # Headings
        style.configure('Heading.TLabel', background="#E0E0E0",
                        foreground="black", font=("Arial", 14, "bold"))
        
        # Default labels
        style.configure('TLabel', background="#E0E0E0", foreground="black")
        
        # Buttons
        style.configure('TButton', background="#E0E0E0",
                        foreground="black", borderwidth=0)
        style.map('TButton', background=[('active', '#E0E0E0')])


class TkinterUi:
    MIN_WIDTH = 800
    MIN_HEIGHT = 600

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("pyPrepERD")
        self.root.geometry(f"{TkinterUi.MIN_WIDTH}x{TkinterUi.MIN_HEIGHT}")
        self.root.minsize(TkinterUi.MIN_WIDTH, TkinterUi.MIN_HEIGHT)
        self.root.configure(bg="#282c36")
        self.theme = WhiteTheme(self.root)

        # Handle close button click
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Optional: Handle SIGINT to allow Ctrl+C to close the window
        signal.signal(signal.SIGINT, self.signal_handler)

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
        FILENAME = "tests/analysis/transform/ERD25_090_02A.ext"
        extended_data = analysis.load_extended_file(FILENAME)

        pixels = create_grid(extended_data, x_index=1, y_index=2)
        title = FILENAME.split('\\')[-1].split('/')[-1].split('.')[0] + ".mvt"
        plot = Plot(pixels, title)
        PlotFrame(plot).render_frame(graph_frame)

    def signal_handler(self, sig, frame):
        print("Ctrl+C pressed, closing...")
        self.root.destroy()
        sys.exit(0)

    def on_close(self):
        self.root.destroy()
        sys.exit(0)  # force the program to exit

    def run(self):
        self.root.mainloop()