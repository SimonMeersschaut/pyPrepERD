import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from .navigation_bar import CustomToolBar, _MoreModes


class PlotFrame:
    def __init__(self, plot):
        self.plot = plot
        self.canvas = None
        self.fig = None
        self.cid = None

    def render_frame(self, parent_frame):
        self.fig = self.plot.create_plot()

        # Adjust layout to prevent title from being cut off
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])  # Leave space at the top for the title

        self.canvas = FigureCanvasTkAgg(self.fig, master=parent_frame)
        self.canvas.draw()

        # Bind mouse event to canvas widget
        self.canvas.get_tk_widget().bind("<ButtonPress-1>", self.tk_callback, add=True)

        # Create matplotlib toolbar
        self.mpl_toolbar = CustomToolBar(self.canvas, self.plot, parent_frame, pack_toolbar=False)
        self.mpl_toolbar.update()

        # Pack the toolbar explicitly
        self.mpl_toolbar.pack(side=tk.TOP, fill=tk.X)

        # Pack canvas below toolbar and buttons
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


    def clear_points(self):
        print("Clear points action triggered")
        self.plot.clear_points()  # You must implement this in your plot class
        self.fig.clf()
        self.fig = self.plot.create_plot()
        self.canvas.figure = self.fig
        self.canvas.draw()

    def tk_callback(self, event):
        if self.fig:
            if self.mpl_toolbar.mode == _MoreModes.POLYGON:
                # draw polygon mode
                ax = self.fig.axes[0]  # Assume one axes
                inv = ax.transData.inverted()

                canvas_widget = self.canvas.get_tk_widget()
                height = canvas_widget.winfo_height()

                flipped_y = height - event.y  # Flip Y coordinate

                xdata, ydata = inv.transform((event.x, flipped_y))

                self.plot.add_polygon_point((round(xdata), round(ydata)))

                if len(self.plot.polygon_points) >= 3:
                    selected_points: list = self.plot.get_selected_points()

                    self.mpl_toolbar.show_selected_points(len(selected_points))
