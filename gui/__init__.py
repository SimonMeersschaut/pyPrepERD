import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import analysis
import ctypes
from .plot.plot_frame import PlotFrame
from gui.plot.plot import Plot
from .project_browser import ProjectBrowser
from utils.grid import create_grid
import sys
import threading
import signal
import glob

if sys.platform.startswith("win"):
    try:
        from ctypes import windll
        # Windows 8.1+  (1 = system DPI aware)
        windll.shcore.SetProcessDpiAwareness(1)
        # For Windows 10 per-monitor DPI awareness:
        # windll.shcore.SetProcessDpiAwareness(2)
    except Exception as e:
        print(f"Could not set DPI awareness: {e}")

WORK_DIR = "\\\\winbe.imec.be\\wasp\\ruthelde\\Simon\\test"

class WhiteTheme:
    def __init__(self, root):
        style = ttk.Style(root)
        # style.theme_use("clam")
        
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

    WIDTH = 900
    HEIGHT = 800

    def __init__(self):
        self.root = tk.Tk()
        self.root.iconbitmap("data/icon.ico")
        self.root.title("pyPrepERD")
        
        # --- Force taskbar icon ---
        # Set the App User Model ID (this is what Windows uses to group icons)
        app_id = "pyPrepERD.App"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        # Get the window handle (HWND)
        self.root.update_idletasks()  # make sure window exists
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

        # Load your icon
        hicon = ctypes.windll.user32.LoadImageW(
            0, "data/icon.ico", 1, 0, 0, 0x00000010 | 0x00000080
        )  # LR_LOADFROMFILE | LR_DEFAULTSIZE

        # Apply the icon to the window
        if hicon:
            ctypes.windll.user32.SendMessageW(hwnd, 0x80, 0, hicon)  # WM_SETICON = 0x80


        self.root.geometry(f"{TkinterUi.WIDTH-1}x{TkinterUi.HEIGHT-1}")
        self.root.minsize(TkinterUi.MIN_WIDTH, TkinterUi.MIN_HEIGHT)
        # self.root.configure(bg="#282c36")
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

        browser = ProjectBrowser(on_update=self.select_project)
        browser.render_frame(project_browser_frame)

        # Progress bar
        self.progressbar = ttk.Progressbar(mode="determinate", maximum=60)
        self.progressbar.place(x=30, y=60, width=200)
        self.status_label = ttk.Label(text="", background="#E0E0E0")
        self.status_label.place(x=240, y=60)

        # Graph Frame
        self.graph_frame = ttk.Frame(main_frame, padding="10", style='DarkFrame.TFrame')
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        # 
        self.plot = Plot()
        self.plotframe = PlotFrame(self.plot)
        self.plotframe.render_frame(self.graph_frame)

        #
        self.select_project("C:\\Users\\meerss01\\Desktop\\01A")

        #
        self.root.after(500, self._force_resize) # needed for plot to render correctly

    def _force_resize(self, ):
        """
        Tiny resize jiggle: grow by 1px then restore after `delay_restore_ms`. TODO is niet meer correct
        This forces the WM/backend to recompute layout so embedded Matplotlib lays out correctly.
        """
        self.root.geometry(f"{TkinterUi.WIDTH}x{TkinterUi.HEIGHT}")

    def signal_handler(self, sig, frame):
        print("Ctrl+C pressed, closing...")
        self.root.destroy()
        sys.exit(0)

    def on_close(self):
        self.root.destroy()
        sys.exit(0)  # force the program to exit

    def run(self):
        self.root.mainloop()
    
    
    def select_project(self, path: str):
        """Called by ProjectBrowser when a new folder is selected."""

        # Start the progress bar on the main thread
        self.progressbar.start()
        self.status_label.config(text="")

        def worker():
            try:
                flt_files = glob.glob(path+"\\*.flt")
                if len(flt_files) == 0:
                    raise ValueError(f"No flt files found in {path}.")
                if len(flt_files) > 1:
                    raise ValueError(f"More than one flt file found in {path}.")
                
                self.plotframe.mpl_toolbar.current_project_dir = path
                
                # --- Heavy work happens in the thread ---
                flt_data = analysis.load_flt_file(flt_files[0])
                ns_ch, t_offs = analysis.load_tof_file(WORK_DIR + "/Tof.in")
                B0, B1, B2 = analysis.load_bparams_file(WORK_DIR + "/Bparams.txt")
                extended_data = analysis.extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)
                pixels = create_grid(extended_data, x_index=1, y_index=2)
                title = flt_files[0].split('\\')[-1].split('/')[-1].split('.')[0] + ".mvt"

                # Schedule UI update back on the main thread
                self.root.after(0, lambda: self._update_plot(pixels, extended_data, title))

            except Exception as e:
                print(f"Error in worker:", e)
                tkinter.messagebox.showerror("Error opening folder", str(e))
                # Schedule GUI cleanup on main thread
                self.root.after(0, lambda: self._cleanup_on_error())

        # Run the worker in a separate thread so the GUI stays responsive
        threading.Thread(target=worker, daemon=True).start()

    def _cleanup_on_error(self):
        self.progressbar.stop()
        self.plot.clear()
        self.status_label.config(text="❌ Error")

    def _update_plot(self, pixels, extended_data, title):
        """Updates plot and stops the progress bar — runs in main thread."""
        self.plot.set_data(pixels, extended_data, title)
        
        # Show completion clearly
        self.progressbar.stop()
        self.progressbar.config(maximum=60, value=60)
        self.status_label.config(text="✅ Finished")