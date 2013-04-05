import platform
import subprocess
import os
import sys

import sublime_plugin
import sublime


SETTINGS = sublime.load_settings("CoffeeCompile.sublime-settings")

PLATFORM = platform.system()
PLATFORM_IS_WINDOWS = PLATFORM is 'Windows'
PLATFORM_IS_OSX     = PLATFORM is 'Darwin'


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'
    DEFAULT_COFFEE_EXECUTABLE = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'

    def run(self, edit):
        coffeescript = self._get_text_to_compile()
        coffeescript = coffeescript.encode('utf8')
        window = self.view.window()

        javascript, error = self._compile(coffeescript, window)
        if error: self._log(error)
        self._write_output_to_panel(window, javascript.decode('utf8'), error, edit)

    def _compile(self, text, window):
        path = self._get_path()
        args = self._get_coffee_args()
        self._log("Using PATH=%s" % path)
        try:
            return self._execute_command(args, text, path)
        except OSError as e:
            error_message = '# CoffeeCompile error\n'

            if e.errno is 2:
                error_message += 'Could not find your `coffee` executable\n'

            error_message += "\n## Details\n%s\n\n" % str(e)
            error_message += "## PATH\n%s\n" % "\n".join(path.split(':'))

            sublime.status_message('CoffeeCompile Error :(')
            return (b'', error_message)

    def _execute_command(self, args, text, path=None):
        # This is needed for Windows... not sure why. See:
        # https://github.com/surjikal/sublime-coffee-compile/issues/13
        if path and PLATFORM_IS_WINDOWS:
            os.environ['PATH'] = path
            path = None

        env = {'PATH': path} if path else None
        process = subprocess.Popen(args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=self._get_startupinfo(),
            env=env)
        return process.communicate(text)

    def _write_output_to_panel(self, window, javascript, error=None, edit=None):
        panel = window.get_output_panel(self.PANEL_NAME)
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        text = javascript or str(error)
        self._write_to_panel(panel, text, edit)
        self._show_panel(window)

    def _write_to_panel(self, panel, text, edit=None):
        panel.set_read_only(False)

        if not edit:
            edit = panel.begin_edit()

        panel.insert(edit, 0, text)
        panel.end_edit(edit)
        panel.sel().clear()
        panel.set_read_only(True)

    def _show_panel(self, window):
        window.run_command('show_panel', {'panel': 'output.%s' % self.PANEL_NAME})

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

    def _get_coffee_args(self):
        if SETTINGS.get('coffee_script_redux'):
            self._log("Using coffee script redux.")
            return self._get_redux_coffee_args()
        else:
            self._log("Using vanilla compiler.")
            return self._get_vanilla_coffee_args()

    def _get_vanilla_coffee_args(self):
        coffee_executable = self._get_coffee_executable()

        args = [coffee_executable, '--stdio', '--print', '--lint']

        if SETTINGS.get('bare'):
            args.append('--bare')

        return args

    def _get_redux_coffee_args(self):
        coffee_executable = self._get_coffee_executable()
        return [coffee_executable, '--js']

    def _get_coffee_executable(self):
        return SETTINGS.get('coffee_executable') or self.DEFAULT_COFFEE_EXECUTABLE

    def _get_startupinfo(self):
        if PLATFORM_IS_WINDOWS:
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
            return info
        return None

    def _get_path(self):
        node_path   = SETTINGS.get('node_path')
        coffee_path = self._get_coffee_path()

        path = os.environ.get('PATH', '').split(':')

        if node_path:
            path.append(node_path)
        if coffee_path:
            path.append(coffee_path)

        return ":".join(path)

    def _get_coffee_path(self):
        coffee_path = SETTINGS.get('coffee_path')

        if SETTINGS.get('coffee_script_redux'):
            return SETTINGS.get('redux_coffee_path') or coffee_path

        return coffee_path

    def _log(self, msg):
        sys.stdout.write("[CoffeeCompile] %s\n" % msg)
