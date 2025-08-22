import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.ticker as ticker
import numpy as np

@dataclass
class ERDPlot:
    def __init__(self):
        self.ax: plt.Axes = field(init=False, default=None)
        self.extent = None # set later
        self.im = None # set later
        self.fig, self.ax = plt.subplots()

        anchor_values = np.array([1, 2, 4, 8, 16, 32])
        anchor_colors = ["#000000", "#ff5500", "#ffff00", "#00ff00", "#00ffff", "#0000ff"]
        norm_anchor_vals = (np.log2(anchor_values) - np.log2(anchor_values[0])) / \
                            (np.log2(anchor_values[-1]) - np.log2(anchor_values[0]))
        self.cmap = LinearSegmentedColormap.from_list("custom_cmap", list(zip(norm_anchor_vals, anchor_colors)))
        self.norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=32, base=2)

        self.cbar = None
    
    def create_plot(self):
        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        return self.fig

    def set_data(self, pixels, extended_data) -> None:
        """Sets the main data for the plot, preserving the polygon artists."""
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
                aspect="auto",
                extent=self.extent
            )
            if self.cbar is None:
                self.cbar = self.fig.colorbar(sm, ax=self.ax)
                self.cbar.set_label('Counts')
        else:
            # Just update bitmap — no re-colormapping
            self.im.set_data(rgba_img)

        # Force colorbar to show integer ticks instead of powers-of-two
        self.cbar.ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        self.cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))

        ticks = [1, 2, 4, 8, 16, 32]
        self.cbar.set_ticks(ticks)
        self.cbar.ax.set_yticklabels([str(t) for t in ticks])

        # Add lines at H, O, Si, Ti positions
        x_coords = [100, 120, 140, 160]
        labels   = ["H", "O", "Si", "Ti"] # TODO: zet ergens in een config

        self.set_vertical_lines(x_coords, labels)
    
    def set_vertical_lines(
        self,
        x_coords: list[float],
        labels: list[str] = None,
        y_max: float = 1500,
        color="red",
        linestyle="-",
        linewidth=1,
    ):
        """Draw vertical lines up to y_max with optional labels above them."""

        # Remove old lines and labels if they exist
        if hasattr(self, "_vertical_artists"):
            for line in self._vertical_artists:
                line.remove()
        if hasattr(self, "_vertical_labels"):
            for txt in self._vertical_labels:
                txt.remove()

        # Draw new lines
        self._vertical_artists = [
            self.ax.vlines(x, ymin=0, ymax=y_max, color=color,
                           linestyle=linestyle, linewidth=linewidth, zorder=4)
            for x in x_coords
        ]

        # Draw new labels if provided
        self._vertical_labels = []
        if labels is not None:
            for x, lbl in zip(x_coords, labels):
                txt = self.ax.text(
                    x,
                    5500,
                    lbl,
                    color=color,
                    ha="center",
                    va="bottom",
                    fontsize=10,
                    zorder=5
                )
                self._vertical_labels.append(txt)

        self.fig.canvas.draw()
    
    def set_title(self, title: str):
        self.ax.set_title(title)
    
    def _update_background(self, event=None):
        if self.fig and self.ax:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
    
    def save(self, filename: str):
        self.create_plot()
        self.fig.savefig(filename)

    def clear(self):
        """Clear all data contents of the plot."""
        self.set_data(np.zeros((2, 2)), [], "Error")
    
    def show(self):
        self.fig.show()