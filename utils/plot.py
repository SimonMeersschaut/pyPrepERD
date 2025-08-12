import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.ticker as ticker
import numpy as np

@dataclass
class Plot:
    pixels: any  # TODO: specify type if possible
    display_title: str
    
    fig: plt.Figure = field(init=False, default=None)
    ax: plt.Axes = field(init=False, default=None)
    polygon_points: list[tuple[float, float]] = field(default_factory=list, init=False)

    def create_plot(self):
        if self.pixels is None:
            raise ValueError("`pixels` cannot be `None`.")

        self.fig, self.ax = plt.subplots()

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

        norm_anchor_vals = (np.log2(anchor_values) - np.log2(anchor_values[0])) / \
                           (np.log2(anchor_values[-1]) - np.log2(anchor_values[0]))

        cmap = LinearSegmentedColormap.from_list(
            "custom_cmap", list(zip(norm_anchor_vals, anchor_colors))
        )

        norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=128, base=2)

        white_pixels = np.where(self.pixels == 0, 1, np.nan)
        self.ax.pcolormesh(white_pixels, cmap=ListedColormap(["white"]), vmin=0, vmax=1)

        masked_pixels = np.where(self.pixels >= 1, self.pixels, np.nan)
        im = self.ax.pcolormesh(masked_pixels, cmap=cmap, norm=norm)

        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label('Counts')
        cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        self.ax.set_title(self.display_title)
        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        # Plot existing polygon points if any (for redraw)
        if self.polygon_points:
            xs, ys = zip(*self.polygon_points)
            self.ax.scatter(xs, ys, color='red', marker='o')

        return self.fig

    def add_polygon_point(self, point: tuple[float, float]):
        if self.ax is None:
            raise RuntimeError("Plot must be created first by calling `create_plot()`.")

        # Store the point
        self.polygon_points.append(point)

        # Plot the point on the current axis
        self.ax.scatter(point[0], point[1], color='red', marker='o')

        # Redraw canvas to update the figure immediately
        self.fig.canvas.draw_idle()

    def save(self, filename: str):
        if self.fig is None:
            self.create_plot()
        self.fig.savefig(filename)
