import matplotlib.pyplot as plt
from dataclasses import dataclass
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import ListedColormap
import matplotlib.ticker as ticker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

@dataclass
class Graph:
    pixels: any # TODO
    display_title: str
    filename: str

    def create_plot(self):
        if self.pixels is None:
            raise ValueError("`pixels` cannot be `None`.")

        fig, ax = plt.subplots()

        # Anchor colors from your original scale
        anchor_values = np.array([1, 2, 4, 8, 16, 32, 64, 128])
        anchor_colors = [
            "#000000",  # black
            "#550000",  # dark red
            "#aa0000",  # red
            "#ff5500",  # orange-red
            "#ffff00",  # yellow
            "#00ff00",  # green
            "#00ffff",  # cyan/light blue
            "#0000ff"   # blue
        ]

        # Normalize anchor values to [0,1] for colormap definition
        norm_anchor_vals = (np.log2(anchor_values) - np.log2(anchor_values[0])) / \
                        (np.log2(anchor_values[-1]) - np.log2(anchor_values[0]))

        # Build continuous colormap for values >= 1
        cmap = LinearSegmentedColormap.from_list(
            "custom_cmap", list(zip(norm_anchor_vals, anchor_colors))
        )

        # SymLogNorm for values >= 1
        norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=128, base=2)

        # -------- LAYER 1: Plot white background where values == 0 --------
        white_pixels = np.where(self.pixels == 0, 1, np.nan)  # 1 just as dummy, NaN elsewhere
        ax.pcolormesh(white_pixels, cmap=ListedColormap(["white"]), vmin=0, vmax=1)

        # -------- LAYER 2: Plot normal log-scaled data where values >= 1 --------
        masked_pixels = np.where(self.pixels >= 1, self.pixels, np.nan)
        im = ax.pcolormesh(masked_pixels, cmap=cmap, norm=norm)

        # Colorbar
        cbar = fig.colorbar(im, ax=ax)
        cbar.set_label('Counts')
        cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        ax.set_title(self.display_title)
        # ax.set(xlim=(0, 300), ylim=(0, 8000))
        ax.set_xlabel('Time of flight (ns)')
        ax.set_ylabel('Energy channel')

        return fig


    def render_frame(self, parent_frame):
        fig = self.create_plot()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def show(self):
        self.create_plot()
        plt.show()
