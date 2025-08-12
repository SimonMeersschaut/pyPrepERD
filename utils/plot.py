import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.ticker as ticker
import numpy as np
from .polygon import is_point_in_polygon

@dataclass
class Plot:
    pixels: any
    display_title: str

    fig: plt.Figure = field(init=False, default=None)
    ax: plt.Axes = field(init=False, default=None)

    polygon_points: list[tuple[float, float]] = field(default_factory=list, init=False)
    scatter = None
    polygon_line = None
    closing_line = None
    background = None  # for blitting

    def create_plot(self):
        if self.pixels is None:
            raise ValueError("`pixels` cannot be `None`.")

        self.fig, self.ax = plt.subplots()

        anchor_values = np.array([1, 2, 4, 8, 16, 32])
        anchor_colors = [
            "#000000", "#ff5500", "#ffff00", "#00ff00", "#00ffff", "#0000ff"
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
        im = self.ax.pcolormesh(masked_pixels, cmap=cmap, norm=norm)

        cbar = self.fig.colorbar(im, ax=self.ax)
        cbar.set_label('Counts')
        cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        self.ax.set_title(self.display_title)
        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        # Empty artists for updates
        self.scatter = self.ax.scatter([], [], color='red', marker='o')
        self.polygon_line, = self.ax.plot([], [], color='red')
        self.closing_line, = self.ax.plot([], [], color='orange', linestyle='--')

        # Force correct layout before background capture
        self.fig.tight_layout()
        self.scatter.set_visible(False)
        self.polygon_line.set_visible(False)
        self.closing_line.set_visible(False)

        self.fig.canvas.draw()  # now the layout is correct
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        
        # Restore visibility
        self.scatter.set_visible(True)
        self.polygon_line.set_visible(True)
        self.closing_line.set_visible(True)

        # Update background automatically on every full draw
        self.fig.canvas.mpl_connect("draw_event", self._update_background)

        return self.fig

    def add_polygon_point(self, point: tuple[float, float]):
        self.polygon_points.append(point)

        # Restore background (fast)
        self.fig.canvas.restore_region(self.background)

        # Update scatter points
        self.scatter.set_offsets(self.polygon_points)

        if len(self.polygon_points) > 1:
            xs, ys = zip(*self.polygon_points)
            self.polygon_line.set_data(xs, ys)

            self.closing_line.set_data(
                [self.polygon_points[-1][0], self.polygon_points[0][0]],
                [self.polygon_points[-1][1], self.polygon_points[0][1]]
            )

        # Draw updated artists
        self.ax.draw_artist(self.scatter)
        self.ax.draw_artist(self.polygon_line)
        self.ax.draw_artist(self.closing_line)

        # Blit the updated region
        self.fig.canvas.blit(self.ax.bbox)
        self.fig.canvas.flush_events()

        self.calculate_containing_points()
    
    def calculate_containing_points(self):
        if len(self.polygon_points) < 3:
            return
        
        if is_point_in_polygon((100, 100), self.polygon_points):
            print("Point (100, 100) is inside the polygon.")
        

    def _update_background(self, event=None):
        if self.fig and self.ax:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
