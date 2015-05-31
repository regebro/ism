import urwid
import sys
from doctrine.urwid import TextEditor, LineNosWidget, EditorConfig
import doctrine.code


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()


palette = [
    ('body','black', 'light gray'),
    ('foot','dark cyan', 'dark blue', 'bold'),
    ('key','light cyan', 'dark blue', 'underline'),
    ('lineno', 'light red', 'white'),
    ]

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
    config = EditorConfig()
    with open(sys.argv[1]) as file:
        editwidget = TextEditor(doctrine.code.Code(file, 'python'), config)
        linenos = LineNosWidget(editwidget)
        loop = MainLoop(linenos, palette=palette, unhandled_input=exit_on_q)
        loop.run()
