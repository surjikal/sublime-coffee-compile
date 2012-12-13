import platform
import subprocess
import os

import sublime_plugin
import sublime


PLATFORM = platform.system()
PLATFORM_IS_WINDOWS = PLATFORM is 'Windows'
PLATFORM_IS_OSX     = PLATFORM is 'Darwin'


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'
    DEFAULT_COFFEE_EXECUTABLE = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'
    SETTINGS = sublime.load_settings("CoffeeCompile.sublime-settings")

    def run(self, edit):
        text = self._get_text_to_compile()
        text = text.encode('utf8')
        window = self.view.window()

        javascript, error = self._compile(text, window)
        self._write_output_to_panel(window, javascript, error)

    def _compile(self, text, window):
        path = self._get_path()
        args = self._get_coffee_args()
        print "[CoffeeCompile] Using PATH=%s" % path
        try:
            return self._execute_command(args, text, path)
        except OSError as e:
            error_message = 'CoffeeCompile error: '
            if e.errno is 2:
                error_message += 'Could not find your "coffee" executable. '
            error_message += str(e)

            sublime.status_message(error_message)
            return ('', error_message)

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

    def _write_output_to_panel(self, window, javascript, error):
        panel = window.get_output_panel(self.PANEL_NAME)
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        text = javascript or str(error)
        text = text.decode('utf8')
        self._write_to_panel(panel, text)

        window.run_command('show_panel', {'panel': 'output.%s' % self.PANEL_NAME})

    def _write_to_panel(self, panel, text):
        panel.set_read_only(False)
        edit = panel.begin_edit()
        panel.insert(edit, 0, text)
        panel.end_edit(edit)
        panel.sel().clear()
        panel.set_read_only(True)

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
        if self.SETTINGS.get('coffee_script_redux'):
            print "[CoffeeCompile] Using coffee script redux."
            return self._get_redux_coffee_args()
        else:
            print "[CoffeeCompile] Using vanilla compiler."
            return self._get_vanilla_coffee_args()

    def _get_vanilla_coffee_args(self):
        coffee_executable = self._get_coffee_executable()

        args = [coffee_executable, '--stdio', '--print', '--lint']

        if self.SETTINGS.get('bare'):
            args.append('--bare')

        return args

    def _get_redux_coffee_args(self):
        coffee_executable = self._get_coffee_executable()
        return [coffee_executable, '--js']

    def _get_coffee_executable(self):
        return self.SETTINGS.get('coffee_executable') or self.DEFAULT_COFFEE_EXECUTABLE

    def _get_startupinfo(self):
        if PLATFORM_IS_WINDOWS:
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
            return info
        return None

    def _get_path(self):
        node_path   = self.SETTINGS.get('node_path')
        coffee_path = self._get_coffee_path()

        path = os.environ.get('PATH', '').split(':')

        if node_path:
            path.append(node_path)
        if coffee_path:
            path.append(coffee_path)

        return ":".join(path)

    def _get_coffee_path(self):
        coffee_path = self.SETTINGS.get('coffee_path')

        if self.SETTINGS.get('coffee_script_redux'):
            return self.SETTINGS.get('redux_coffee_path') or coffee_path

        return coffee_path
