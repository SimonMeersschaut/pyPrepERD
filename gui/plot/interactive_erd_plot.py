from .erd_plot import ERDPlot
import numpy as np
from utils.polygon import points_in_polygon
from utils import Log


class InteractiveERDPlot(ERDPlot):
    def __init__(self):
        super().__init__()
        
        self.polygon_points: list[tuple[float, float]] = []
        self.scatter = None
        self.extended_data = None
        self.polygon_line = None
        self.closing_line = None
        self.background = None  # for blitting
        self.im = None
    
    def create_plot(self):
        super().create_plot()


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
    
    def set_data(self, pixels, extended_data) -> None: # TODO: Remove title
        super().set_data(pixels, extended_data)

        self.clear_polygon_points()

        self.fig.canvas.draw()
    
    def add_polygon_point(self, point: tuple[float, float]):
        if self.fig is None:
            self.create_plot()
        self.polygon_points.append(point)
        self._update_polygon()
    
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
        
        if self.extended_data is None:
            Log.error("Runtime error", "No data was loaded yet")
            return
        
        # Add a column with the line number to extended data
        # Create column with row indices (line numbers)
        line_numbers = np.arange(len(self.extended_data)).reshape(-1, 1)

        # Add it as the last column
        result = np.hstack((self.extended_data, line_numbers))
        
        # Select points based on polygon
        selected = points_in_polygon(result, self.polygon_points, x_index=1, y_index=2)
        
        # return only columns 0, 2 and 5 = (t_k, E_k, line number) respectively
        return selected[:, [0, 2, 5]]
    