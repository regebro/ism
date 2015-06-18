import urwid.curses_display
import urwid
import sys

from doctrine import urwid as urwidwidget
import doctrine.code

SAVE = 'save'
EXIT = 'exit'

DEFAULT_COMMAND_MAP = {
    'backspace': urwidwidget.ERASE_LEFT,
    'delete': urwidwidget.ERASE_RIGHT,
    'ctrl s': SAVE,
    'ctrl q': EXIT,
}


class SelText(urwid.Text):
    """A selectable text widget."""

    _selectable = True

    def keypress(self, size, key):
        """Don't handle any keys."""
        return key


class Menu(urwid.WidgetWrap):
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

        content = [urwid.AttrWrap(SelText(" " + w), None, attr[1])
                   for w in menu_list]

        #Calculate width and height of the menu widget:
        height = len(menu_list)
        width = 0
        for entry in menu_list:
            if len(entry) > width:
                width = len(entry)

        #Create the ListBox widget and put it on top of body:
        self._listbox = urwid.AttrWrap(urwid.ListBox(content), attr[0])
        overlay = urwid.Overlay(self._listbox, body, ('fixed left', pos[0]),
                                width + 2, ('fixed top', pos[1]), height)

        urwid.WidgetWrap.__init__(self, overlay)


    def keypress(self, size, key):

        if key == "enter":
            (widget, foo) = self._listbox.get_focus()
            (text, foo) = widget.get_text()
            self.selected = text[1:] #Get rid of the leading space...
        else:
            return self._listbox.keypress(size, key)



def menubar():
    """Menu bar at the top of the screen"""

    menu_text = [('menuh', " P"), ('menu', "rogram   "),
                 ]

    return urwid.AttrWrap(urwid.Text(menu_text), 'menu')



def statusbar():
    """
    Status bar at the bottom of the screen.
    """

    status_text = "Statusbar -- Press Alt + <key> for menu entries"
    return urwid.AttrWrap(urwid.Text(status_text), 'menu')



def body():
    """
    Body (main part) of the screen
    """

    main_text = " Hello world! \n\n I'm the main view."
    return urwid.AttrWrap(urwid.Filler(urwid.Text(main_text)), 'bg')



class Dialog(urwid.WidgetWrap):
    """
    Creates a BoxWidget that displays a message

    Attributes:

    b_pressed -- Contains the label of the last button pressed or None if no
                 button has been pressed.
    edit_text -- After a button is pressed, this contains the text the user
                 has entered in the edit field
    """

    b_pressed = None
    edit_text = None

    _blank = urwid.Text("")
    _edit_widget = None
    _mode = None

    def __init__(self, msg, buttons, attr, width, height, body, ):
        """
        msg -- content of the message widget, one of:
                   plain string -- string is displayed
                   (attr, markup2) -- markup2 is given attribute attr
                   [markupA, markupB, ... ] -- list items joined together
        buttons -- a list of strings with the button labels
        attr -- a tuple (background, button, active_button) of attributes
        width -- width of the message widget
        height -- height of the message widget
        body -- widget displayed beneath the message widget
        """

        #Text widget containing the message:
        msg_widget = urwid.Padding(urwid.Text(msg), 'center', width - 4)

        #GridFlow widget containing all the buttons:
        button_widgets = []

        for button in buttons:
            button_widgets.append(urwid.AttrWrap(
                urwid.Button(button, self._action), attr[1], attr[2]))

        button_grid = urwid.GridFlow(button_widgets, 12, 2, 1, 'center')

        #Combine message widget and button widget:
        widget_list = [msg_widget, self._blank, button_grid]
        self._combined = urwid.AttrWrap(urwid.Filler(
            urwid.Pile(widget_list, 2)), attr[0])

        #Place the dialog widget on top of body:
        overlay = urwid.Overlay(self._combined, body, 'center', width,
                                'middle', height)

        urwid.WidgetWrap.__init__(self, overlay)


    def _action(self, button):
        """
        Function called when a button is pressed.
        Should not be called manually.
        """

        self.b_pressed = button.get_label()
        if self._edit_widget:
            self.edit_text = self._edit_widget.get_edit_text()



def confirm_quit(ui, dim, display):
    """Confirm quit dialog"""

    confirm = Dialog("Really quit?", ["Yes", "No"],
                     ('menu', 'bg', 'bgf'), 30, 5, display)

    keys = True

    #Event loop:
    while True:
        if keys:
            ui.draw_screen(dim, confirm.render(dim, True))

        keys = ui.get_input()
        if "window resize" in keys:
            dim = ui.get_cols_rows()
        if "esc" in keys:
            return False
        for k in keys:
            confirm.keypress(dim, k)

        if confirm.b_pressed == "Yes":
            return True
        if confirm.b_pressed == "No":
            return False



