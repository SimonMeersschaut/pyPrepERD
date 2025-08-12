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

        # Try matplotlib event first (usually works)
        # self.cid = self.canvas.mpl_connect('button_press_event', self.callback)

        # Also bind Tkinter event on the canvas widget directly (fallback)
        self.canvas.get_tk_widget().bind("<ButtonPress-1>", self.tk_callback)

        toolbar = NavigationToolbar2Tk(self.canvas, parent_frame, pack_toolbar=False)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill="both", expand=True)


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
