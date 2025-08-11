# import matplotlib
# matplotlib.rcParams['path.simplify_threshold'] = 1.0
# matplotlib.rcParams['agg.path.chunksize'] = 10000
# matplotlib.use("Agg")  # Avoid default GUI backend conflicts
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg



@dataclass
class Graph:
    x: np.array
    y: np.array
    display_title: str
    filename: str

    def create_plot(self):
        bg_color = "#282c36"  # same as Tkinter DarkFrame background

        # Create figure and set background
        fig, ax = plt.subplots(facecolor=bg_color)
        ax.set_facecolor(bg_color)

        # Plot series with custom colors for contrast
        ax.scatter(self.x, self.y, marker='x', linewidths=.1, color="#7FDBFF", label="Series 1")
        
        # ax.set(
        #     xlim=(0, 8), xticks=np.arange(1, 8),
        #     ylim=(0, 8), yticks=np.arange(1, 8),
        #     title=self.display_title,
        #     # titlepad=15
        # )

        # Set text colors for dark background
        ax.tick_params(colors="white")
        ax.xaxis.label.set_color("white")
        ax.yaxis.label.set_color("white")
        ax.title.set_color("white")
        for spine in ax.spines.values():
            spine.set_color("white")

        ax.legend(facecolor=bg_color, edgecolor="white", labelcolor="white")

        return fig

    def render_frame(self, parent_frame):
        fig = self.create_plot()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show(self):
        self.create_plot()
        plt.show()
