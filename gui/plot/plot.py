import matplotlib.pyplot as plt
from dataclasses import dataclass, field
import matplotlib.colors as colors
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
import matplotlib.ticker as ticker
import numpy as np
from utils.polygon import points_in_polygon

@dataclass
class Plot:
    # pixels: any
    # display_title: str
    # extended_data: list[float, float]

    fig: plt.Figure = field(init=False, default=None)
    ax: plt.Axes = field(init=False, default=None)

    polygon_points: list[tuple[float, float]] = field(default_factory=list, init=False)
    scatter = None
    polygon_line = None
    closing_line = None
    background = None  # for blitting

    def create_plot(self):
        self.cbar = None
        self.fig, self.ax = plt.subplots()

        # Example colormap stuff
        anchor_values = np.array([1, 2, 4, 8, 16, 32])
        anchor_colors = ["#000000", "#ff5500", "#ffff00", "#00ff00", "#00ffff", "#0000ff"]
        norm_anchor_vals = (np.log2(anchor_values) - np.log2(anchor_values[0])) / \
                            (np.log2(anchor_values[-1]) - np.log2(anchor_values[0]))
        self.cmap = LinearSegmentedColormap.from_list("custom_cmap", list(zip(norm_anchor_vals, anchor_colors)))
        self.norm = colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=1, vmax=32, base=2)

        self.ax.set_xlabel('Time of flight (ns)')
        self.ax.set_ylabel('Energy channel')

        # Create artists **once** and attach to Axes
        self.scatter = self.ax.scatter([], [], color='red', marker='o')
        self.polygon_line, = self.ax.plot([], [], color='red')
        self.closing_line, = self.ax.plot([], [], color='orange', linestyle='--')

        self.fig.tight_layout()
        self.fig.canvas.draw()  # Force layout & renderer
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

        # Update background on full draw
        self.fig.canvas.mpl_connect("draw_event", self._update_background)

        return self.fig

    def set_data(self, pixels, extended_data, title: str) -> None:
        """TODO: docs"""
        self.extended_data = extended_data

        # Remove old meshes before adding new ones
        for coll in list(self.ax.collections):
            coll.remove()

        white_pixels = np.where(pixels == 0, 1, np.nan)
        self.ax.pcolormesh(white_pixels, cmap=ListedColormap(["white"]), vmin=0, vmax=1)

        masked_pixels = np.where(pixels >= 1, pixels, np.nan)
        im = self.ax.pcolormesh(masked_pixels, cmap=self.cmap, norm=self.norm)

        if self.cbar is None:
            self.cbar = self.fig.colorbar(im, ax=self.ax)
            self.cbar.set_label('Counts')
            self.cbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
        else:
            # Update the colorbar with the new image
            self.cbar.update_normal(im)

        self.ax.set_title(title)

        # Force a full redraw so everything updates
        self.fig.canvas.draw()

    def add_polygon_point(self, point: tuple[float, float]):
        if self.fig is None:
            self.create_plot()
        self.polygon_points.append(point)
        self._update_polygon()
    
    def _update_polygon(self):
        if not all([self.fig, self.ax, self.scatter, self.polygon_line, self.closing_line]):
            return

        # Ensure the renderer exists
        if self.fig.canvas.get_renderer() is None:
            self.fig.canvas.draw()

        # Restore background only if we have one
        if self.background is not None:
            self.fig.canvas.restore_region(self.background)

        # Update scatter points
        if not self.polygon_points:
            self.scatter.set_offsets(np.empty((0, 2)))
            self.polygon_line.set_data([], [])
            self.closing_line.set_data([], [])
        else:
            self.scatter.set_offsets(self.polygon_points)
            if len(self.polygon_points) > 1:
                xs, ys = zip(*self.polygon_points)
                self.polygon_line.set_data(xs, ys)
                self.closing_line.set_data(
                    [self.polygon_points[-1][0], self.polygon_points[0][0]],
                    [self.polygon_points[-1][1], self.polygon_points[0][1]]
                )
            else:
                self.polygon_line.set_data([], [])
                self.closing_line.set_data([], [])

        # Draw updated artists
        if self.scatter.figure:
            self.ax.draw_artist(self.scatter)
        if self.polygon_line.figure:
            self.ax.draw_artist(self.polygon_line)
        if self.closing_line.figure:
            self.ax.draw_artist(self.closing_line)

        # Blit updated region
        self.fig.canvas.blit(self.ax.bbox)
        self.fig.canvas.flush_events()

        # IMPORTANT: recapture the background so next draw keeps points
        self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)



    def _update_background(self, event=None):
        if self.fig and self.ax:
            self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)
    
    def clear_polygon_points(self):
        if len(self.polygon_points) == 0:
            # nothing to update
            return
        
        self.polygon_points = []
        self._update_polygon()

    def get_selected_points(self):
        if len(self.polygon_points) < 3:
            return []
        
        return points_in_polygon(self.extended_data, self.polygon_points)
    
    def save(self, filename: str):
        """For automatically saving the plot."""
        if self.fig is None:
            self.create_plot()
        self.fig.savefig(filename)

    def clear(self):
        """Clear all contents of the plot."""
        self.set_data(np.zeros((2, 2)), [], "Error")