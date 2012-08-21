import platform

import sublime_plugin
import sublime
import os
import subprocess


PLATFORM_IS_WINDOWS = platform.system() == 'Windows'
COFFEE_COMMAND = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'
PANEL_NAME = 'coffeescript_output'


def _log(msg):
    print '[CoffeeCompile] %s' % msg

_log('Platform is "%s"' % platform.system())
_log('Coffee command is "%s"' % COFFEE_COMMAND)


def is_null_empty(value):
    return value is None or len(value) == 0


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        text = self._get_text_to_compile()
        window = self.view.window()

        javascript, error = self._compile(text, window)
        self._write_output_to_panel(window, javascript, error)

    def _compile(self, text, window):
        args = [COFFEE_COMMAND, '--stdio', '--print', '--lint']

        process = subprocess.Popen(args, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            startupinfo=self.get_startupinfo())
        return process.communicate(text)

    def _write_output_to_panel(self, window, javascript, error):

        panel = window.get_output_panel(PANEL_NAME)
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        output_view = window.get_output_panel(PANEL_NAME)
        output_view.set_read_only(False)
        edit = output_view.begin_edit()
        output_view.insert(edit, 0, javascript)
        output_view.end_edit(edit)
        output_view.sel().clear()
        output_view.set_read_only(True)
        window.run_command('show_panel', {'panel': 'output.' + PANEL_NAME})

    def _get_text_to_compile(self):
        region = self._get_selected_region() if self._editor_contains_selected_text() \
            else self._get_region_for_entire_file()
        return self.view.substr(region)

    def _get_region_for_entire_file(self):
        return sublime.Region(0, self.view.size())

    def _get_selected_region(self):
        return self.view.sel()[0]

    def _editor_contains_selected_text(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

    def get_startupinfo(self):
        info = None

        if os.name == 'nt':
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE

        return info
