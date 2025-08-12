import matplotlib.pyplot as plt
from dataclasses import dataclass
import matplotlib.colors as colors
from matplotlib.cm import get_cmap
import quads
from .grid import create_grid


@dataclass
class Graph:
    tree: quads.QuadTree
    display_title: str
    filename: str

    def create_plot(self):
        if self.tree is None:
            raise ValueError("`tree` cannot be `None`.")

        pixels = create_grid(self.tree)  # Assuming pixels is a 2D numpy array of counts or intensities

        fig, ax = plt.subplots()

        cmap = get_cmap('gnuplot2') # color scheme

        # Normalize pixels to color range, here assuming max value 128 from colorbar
        norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03,
            vmin=1, vmax=1E4, base=10)

        # Show image with colormap and normalization
        im = ax.pcolormesh(pixels, cmap=cmap, norm=norm, )

        # Add colorbar on the right
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Counts')

        ax.set_title(self.display_title)
        ax.set_xlabel('Time of flight (ns)')
        ax.set_ylabel('Energy channel')

        # You can customize ticks here if needed, and axis limits

        return fig

    def render_frame(self, parent_frame):
        # fig = self.create_plot()
        # canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill="both", expand=True)
        ...

    def show(self):
        self.create_plot()
        plt.show()
