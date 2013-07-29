import platform
import subprocess
import os
import sys

import sublime_plugin
import sublime



PLATFORM = sublime.platform()
PLATFORM_IS_WINDOWS = PLATFORM is 'windows'
PLATFORM_IS_OSX     = PLATFORM is 'osx'

IS_SUBLIME_TEXT_2 = int(sublime.version()) < 3000



class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'
    DEFAULT_COFFEE_EXECUTABLE = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'

    def run(self, edit):
        self.settings = sublime.load_settings("CoffeeCompile.sublime-settings")
        self.window   = self.view.window()

        coffeescript = self._get_text_to_compile()
        coffeescript = coffeescript.encode('utf8')

        path = self._get_path()
        args = self._get_coffee_args()

        self._log("Path is\n%s" % path)

        try:
            javascript = self._compile(coffeescript, args, path)
            self._write_javascript_to_panel(javascript, edit)
        except CoffeeCompileError as e:
            self._log(e)
            self._write_compile_error_to_panel(e, edit)

    def _compile(self, coffeescript, args, path):
        try:
            javascript, error = self._execute_command(coffeescript, args, path)
            if error: raise CoffeeCompilationError(error)
            return javascript.decode('utf8')
        except OSError as e:
            raise CoffeeCompilationOSError(e, path)

    def _execute_command(self, text, args, path=None):
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

    def _write_javascript_to_panel(self, javascript, edit):
        panel = self._create_panel()
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')
        panel.display(javascript, edit)

    def _write_compile_error_to_panel(self, error, edit):
        panel = self._create_panel()
        panel.display(str(error), edit)

    def _create_panel(self):
        return SublimeTextOutputPanel(self.window, self.PANEL_NAME)

    def _get_text_to_compile(self):
        region = self._get_region()
        return self.view.substr(region)

    def _get_region(self):
        if self._editor_contains_selected_text():
            # return selected region
            return self.view.sel()[0]
        else:
            # return region that spans the entire file
            return sublime.Region(0, self.view.size())

    def _editor_contains_selected_text(self):
        for region in self.view.sel():
            if not region.empty():
                return True
        return False

    def _get_coffee_args(self):
        if self.settings.get('coffee_script_redux'):
            self._log("Using coffee script redux.")
            return self._get_redux_coffee_args()
        else:
            self._log("Using vanilla compiler.")
            return self._get_vanilla_coffee_args()

    def _get_vanilla_coffee_args(self):
        coffee_executable = self._get_coffee_executable()

        args = [coffee_executable, '--stdio', '--print']

        if self.settings.get('bare'):
            args.append('--bare')

        return args

    def _get_redux_coffee_args(self):
        coffee_executable = self._get_coffee_executable()
        return [coffee_executable, '--js']

    def _get_coffee_executable(self):
        return self.settings.get('coffee_executable') or self.DEFAULT_COFFEE_EXECUTABLE

    def _get_startupinfo(self):
        if PLATFORM_IS_WINDOWS:
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
            return info
        return None

    def _get_path(self):
        node_path   = self.settings.get('node_path')
        coffee_path = self._get_coffee_path()

        path = os.environ.get('PATH', '').split(':')

        if node_path:
            path.append(node_path)
        if coffee_path:
            path.append(coffee_path)

        return ":".join(path)

    def _get_coffee_path(self):
        coffee_path = self.settings.get('coffee_path')

        if self.settings.get('coffee_script_redux'):
            return self.settings.get('redux_coffee_path') or coffee_path

        return coffee_path

    def _log(self, msg):
        sys.stdout.write("[CoffeeCompile] %s\n" % msg)



class SublimeTextOutputPanel:

    def __init__(self, window, name):
        self.name = name
        self._window = window
        self._panel = self._get_or_create_panel(window, name)

    def show(self):
        self._window.run_command('show_panel', {'panel': 'output.%s' % self.name})

    def write(self, text, edit=None):
        if IS_SUBLIME_TEXT_2:
            self._panel.set_read_only(False)
            if not edit:
                edit = self._panel.begin_edit()
            self._panel.insert(edit, 0, text)
            self._panel.end_edit(edit)
            self._panel.sel().clear()
            self._panel.set_read_only(True)
        else:
            self._panel.run_command('append', {'characters': text})

    def display(self, text, edit=None):
        self.write(text, edit)
        self.show()

    def set_syntax_file(self, syntax_file):
        self._panel.set_syntax_file(syntax_file)

    def _get_or_create_panel(self, window, name):
        try:
            return window.get_output_panel(name)
        except AttributeError:
            return window.create_output_panel(name)



class CoffeeCompileError(Exception):
    def __init__(self, message):
        self.message
    def __str__(self):
        return str(self.message)



class CoffeeCompilationError(Exception):
    """ Raised when your coffee is bad """
    def __init__(self, message):
        super(CoffeeCompilationError, self).__init__(message)



class CoffeeCompilationOSError(Exception):
    """ Raised when your paths are not configured properly """
    def __init__(self, error, path):
        super(CoffeeCompilationOSError, self).__init__(self._make_message(error, path))

    def _make_message(self, error, path):
        message = '# CoffeeCompile error\n'
        if error.errno is 2:
            message += 'Could not find your `coffee` executable\n'
        message += "\n## Details\n%s\n\n" % str(error)
        message += "## PATH\n%s\n" % "\n".join(path.split(':'))
        return message
