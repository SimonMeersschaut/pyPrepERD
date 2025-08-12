import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt

class PlotFrame:
    def __init__(self, plot):
        self.plot = plot

    def render_frame(self, parent_frame):
        fig = self.plot.create_plot()
        self.canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        self.canvas.draw()

        # Connect to matplotlib event
        self.canvas.mpl_connect('button_press_event', self.callback)

        toolbar = NavigationToolbar2Tk(self.canvas, parent_frame, pack_toolbar=False)
        toolbar.update()

        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def callback(self, event):
        print(f"Mouse pressed at pixel coords: ({event.x}, {event.y})")
        print(f"Mouse pressed at data coords: ({event.xdata}, {event.ydata})")

class MyPlot:
    def create_plot(self):
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3], [1, 4, 9])
        return fig

root = tk.Tk()
frame = tk.Frame(root)
frame.pack(fill="both", expand=True)

pf = PlotFrame(MyPlot())
pf.render_frame(frame)

root.mainloop()
