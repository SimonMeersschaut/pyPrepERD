import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.ticker as ticker
import numpy as np
from utils.polygon import points_in_polygon

@dataclass
class Plot:
    def __init__(self):
        self.ax: plt.Axes = field(init=False, default=None)

        self.fig, self.ax = plt.subplots()

        anchor_values = np.array([1, 2, 4, 8, 16, 32])
        anchor_colors = ["#000000", "#ff5500", "#ffff00", "#00ff00", "#00ffff", "#0000ff"]
        norm_anchor_vals = (np.log2(anchor_values) - np.log2(anchor_values[0])) / \
                            (np.log2(anchor_values[-1]) - np.log2(anchor_values[0]))
        self.cmap = LinearSegmentedColormap.from_list("custom_cmap", list(zip(norm_anchor_vals, anchor_colors)))
        self.norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=32, base=2)

        self.polygon_points: list[tuple[float, float]] = []
        self.scatter = None
        self.polygon_line = None
        self.closing_line = None
        self.background = None  # for blitting
        self.cbar = None
        self. im = None

    def create_plot(self):
        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        # Create artists **once** and attach to Axes. zorder ensures they draw on top.
        self.scatter = self.ax.scatter([], [], color='red', marker='o', zorder=5, s=10) # s: markersize
        self.polygon_line, = self.ax.plot([], [], color='red', zorder=5, linewidth=1)
        self.closing_line, = self.ax.plot([], [], color='red', linestyle='--', zorder=5, linewidth=1)

        self.fig.tight_layout()
        self.fig.canvas.draw()  # Force layout & renderer
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # Update background on full draw
        self.fig.canvas.mpl_connect("draw_event", self._update_background)

        return self.fig

    def set_data(self, pixels, extended_data, title: str) -> None:
        """Sets the main data for the plot, preserving the polygon artists."""
        self.clear_polygon_points()

        self.extended_data = extended_data

        # Mask invalid pixels
        masked_pixels = np.where(pixels >= 1, pixels, np.nan)

        # Create ScalarMappable to convert data -> RGBA
        sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        rgba_img = (sm.to_rgba(masked_pixels, bytes=True))  # uint8 RGBA array

        if self.im is None:
            # Feed pre-rendered RGBA directly to imshow
            self.im = self.ax.imshow(
                rgba_img,
                origin="lower",
                # interpolation="nearest",
                # extent=[0, 300, 0, 8000],
                aspect="auto"
            )
            if self.cbar is None:
                self.cbar = self.fig.colorbar(sm, ax=self.ax)
                self.cbar.set_label('Counts')
        else:
            # Just update bitmap — no re-colormapping
            self.im.set_data(rgba_img)

        self.ax.set_title(title)

        # Force colorbar to show integer ticks instead of powers-of-two
        self.cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        ticks = [1, 2, 4, 8, 16, 32]
        self.cbar.set_ticks(ticks)
        self.cbar.ax.set_yticklabels([str(t) for t in ticks])

        
        self.fig.canvas.draw()
        # self.fig.canvas.draw_idle()

    def add_polygon_point(self, point: tuple[float, float]):
        if self.fig is None:
            self.create_plot()
        self.polygon_points.append(point)
        self._update_polygon()
    
    def _update_background(self, event=None):
        if self.fig and self.ax:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
    
    def clear_polygon_points(self):
        if len(self.polygon_points) == 0:
            return
        
        self.polygon_points = []
        self._update_polygon()
        self.fig.canvas.draw() # Force a full redraw so everything updates
    
    def _update_polygon(self):
        """Update the polygon overlay using blitting for efficiency."""
        if self.background is None:
            return

        self.fig.canvas.restore_region(self.background)

        if not self.polygon_points:
            # Clear all polygon artists
            self.scatter.set_offsets(np.empty((0, 2)))
            self.polygon_line.set_data([], [])
            self.closing_line.set_data([], [])
        else:
            x, y = zip(*self.polygon_points)
            
            # Update artists with new data
            self.scatter.set_offsets(self.polygon_points)
            self.polygon_line.set_data(x, y)
            
            if len(self.polygon_points) > 1:
                self.closing_line.set_data([x[-1], x[0]], [y[-1], y[0]])
            else:
                self.closing_line.set_data([], [])
        
        # Redraw only the changed artists
        self.ax.draw_artist(self.scatter)
        self.ax.draw_artist(self.polygon_line)
        self.ax.draw_artist(self.closing_line)

        # Blit the updated axes to the canvas
        self.fig.canvas.blit(self.ax.bbox)
        self.fig.canvas.flush_events()


    def get_selected_points(self):
        if len(self.polygon_points) < 3:
            return []
        
        # Add a column with the line number to extended data
        # Create column with row indices (line numbers)
        line_numbers = np.arange(len(self.extended_data)).reshape(-1, 1)

        # Add it as the last column
        result = np.hstack((self.extended_data, line_numbers))
        
        # Select points based on polygon
        selected = points_in_polygon(result, self.polygon_points, x_index=1, y_index=2)
        
        # return only columns 1, 2 and 5
        return selected[:, [1, 2, 5]]
    
    def save(self, filename: str):
        self.create_plot()
        self.fig.savefig(filename)

    def clear(self):
        """Clear all data contents of the plot."""
        self.set_data(np.zeros((2, 2)), [], "Error")