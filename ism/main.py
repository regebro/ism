import urwid
import sys
from doctrine import urwid as urwidwidget
import doctrine.code


palette = [
    ('body','black', 'light gray'),
    ('foot','dark cyan', 'dark blue', 'bold'),
    ('key','light cyan', 'dark blue', 'underline'),
    ('lineno', 'light red', 'white'),
    ]

SAVE = 'save'
EXIT = 'exit'

DEFAULT_COMMAND_MAP = {
    'backspace': urwidwidget.ERASE_LEFT,
    'delete': urwidwidget.ERASE_RIGHT,
    'ctrl s': SAVE,
    'ctrl q': EXIT,
}


class InputHandler(object):
    def __init__(self, wrapper):
        self.wrapper = wrapper

    def handle_input(self, key):
        command = urwid.command_map[key]
        if command == EXIT:
            raise urwid.ExitMainLoop()
        if command == SAVE:
            self.wrapper.save()


class MainLoop(urwid.MainLoop):
    def run(self):
        try:
            self.screen.tty_signal_keys(intr='undefined',
                                        quit='undefined',
                                        start='undefined',
                                        stop='undefined',
                                        susp='undefined')
            self._run()
        except urwid.ExitMainLoop:
            pass
        except BaseException:
            self.screen.stop()
            raise

def main():
    config = urwidwidget.EditorConfig(command_map=DEFAULT_COMMAND_MAP)
    wrapper = doctrine.code.CodeContext(sys.argv[1], 'python')
    input_handler = InputHandler(wrapper)
    with wrapper.open() as code:
        editwidget = urwidwidget.TextEditor(code, config)
        linenos = urwidwidget.LineNosWidget(editwidget)
        loop = MainLoop(linenos, palette=palette, unhandled_input=input_handler.handle_input)
        loop.run()
