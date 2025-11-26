from tkinter import *
from tkinter import ttk


class TkinterMaster:
    def __init__(self, title, geometry):
        self.root = Tk()
        self.root.title(title)
        self.root.geometry(geometry)
        self.style = ttk.Style(self.root)

    def run(self):
        self.root.mainloop()

    def notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew")

    def configure_style(self, style_name, options):
        self.style.configure(style_name, **options)

    def make_config(self, config):
        config_to_response = {}
        for k, v in config.items():
            config_to_response[k] = v
        return config_to_response

    def grid_options(seld, widget, show, grid, is_special_grid_widget):
        if is_special_grid_widget:
            widget = GridWidget(widget, grid)
        if show:
            widget.show() if is_special_grid_widget else widget.grid(**grid)
        return widget

    def add_label(
        self, parent, text, grid, label=None, show=True, special_grid_widget=False
    ):
        label_config = self.make_config(label) if label else {}
        label = ttk.Label(parent, text=text, **label_config)
        return self.grid_options(label, show, grid, special_grid_widget)

    def add_button(
        self,
        parent,
        text,
        command=None,
        grid=None,
        button=None,
        show=True,
        special_grid_widget=False,
    ):
        button_config = self.make_config(button) if button else {}
        button = ttk.Button(parent, text=text, command=command, **button_config)
        return self.grid_options(button, show, grid, special_grid_widget)

    def add_entry(self, parent, grid, entry=None, show=True, special_grid_widget=False):
        entry_config = self.make_config(entry) if entry else {}
        entry = ttk.Entry(parent, **entry_config)
        return self.grid_options(entry, show, grid, special_grid_widget)

    def add_text(
        self,
        parent,
        width,
        height,
        grid=None,
        text=None,
        show=True,
        special_grid_widget=False,
    ):
        text_config = self.make_config(text) if text else {}
        text = Text(parent, width=width, height=height, **text_config)
        return self.grid_options(text, show, grid, special_grid_widget)

    def add_listbox(
        self,
        parent,
        items,
        grid=None,
        listbox=None,
        show=True,
        special_grid_widget=False,
    ):
        listbox_config = self.make_config(listbox) if listbox else {}
        listbox = Listbox(parent, selectmode=SINGLE, **listbox_config)
        for item in items:
            listbox.insert(END, item)
        return self.grid_options(listbox, show, grid, special_grid_widget)

    def add_frame(
        self,
        parent,
        grid=None,
        frame=None,
        show=True,
        special_grid_widget=False,
        for_notebook=False,
    ):
        frame_config = self.make_config(frame) if frame else {}
        frame = ttk.Frame(parent, **frame_config)
        return (
            frame
            if for_notebook
            else self.grid_options(frame, show, grid, special_grid_widget)
        )

    def add_combobox(
        self,
        parent,
        values,
        grid=None,
        combobox=None,
        show=True,
        special_grid_widget=False,
    ):
        combobox_config = self.make_config(combobox) if combobox else {}
        combobox = ttk.Combobox(parent, values=values, **combobox_config)
        return self.grid_options(combobox, show, grid, special_grid_widget)

    def add_radiobutton(
        self,
        parent,
        text,
        variable,
        value,
        grid=None,
        radiobutton=None,
        show=True,
        special_grid_widget=False,
    ):
        radiobutton_config = self.make_config(radiobutton) if radiobutton else {}
        radiobutton = ttk.Radiobutton(
            parent, text=text, variable=variable, value=value, **radiobutton_config
        )
        return self.grid_options(radiobutton, show, grid, special_grid_widget)

    def add_checkbox(
        self,
        parent,
        text,
        variable,
        grid=None,
        checkbox=None,
        show=True,
        special_grid_widget=False,
    ):
        checkbox_config = self.make_config(checkbox) if checkbox else {}
        checkbox = ttk.Checkbutton(
            parent, text=text, variable=variable, **checkbox_config
        )
        return self.grid_options(checkbox, show, grid, special_grid_widget)


class GridWidget:
    def __init__(self, widget, grid):
        self.w = widget
        self.column = grid["column"]
        self.row = grid["row"]
        grid.pop("column", None)
        grid.pop("row", None)
        self.extra_properties = grid

    def show(self):
        self.w.grid(column=self.column, row=self.row, **self.extra_properties)

    def hide(self):
        self.w.grid_forget()
