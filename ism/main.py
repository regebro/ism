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

    def __init__(self, text, buttons, size):
        self.size = size
        button_widgets = []
        self.minwidth = -1  # We don't need a space before the first
        for id, label in buttons:
            self.minwidth += len(label) + 5
            button = urwid.Button(label)
            button.id = id
            urwid.connect_signal(button, 'click',
                self.buttonpress)
            button_widgets.append(button)

        # We won't render it wider than necessary
        self.maxwidth = max(self.minwidth, len(text))

        buttons = urwid.Columns(button_widgets, dividechars=1)
        label = urwid.Text(text)

        pile = urwid.Pile([label, buttons])
        self.__super.__init__(urwid.AttrWrap(pile, 'popbg'))

    def keypress(self, size, key):
        if key == 'esc':
            self.pressed = None
            self._emit("close")
            return
        return self._w.keypress(size, key)

    def buttonpress(self, button):
        self.pressed = button.id
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


class MainFrame(urwid.Frame):

    _pop_up_widget = None

    def __init__(self):
        body = urwid.Filler(urwid.Padding(ThingWithAPopUp(), 'center', 15))

        footer = urwid.AttrWrap(urwid.Text(self.help_text()), 'menu')

        self.__super.__init__(body, header=None, footer=footer,
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
        if key == 'ctrl r':
            self.pop_up(SimpleDialog('Do you want to quit?', [('yes', 'Yes'), ('no', 'No')], (25, 4)))


        return super(MainFrame, self).keypress(size, key)

    def render(self, size, focus=False):
        canv = self.__super.render(size, focus)
        if self._pop_up_widget:
            canv = urwid.CompositeCanvas(canv)
            canv.set_pop_up(self._pop_up_widget, 0, 0, size[0], size[1])
        return canv


class ThingWithAPopUp(urwid.PopUpLauncher):
    def __init__(self):
        self.__super.__init__(urwid.Button("click-me"))
        urwid.connect_signal(self.original_widget, 'click',
            lambda button: self.open_pop_up())

    def create_pop_up(self):
        pop_up = SimpleDialog('Text', [('yes', 'Yes'), ('no', 'No')], (32, 7))
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
