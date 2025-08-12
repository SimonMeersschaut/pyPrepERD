import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.lines import Line2D

@dataclass
class Plot:
    pixels: any  # TODO: specify type if possible
    display_title: str
    
    fig: plt.Figure = field(init=False, default=None)
    ax: plt.Axes = field(init=False, default=None)
    polygon_points: list[tuple[float, float]] = field(default_factory=list, init=False)
    polygon_line: Line2D = field(init=False, default=None)

    def create_plot(self):
        if self.pixels is None:
            raise ValueError("`pixels` cannot be `None`.")

        self.fig, self.ax = plt.subplots()

        # Anchor colors from your original scale
        anchor_values = np.array([1, 2, 4, 8, 16, 32])
        anchor_colors = [
            "#000000",  # black
            # "#550000",  # dark red
            # "#aa0000",  # red
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

        norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=32, base=2)

        white_pixels = np.where(self.pixels == 0, 1, np.nan)
        self.ax.pcolormesh(white_pixels, cmap=ListedColormap(["white"]), vmin=0, vmax=1)

        masked_pixels = np.where(self.pixels >= 1, self.pixels, np.nan)

        self.background = self.ax.pcolormesh(masked_pixels, cmap=cmap, norm=norm)  # drawn once
        self.scatter = self.ax.scatter([], [], color='red', marker='o')            # start empty
        self.polygon_line, = self.ax.plot([], [], color='red')
        self.closing_line, = self.ax.plot([], [], color='orange', linestyle='--')

        cbar = self.fig.colorbar(self.background, ax=self.ax)
        cbar.set_label('Counts')
        cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        self.ax.set_title(self.display_title)
        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        return self.fig

    def add_polygon_point(self, point):
        self.polygon_points.append(point)

        # Update scatter points
        self.scatter.set_offsets(self.polygon_points)

        # Update solid line
        if len(self.polygon_points) > 1:
            xs, ys = zip(*self.polygon_points)
            self.polygon_line.set_data(xs, ys)

            # Update closing edge
            self.closing_line.set_data(
                [self.polygon_points[-1][0], self.polygon_points[0][0]],
                [self.polygon_points[-1][1], self.polygon_points[0][1]]
            )

        self.fig.canvas.draw_idle()

    def save(self, filename: str):
        if self.fig is None:
            self.create_plot()
        self.fig.savefig(filename)
