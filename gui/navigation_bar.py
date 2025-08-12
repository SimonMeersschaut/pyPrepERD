from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.backend_bases import NavigationToolbar2
from enum import Enum
import tkinter as tk
import tkinter.font
from matplotlib import cbook
from matplotlib.backends._backend_tk import add_tooltip

class _MoreModes(str, Enum):
    """Extension of `_Mode` under `matplotlib.backend_bases`."""
    NONE = ""
    PAN = "pan/zoom"
    ZOOM = "zoom rect"
    POLYGON = "draw polygon"

    # TOGGLEABLES =

    def __str__(self):
        return self.value

    @property
    def _navigate_mode(self):
        return self.name if self is not _MoreModes.NONE else None

ORIGINAL = 0
CUSTOM = 1


class CustomToolBar(NavigationToolbar2Tk):
    def __init__(self, canvas, window=None, *, pack_toolbar=True):

        """
        Parameters
        ----------
        canvas : `FigureCanvas`
            The figure canvas on which to operate.
        window : tk.Window
            The tk.Window which owns this toolbar.
        pack_toolbar : bool, default: True
            If True, add the toolbar to the parent's pack manager's packing
            list during initialization with ``side="bottom"`` and ``fill="x"``.
            If you want to use the toolbar with a different layout manager, use
            ``pack_toolbar=False``.
        """

        # original_or_custom, text, tooltip_text, image_file, callback
        toolitems = (
            (ORIGINAL, 'Home', 'Reset original view', 'home', 'home'),
            (ORIGINAL, 'Back', 'Back to previous view', 'back', 'back'),
            (ORIGINAL, 'Forward', 'Forward to next view', 'forward', 'forward'),
            # (ORIGINAL, None, None, None, None),
            (ORIGINAL, 'Pan',
            'Left button pans, Right button zooms\n'
            'x/y fixes axis, CTRL fixes aspect',
            'move', 'pan'),
            (ORIGINAL, 'Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
            # (ORIGINAL, 'Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            (ORIGINAL, None, None, None, None),
            (ORIGINAL, 'Save', 'Save the figure', 'filesave', 'save_figure'),
            (ORIGINAL, None, None, None, None),
            (CUSTOM, 'Polygon', 'Draw a polygon', 'polygon', 'draw_polygon'),
        )

        if window is None:
            window = canvas.get_tk_widget().master
        tk.Frame.__init__(self, master=window, borderwidth=2,
                          width=int(canvas.figure.bbox.width), height=50)

        self._buttons = {}
        for original_or_custom, text, tooltip_text, image_file, callback in toolitems:
            # get image path
            if original_or_custom == ORIGINAL:
                im_path = str(cbook._get_data_path(f"images/{image_file}.png"))
            else:
                im_path = f"C:\\Users\\meerss01\\Desktop\\pyPrepERD\\data\\{image_file}.png"

            if text is None:
                # Add a spacer; return value is unused.
                self._Spacer()
            else:
                self._buttons[text] = button = self._Button(
                    text,
                    im_path,
                    toggle=callback in ["zoom", "pan", "draw_polygon"],
                    command=getattr(self, callback),
                )
                if tooltip_text is not None:
                    add_tooltip(button, tooltip_text)

        self._label_font = tkinter.font.Font(root=window, size=10)

        # This filler item ensures the toolbar is always at least two text
        # lines high. Otherwise the canvas gets redrawn as the mouse hovers
        # over images because those use two-line messages which resize the
        # toolbar.
        label = tk.Label(master=self, font=self._label_font,
                         text='\N{NO-BREAK SPACE}\n\N{NO-BREAK SPACE}')
        label.pack(side=tk.RIGHT)

        self.message = tk.StringVar(master=self)
        self._message_label = tk.Label(master=self, font=self._label_font,
                                       textvariable=self.message,
                                       justify=tk.RIGHT)
        self._message_label.pack(side=tk.RIGHT)

        NavigationToolbar2.__init__(self, canvas)
        if pack_toolbar:
            self.pack(side=tk.BOTTOM, fill=tk.X)
    

    def draw_polygon(self, *args):
        if self.mode == _MoreModes.POLYGON:
            self.mode = _MoreModes.NONE
        else:
            self.mode = _MoreModes.POLYGON
        self._update_buttons_checked()
    
    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for text, mode in [('Zoom', _MoreModes.ZOOM), ('Pan', _MoreModes.PAN), (_MoreModes.POLYGON, "Polygon")]:
            if text in self._buttons:
                if self.mode == mode:
                    self._buttons[text].select()
                else:
                    self._buttons[text].deselect()