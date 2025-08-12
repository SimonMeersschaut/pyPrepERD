import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

class PlotFrame:
    def __init__(self, plot):
        self.plot = plot
        self.canvas = None
        self.fig = None
        self.cid = None

    def render_frame(self, parent_frame):
        self.fig = self.plot.create_plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.draw()

        # Bind mouse event to canvas widget
        self.canvas.get_tk_widget().bind("<ButtonPress-1>", self.tk_callback)

        # Create matplotlib toolbar
        self.mpl_toolbar = NavigationToolbar2Tk(self.canvas, parent_frame, pack_toolbar=False)
        self.mpl_toolbar.update()

        # Pack the toolbar explicitly
        self.mpl_toolbar.pack(side=tk.TOP, fill=tk.X)

        # Create a frame for custom buttons next to toolbar
        button_frame = tk.Frame(parent_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Add some example buttons to your toolbar
        btn_clear = tk.Button(button_frame, text="Clear Points", command=self.clear_points)
        btn_clear.pack(side=tk.LEFT, padx=5)

        btn_save = tk.Button(button_frame, text="Save Figure", command=self.save_figure)
        btn_save.pack(side=tk.LEFT, padx=5)

        # Pack canvas below toolbar and buttons
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def clear_points(self):
        print("Clear points action triggered")
        self.plot.clear_points()  # You must implement this in your plot class
        self.fig.clf()
        self.fig = self.plot.create_plot()
        self.canvas.figure = self.fig
        self.canvas.draw()

    def save_figure(self):
        print("Save figure action triggered")
        self.fig.savefig("plot_saved.png")

    def tk_callback(self, event):
        if self.fig:
            ax = self.fig.axes[0]  # Assume one axes
            inv = ax.transData.inverted()

            canvas_widget = self.canvas.get_tk_widget()
            height = canvas_widget.winfo_height()

            flipped_y = height - event.y  # Flip Y coordinate

            xdata, ydata = inv.transform((event.x, flipped_y))
            print(f"[tk_bind] Mouse pressed at data coords: ({round(xdata)}, {round(ydata)})")

            self.plot.add_polygon_point((round(xdata), round(ydata)))
