from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from matplotlib.backend_bases import NavigationToolbar2
from enum import Enum
import tkinter as tk
from tkinter import ttk
import tkinter.font
import numpy as np
from matplotlib import cbook
from matplotlib.backends._backend_tk import add_tooltip
import analysis
import os
from dataclasses import dataclass
from abc import ABC
import json

with open("data/atomic_weights_table.json", 'r') as f:
    ATOMS = [atom[0] for atom in json.load(f)[1:]] # remove first line

class ToolItem(ABC):
    ...


class ToolSpacer(ToolItem):
    ...

@dataclass
class ToolButton(ToolItem):
    matplotlib_original: bool
    text: str
    tooltip_text: str
    image_file: str
    callback: str

@dataclass
class ToolDropdown(ToolItem):
    matplotlib_original: bool
    text: str
    tooltip_text: str
    # image_file: str
    callback: str


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
    def __init__(self, canvas, plot, window=None, *, pack_toolbar=True):

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
        self.current_project_dir = None
        self.plot = plot
        self.canvas = canvas
        self.selected_atom = None

        # original_or_custom, text, tooltip_text, image_file, callback
        toolitems = (
            ToolButton(ORIGINAL, 'Home', 'Reset original view', 'home', 'home'),
            ToolButton(ORIGINAL, 'Back', 'Back to previous view', 'back', 'back'),
            ToolButton(ORIGINAL, 'Forward', 'Forward to next view', 'forward', 'forward'),
            # ToolSpacer(),
            ToolButton(ORIGINAL, 'Pan',
            'Left button pans, Right button zooms\n'
            'x/y fixes axis, CTRL fixes aspect',
            'move', 'pan'),
            ToolButton(ORIGINAL, 'Zoom', 'Zoom to rectangle\nx/y fixes axis', 'zoom_to_rect', 'zoom'),
            # (ORIGINAL, 'Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
            ToolSpacer(),
            ToolButton(ORIGINAL, 'Save', 'Save the figure', 'filesave', 'save_figure'),
            ToolSpacer(),
            ToolButton(CUSTOM, 'Polygon', 'Draw a polygon', 'polygon', 'draw_polygon'),
            ToolButton(CUSTOM, 'Clear', 'Clear the current polygon', 'clear_polygon', 'clear_polygon'),
            ToolDropdown(CUSTOM, 'Export', 'Export the selected polygon', 'update_element_dropdown'),
            ToolButton(CUSTOM, 'Export', 'Export the selected polygon', 'export', 'export_polygon'),
        )

        if window is None:
            window = canvas.get_tk_widget().master
        tk.Frame.__init__(self, master=window, borderwidth=2,
                          width=int(canvas.figure.bbox.width), height=50)

        self._buttons = {}
        for toolitem in toolitems:
            if isinstance(toolitem, ToolSpacer):
                # Add a spacer; return value is unused.
                self._Spacer()
            elif isinstance(toolitem, ToolButton):
                # get image path
                if toolitem.matplotlib_original == ORIGINAL:
                    im_path = str(cbook._get_data_path(f"images/{toolitem.image_file}.png"))
                else:
                    im_path = f"C:\\Users\\meerss01\\Desktop\\pyPrepERD\\data\\{toolitem.image_file}.png"

                self._buttons[toolitem.text] = button = self._Button(
                    toolitem.text,
                    im_path,
                    toggle=toolitem.callback in ["zoom", "pan", "draw_polygon"],
                    command=getattr(self, toolitem.callback),
                )
                if toolitem.tooltip_text is not None:
                    add_tooltip(button, toolitem.tooltip_text)
            elif isinstance(toolitem, ToolDropdown):
                self._buttons[toolitem.text] = button = self._Dropdown(
                    toolitem.text,
                    options=ATOMS,
                    default_value=ATOMS[0],
                    command=getattr(self, toolitem.callback),
                )

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

        # NavigationToolbar2Tk._set_image_for_button(self, b)

        NavigationToolbar2.__init__(self, canvas)
        if pack_toolbar:
            self.pack(side=tk.BOTTOM, fill=tk.X)
        

    def _Dropdown(self, text, options: list, default_value, command):
        opt = tk.StringVar(value=default_value)
        self.selected_atom = default_value
        
        b = ttk.Combobox(
            self,
            textvariable=opt,
            values=options,
            state="readonly",  # only allow selection, no typing
            width=5           # adjust number of characters visible
        )
        b.bind("<<ComboboxSelected>>", lambda e: command(opt.get()))
        b.pack(side=tk.LEFT)
        
        return b
    

    def draw_polygon(self, *args):
        """
        Called by tkinter ui, when the user clicks the export button.
        """
        if self.mode == _MoreModes.POLYGON:
            self.mode = _MoreModes.NONE
            # remove polygon points
        else:
            self.mode = _MoreModes.POLYGON
            self.set_message("Click to draw a polygon")
        self._update_buttons_checked()
    
    def clear_polygon(self):
        self.plot.clear_polygon_points()
    
    def export_polygon(self):
        """
        Called by tkinter ui, when the user clicks the export button.
        Implementation is analog to matplotlib.backends.backend_tkagg.NavigationToolbar2Tk.save_figure
        """
        if self.current_project_dir is None:
            raise ValueError()
        if not os.path.exists(self.current_project_dir):
            raise FileNotFoundError(f"Project folder {self.current_project_dir} was not found.")
        
        try:
            os.mkdir(self.current_project_dir+"/cuts")
        except FileExistsError:
            pass
        
        # select T_k and E_k from the extended data
        selected_extended_data = self.plot.get_selected_points()

        if len(selected_extended_data) == 0:
            raise ValueError() # TODO: show popup
        # TODO: dump dit in de juiste file, met juiste extentie
        # add a linenumber 
        # output = selected_extended_data + np.linspace(1, len(selected_extended_data))
        analysis.dump_dataframe(selected_extended_data, self.current_project_dir+f"/cuts/{self.selected_atom}.cut")

        # dump polygon points
        with open(self.current_project_dir+f"/cuts/{self.selected_atom}.polygon.json", 'w') as f:
            json.dump(self.plot.polygon_points, f)
    
    def _update_buttons_checked(self):
        # sync button checkstates to match active mode
        for text, mode in [('Zoom', _MoreModes.ZOOM), ('Pan', _MoreModes.PAN), ("Polygon", _MoreModes.POLYGON)]:
            if text in self._buttons:
                if self.mode == mode:
                    self._buttons[text].select()
                else:
                    self._buttons[text].deselect()
    
    def mouse_move(self, event):
        self._update_cursor(event)
        if self.mode == _MoreModes.POLYGON:
            # Show message of selected points
            ...
        else:
            # Defualt behaviour: show mouse coordinates
            self.set_message(self._mouse_event_to_message(event))
    
    def show_selected_points(self, points:int):
        self.set_message(f"{points:,}".replace(",", ".") + " points selected")
    
    def update_element_dropdown(self, value:str):
        self.selected_atom = value