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

    :param buttons: A list of buttons, each button being a tuple of name,
                    label and function to call when pressed
    :type message: list of (name, label, function) tuples

    """
    signals = ['close']
    selected = None

    def __init__(self, text, buttons):
        button_widgets = []
        self._actions = {}
        self.minwidth = -1  # We don't need a space before the first button
        for name, label, function in buttons:
            self.minwidth += len(label) + 5  # Button is 4 wider + 1 space
            button = urwid.Button(label)
            button.name = name
            self._actions[name] = function
            urwid.connect_signal(button, 'click', self.select)
            button_widgets.append(button)

        # We won't render it wider than necessary
        self.maxwidth = max(self.minwidth, len(text))

        buttons = urwid.Columns(button_widgets, dividechars=1)
        label = urwid.Text(text)

        pile = urwid.Pile([label, buttons])
        self.__super.__init__(urwid.AttrWrap(pile, 'popbg'))

    def keypress(self, size, key):
        if key == 'esc':
            self.selected = None
            self._emit("close")
            return
        return self._w.keypress(size, key)

    def select(self, button):
        self.selected = button.name
        action = self._actions[button.name]
        if action is not None:
            action()
        self._emit("close")

    def render(self, size, focus=False):
        cols, rows = size
        if cols < self.minwidth:
            raise AssertionError("This dialog can not be rendered with a "
                                 "width below %n" % self.minwidth)

        # We render it wider, if asked to
        width = max(cols, self.minwidth)
        # But not wider than the maxwidth
        width = min(width, self.maxwidth)

        canv = self._w.render((width,), focus)

        # And now we pad out the canvas to the desired size
        canv = urwid.CompositeCanvas(canv)
        pad = cols - canv.cols()
        left = pad // 2
        right = pad - left
        canv.pad_trim_left_right(left, right)
        pad = rows - canv.rows()
        top = pad // 2
        bottom = pad - top
        canv.pad_trim_top_bottom(top, bottom)

        return canv


class MenuItem(urwid.Text):
    """A MenuItem, used by the Menu class"""

    signals = ['click']
    _selectable = True

    def __init__(self, name, markup):
        self.name = name
        super(MenuItem, self).__init__(markup, align=urwid.LEFT, wrap=urwid.ANY)

    def keypress(self, size, key):
        """Don't handle any keys."""
        return key


class Menu(urwid.WidgetWrap):
    """Creates a popup menu on top of another BoxWidget.

    :param menu_def: The menu entries
    :type menu_def: A list of (name, label, function) tuples

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

    signals = ['close']
    selected = None

    def __init__(self, menu_def):

        self._actions = {}
        items = []
        for name, label, function in menu_def:
            item = MenuItem(name, label)
            self._actions[name] = function
            urwid.connect_signal(item, 'click', self.select)
            items.append(urwid.AttrWrap(item, None, 'menuf'))

        # Calculate width and height of the menu widget:
        height = len(menu_def)
        width = 0
        for entry in menu_def:
            if len(entry) > width:
                width = len(entry)

        # Create the ListBox widget:
        self._listbox = urwid.AttrWrap(urwid.ListBox(items), 'menu')
        urwid.WidgetWrap.__init__(self, self._listbox)


    def keypress(self, size, key):
        if key == "enter":
            (widget, foo) = self._listbox.get_focus()
            self.selected = widget.name
            action = self._actions[widget.name]
            if action is not None:
                action()
            self._emit("close")
        elif key == 'esc':
            self.selected = None
            self._emit("close")
        else:
            return self._listbox.keypress(size, key)

    def select(self, item):
        self.selected = item.name
        action = self._actions[item.name]
        if action is not None:
            action()
        self._emit("close")


class MenuBar(urwid.WidgetWrap):
    """The top bar in a WIMP program

    :param menubar_def: The menu entries
    :type menu: A list of (name, label, menu_def) tuples

    """

    def __init__(self, menubar_def):
        self.menus = {}
        menus = []
        labels = []
        for name, label, menu_def in menubar_def:
            menu = Menu(menu_def)
            menus.append(menu)
            self.menus[name] = menu
            labels.append(urwid.AttrWrap(urwid.Text(label), 'menu'))

        menubar = urwid.Columns(labels, dividechars=1)
        super(MenuBar, self).__init__(menubar)


class MainFrame(urwid.Frame):

    _pop_up_widget = None

    def __init__(self):
        body = urwid.Filler(urwid.Padding(urwid.Text(
            'Ctrl-P for popup, Alt-M for menu'), 'center', 15))

        footer = urwid.AttrWrap(urwid.Text(self.help_text()), 'menu')

        menubar_def = [('file',
                        [('menuh', 'F'), ('menu', 'ile')],
                        [('save', "Save", None),
                         ('saveas', "Save As", None),
                         ('quit', "Quit", None)])]
        self.__super.__init__(body, header=MenuBar(menubar_def), footer=footer,
                              focus_part='body')

    def help_text(self):
        return "Press Alt-H for help"

    def pop_up(self, widget):
        self._pop_up_widget = widget
        p = widget.pack((80, 24))
        urwid.connect_signal(widget, 'close',
            lambda button: self.close_pop_up())
        self._invalidate()

    def close_pop_up(self):
        self._pop_up_widget = None
        self._invalidate()

    def keypress(self, size, key):
        if key == 'ctrl p':
            self.pop_up(SimpleDialog('In a dialogbox you can select buttons or press <esc>',
                                     [('ok', 'OK', None),
                                      ('yes', 'Gotcha', None)]))
            return

        if key == 'ctrl r':
            self.pop_up(SimpleDialog('Do you want to quit?',
                                     [('yes', 'Yes', self.action_quit),
                                      ('no', 'No', None)]))
            return

        return super(MainFrame, self).keypress(size, key)

    def render(self, size, focus=False):
        canv = self.__super.render(size, focus)
        if self._pop_up_widget:
            canv = urwid.CompositeCanvas(canv)
            canv.set_pop_up(self._pop_up_widget, 0, 0, size[0], size[1])
        return canv

    def action_quit(self):
        raise urwid.ExitMainLoop()


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