def program_menu(ui, dim, display):
    """Program menu"""

    program_menu = Menu(["Save", "Save As", "Quit"],
                        ('menu', 'menuf'), (0, 1), display)

    keys = True

    #Event loop:
    while True:
        if keys:
            ui.draw_screen(dim, program_menu.render(dim, True))

        keys = ui.get_input()

        if "window resize" in keys:
            dim = ui.get_cols_rows()
        if "esc" in keys:
            return

        for k in keys:
            #Send key to underlying widget:
            program_menu.keypress(dim, k)

        if program_menu.selected == "Quit":
            if confirm_quit(ui, dim, display):
                sys.exit(0)
            else:
                return

        if program_menu.selected == "Foo":
            #Do something
            return

        if program_menu.selected == "Bar":
            #Do something
            return


class MainLoop(urwid.MainLoop):
    def run(self):
        try:
            self._run()
        except urwid.ExitMainLoop:
            pass
        except BaseException:
            self.screen.stop()
            raise


class InputHandler(object):
    def __init__(self, wrapper, display):
        self.wrapper = wrapper
        self.display = display

    def handle_input(self, key):
        dim = ui.get_cols_rows()

        command = urwid.command_map[key]
        if command == EXIT:
            if confirm_quit(ui, dim, self.display):
                sys.exit(0)
        if command == SAVE:
            self.wrapper.save()

        ui.draw_screen(dim, self.display.render(dim, True))



def run():
    """
    Main part.
    """
    palette = [('menu', 'black', 'light gray', 'standout'),
     ('menuh', 'yellow', 'light gray', ('standout', 'bold')),
     ('menuf', 'light gray', 'dark blue'),
     ('bgf', 'light gray', 'dark blue'),
     ('bg', 'black', 'light gray', 'standout'),
     ('alert', 'light gray', 'dark red', ('standout', 'bold')),
     ('code', 'black', 'light gray'),
     ('lineno', 'light blue', 'light gray'),
     ]

    #Set up displayed stuff:
    dim = ui.get_cols_rows()

    config = urwidwidget.EditorConfig(command_map=DEFAULT_COMMAND_MAP)
    wrapper = doctrine.code.CodeContext(sys.argv[1], 'python')
    with wrapper.open() as code:
        editwidget = urwidwidget.TextEditor(code, config)
        main_view = urwidwidget.LineNosWidget(editwidget)
        display = urwid.Frame(main_view, menubar(), statusbar())

        keys = True
        input_handler = InputHandler(wrapper, display)
        loop = MainLoop(display, palette=palette, unhandled_input=input_handler.handle_input)
        loop.run()
        sys.exit(0)


        #Main event loop:
        while True:
            if keys:
                #Redraw screen after user input:
                display = urwid.Frame(main_view, menubar(), statusbar())
                ui.draw_screen(dim, display.render(dim, True))

            keys = ui.get_input()

            if "window resize" in keys:
                dim = ui.get_cols_rows()
                continue

            if "meta P" in keys or "meta p" in keys:
                #Show program menu:
                program_menu(ui, dim, display)
                continue

            for key in keys:
                key = display.keypress(dim, key)

                if key is None:
                    continue  # Key was handled
                command = urwid.command_map[key]
                if command == EXIT:
                    #raise urwid.ExitMainLoop()
                    if confirm_quit(ui, dim, display):
                        sys.exit(0)

                if command == SAVE:
                    wrapper.save()


# Entry point. Perform some initialisation:

#init screen:
ui = urwid.raw_display.Screen()
ui.register_palette(
    [('menu', 'black', 'light gray', 'standout'),
     ('menuh', 'yellow', 'light gray', ('standout', 'bold')),
     ('menuf', 'light gray', 'dark blue'),
     ('bgf', 'light gray', 'dark blue'),
     ('bg', 'black', 'light gray', 'standout'),
     ('alert', 'light gray', 'dark red', ('standout', 'bold')),
     ('code', 'black', 'light gray'),
     ('lineno', 'light blue', 'light gray'),
     ])

#start main part:
def main():
    try:
        ui.tty_signal_keys(#intr='undefined',
                   #        quit='undefined',
                           start='undefined',
                           stop='undefined',
                           susp='undefined')
        ui.run_wrapper(run)
    except urwid.ExitMainLoop:
        pass
    except BaseException:
        ui.stop()
        raise

