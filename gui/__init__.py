import tkinter as tk
from tkinter import ttk
import analysis
import utils
import sys
import threading
import signal
import glob
from pathlib import Path

from utils import FileHandler, Log
from utils.grid import create_grid

from .plot.plot_frame import PlotFrame
from gui.plot import InteractiveERDPlot
from .menu_bar import CustomMenuBar
from .project_browser import ProjectBrowser
from .fit_wizard import FitWizard


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

    def __init__(self, filehandler: FileHandler, headless=False):
        self.filehandler = filehandler
        self.workdir = self.filehandler.transfer_ERD_path / "ERD_999_TEST" # TODO: replace with glob

        self.root = tk.Tk(useTk=not headless)
        self.root.iconbitmap(self.filehandler.images_path / "icon.ico")
        self.root.title("pyPrepERD")

        if not headless:

            self.menubar = CustomMenuBar(
                self.root,
                project_browser=ProjectBrowser(self.root, lambda path: self.select_project(Path(path)), self.filehandler.transfer_ERD_path),
                fit_wizard=FitWizard(self.root, self.filehandler)
            )
            
            self.root.geometry(f"{TkinterUi.WIDTH-1}x{TkinterUi.HEIGHT-1}")
            self.root.minsize(TkinterUi.MIN_WIDTH, TkinterUi.MIN_HEIGHT)
            # self.root.configure(bg="#282c36")
            self.theme = WhiteTheme(self.root)

            # Handle close button click
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)

            # Optional: Handle SIGINT to allow Ctrl+C to close the window
            signal.signal(signal.SIGINT, self.signal_handler)

            self.root.config(menu=self.menubar)

    def initialize(self):
        main_frame = ttk.Frame(self.root, padding="10",
                               style='DarkFrame.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Progress bar
        self.progressbar = ttk.Progressbar(mode="determinate", maximum=60)
        self.status_label = ttk.Label(text="", background="#E0E0E0")

        # Graph Frame
        self.graph_frame = ttk.Frame(main_frame, padding="10", style='DarkFrame.TFrame')
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

        self.plot = InteractiveERDPlot()
        self.plotframe = PlotFrame(self.plot, self.filehandler)
        self.plotframe.render_frame(self.graph_frame)

        self.select_project(self.workdir)

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

    def run(self, block=True):
        if block:
            self.root.mainloop()
    
    
    def select_project(self, path: Path):
        """Called by ProjectBrowser when a new folder is selected."""
        # Start the progress bar on the main thread
        self.progressbar.start()
        self.status_label.config(text="")

        def worker():
            try:
                flt_files = glob.glob(str(path / "*.flt"))
                if len(flt_files) == 0:
                    raise ValueError(f"No flt files found in {path}.")
                if len(flt_files) > 1:
                    raise ValueError(f"More than one flt file found in {path}.")
                flt_file = Path(flt_files[0])
                
                self.plotframe.mpl_toolbar.set_project_dir(path)
                
                # --- Heavy work happens in the thread ---
                flt_data = analysis.load_flt_file(flt_file)
                ns_ch, t_offs = analysis.load_tof_file(self.filehandler.tof_file_path)
                B0, B1, B2 = analysis.load_bparams_file(self.filehandler.bparams_file_path)
                extended_data = analysis.extend_flt_data(flt_data, B0, B1, B2, ns_ch, t_offs)
                pixels, extent = create_grid(extended_data, x_index=1, y_index=2)
                title = self.filehandler.get_stem(Path(flt_file)) + ".evt"
                self.plot.set_title(title)

                # Schedule UI update back on the main thread
                self.root.after(0, lambda: self._update_plot(pixels, extended_data, extent))

            except Exception as e:
                print(f"Error in worker:", e)
                Log.error("Uncaught error", "Error opening folder", str(e))
                # Schedule GUI cleanup on main thread
                self.root.after(0, lambda: self._cleanup_on_error())
                raise e

        # Run the worker in a separate thread so the GUI stays responsive
        threading.Thread(target=worker, daemon=True).start()

    def _cleanup_on_error(self):
        self.progressbar.stop()
        self.plot.clear()
        self.status_label.config(text="❌ Error")

    def _update_plot(self, pixels, extended_data, extent):
        """Updates plot and stops the progress bar — runs in main thread."""
        self.plot.set_data(pixels, extended_data)
        self.plot.extent = extent
        
        # Show completion clearly
        self.progressbar.stop()
        self.progressbar.config(maximum=60, value=60)
        self.status_label.config(text="✅ Finished")

        # Now the plot is loaded, update the element dropdown
        # this will load the current element, the associated polygon
        # and will draw the polygon to the screen
        self.plotframe.mpl_toolbar.update_element_dropdown(None)