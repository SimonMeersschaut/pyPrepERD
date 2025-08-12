from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PlotFrame:
    def __init__(self, plot):
        self.plot = plot
    
    def render_frame(self, parent_frame):
        fig = self.plot.create_plot()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)