#!/usr/bin/python

import urwid

DEFAULT_PALETTE = [('menu', 'black', 'light gray', 'standout'),
                   ('menuh', 'yellow', 'light gray', ('standout', 'bold')),
                   ('menuf', 'light gray', 'dark blue'),
                   ('bgf', 'light gray', 'dark blue'),
                   ('bg', 'black', 'light gray', 'standout'),
                   ('alert', 'light gray', 'dark red', ('standout', 'bold')),
                   ('code', 'black', 'light gray'),
                   ('lineno', 'light blue', 'light gray'),
                   ]


class SimpleDialog(urwid.WidgetWrap):
    """Simple popup dialog with text and buttons

    :param message: The text message in the dialog
    :type message: str

    :param buttons: Buttons to show, each button have an id and a label.
    :type message: list of (name, label) tuples

    """
    signals = ['close']
    pressed = None

    def __init__(self, text, buttons):
        button_widgets = []
        for id, label in buttons:
            button = urwid.Button(label)
            button.id = id
            urwid.connect_signal(button, 'click',
                self.buttonpress)
            button_widgets.append(button)

        buttons = urwid.Columns(button_widgets)
        pile = urwid.Pile([urwid.Text( text), buttons])
        fill = urwid.Filler(pile)
        self.__super.__init__(urwid.AttrWrap(fill, 'popbg'))

    def keypress(self, size, key):
        if key == 'esc':
            self.pressed = None
            self._emit("close")
            return
        return self._w.keypress(size, key)

    def buttonpress(self, button):
        self.pressed = button.id
        self._emit("close")


class MenuItem(urwid.Text):
    """A MenuItem"""

    _selectable = True

    def keypress(self, size, key):
        """Don't handle any keys."""
        return key


class PopupMenu(urwid.WidgetWrap):
    """Creates a popup menu on top of another BoxWidget.

    :param menu_list: The menu entries
    :type menu_list: A list of strings

    :param attr: Display attributes (background, active_item)
    :type attr: tuple

    :param pos: The position of the menu widget
    :type pos: (x, y) tuple

    :param body: The widget displayed beneath the message widget
    :type body: widget

    Attributes:

    :param selected: The item the user has selected by pressing <RETURN>,
                     or None if nothing has been selected.
    """

    selected = None

    def __init__(self, menu_list, attr, pos, body):

        content = [urwid.AttrWrap(MenuItem(" " + w), None, attr[1])
                   for w in menu_list]

        # Calculate width and height of the menu widget:
        height = len(menu_list)
        width = 0
        for entry in menu_list:
            if len(entry) > width:
                width = len(entry)

        # Create the ListBox widget and put it on top of body:
        self._listbox = urwid.AttrWrap(urwid.ListBox(content), attr[0])
        overlay = urwid.Overlay(self._listbox, body, ('fixed left', pos[0]),
                                width + 2, ('fixed top', pos[1]), height)

        urwid.WidgetWrap.__init__(self, overlay)

    def keypress(self, size, key):

        if key == "enter":
            (widget, foo) = self._listbox.get_focus()
            (text, foo) = widget.get_text()
            self.selected = text[1:] # Get rid of the leading space...
        else:
            return self._listbox.keypress(size, key)

    def render(self, size, focus):
        return urwid.WidgetWrap.render(self, size, focus)


class Menu(urwid.PopUpLauncher):
    def __init__(self, label, menu_items):
        self.__super.__init__(urwid.Button(label))
        self.menu_items = menu_items
        self.height = len(menu_items)
        self.width = max(len(x) + 2 for x in menu_items)
        urwid.connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        return PopupMenu(self.menu_items, ('menu', 'menuf'), (0, 1), self)

    def get_pop_up_parameters(self):
        return {'left': 0, 'top': 1, 'overlay_width': self.width, 'overlay_height': self.height}


class MenuBar(urwid.Columns):

    def __init__(self, menu_def):
        menus = [Menu(label, items) for label, items in menu_def]
        super(MenuBar, self).__init__(menus, dividechars=1)


class MainFrame(urwid.Frame):
    def __init__(self):
        body = urwid.Filler(urwid.Padding(ThingWithAPopUp(), 'center', 15))

        menu_text = [('menuh', " P"), ('menu', "rogram   "),
                     ]

        program_menu = ["Save", "Save As", "Quit"]
        header = urwid.AttrWrap(MenuBar([(menu_text, program_menu)]), 'menu')

        footer = urwid.AttrWrap(urwid.Text(self.help_text()), 'menu')

        self.__super.__init__(body, header=header, footer=footer,
                              focus_part='body')

    def help_text(self):
        return "Press Alt-H for help"

    def keypress(self, size, key):
        if key == 'meta p':
            return self.header.open_pop_up()

        return super(MainFrame, self).keypress(size, key)



class ThingWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        self.__super.__init__(urwid.Button("click-me"))
        urwid.connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = SimpleDialog('Text', [('yes', 'Yes'), ('no', 'No')])
        urwid.connect_signal(pop_up, 'close',
            lambda button: self.close_pop_up())
        return pop_up

    def get_pop_up_parameters(self):
        return {'left':0, 'top':1, 'overlay_width':32, 'overlay_height':7}


# Custom main loop that stops screen on exceptions.
class MainLoop(urwid.MainLoop):
    def run(self):
        try:
            self._run()
        except urwid.ExitMainLoop:
            pass
        except BaseException:
            self.screen.stop()
            raise


def main():
        ui = urwid.raw_display.Screen()
        #ui.tty_signal_keys(intr='undefined',
                           #quit='undefined',
                           #start='undefined',
                           #stop='undefined',
                           #susp='undefined')
        fill = MainFrame()
        loop = MainLoop(
            fill,
            DEFAULT_PALETTE,
            pop_ups=True)
        loop.run()



if __name__ == '__main__':
    main()