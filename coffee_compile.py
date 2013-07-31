import platform
import subprocess
import os
import sys

import sublime_plugin
import sublime



PLATFORM = sublime.platform()
PLATFORM_IS_WINDOWS = (PLATFORM == 'windows')

IS_SUBLIME_TEXT_2 = int(sublime.version()) < 3000


def log(msg):
    sys.stdout.write("[CoffeeCompile] %s\n" % msg)


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'

    def run(self, edit):
        log("Platform is '%s'" % PLATFORM)

        self.settings = sublime.load_settings("CoffeeCompile.sublime-settings")
        self.window   = self.view.window()
        self.editor   = SublimeTextEditorView(self.view)

        coffeescript = self.editor.get_text()
        coffeescript = coffeescript.encode('utf8')

        try:
            javascript = self._compile(coffeescript)
            self._write_javascript_to_panel(javascript, edit)
        except CoffeeCompilationError as e:
            self._write_compile_error_to_panel(e, edit)

    def _compile(self, coffeescript):
        path = self._get_path()
        args = self._get_coffee_args()

        try:
            javascript, error = self._execute_command(coffeescript, args, path)

            if error:
                raise CoffeeCompilationError(
                    path
                  , 'Something went horribly wrong  compiling your coffee'
                  , error
                )

            if javascript:
                javascript = javascript.strip()

            if javascript == "env: node: No such file or directory":
                message  = "`coffee` couldn't find NodeJS `coffee`.\n"
                message += "Your `node_path` setting is probably not configured properly.\n\n"
                message += "To configure CoffeeCompile, go to:\n"
                message += "`Preferences > Package Settings > CoffeeCompile > Settings - User`"
                raise CoffeeCompilationError(path, message, javascript)

            return javascript

        except OSError as e:
            raise CoffeeCompilationOSError(path, e)

    def _execute_command(self, text, args, path=None):
        # This is needed for Windows... not sure why. See:
        # https://github.com/surjikal/sublime-coffee-compile/issues/13

        if path and PLATFORM_IS_WINDOWS:
            os.environ['PATH'] = path
            path = None

        log("Executing command:\nPath=%s\nargs=%s" % (path, args))

        env = {'PATH': path} if path else None
        process = subprocess.Popen(args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            startupinfo=self._get_startupinfo(),
            env=env)

        output, error = process.communicate(text)

        if output:
            output = output.decode('utf8')

        return (output, error)

    def _create_panel(self):
        return SublimeTextOutputPanel(self.window, self.PANEL_NAME)

    def _write_javascript_to_panel(self, javascript, edit):
        panel = self._create_panel()
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')
        panel.display(javascript, edit)

    def _write_compile_error_to_panel(self, error, edit):
        panel = self._create_panel()
        panel.set_syntax_file('Packages/Markdown/Markdown.tmLanguage')
        panel.display(str(error), edit)

    def _get_coffee_args(self):
        if self.settings.get('coffee_script_redux'):
            log("Using coffee script redux.")
            return self._get_redux_coffee_args()
        else:
            log("Using vanilla compiler.")
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
        cmd = self.settings.get('coffee_executable')
        if not cmd:
            if PLATFORM_IS_WINDOWS:
                cmd = 'coffee.cmd'
            else:
                cmd = 'coffee'
        return cmd

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


class SublimeTextOutputPanel:

    def __init__(self, window, name):
        self.name = name
        self._window = window
        self._panel = self._get_or_create_panel(window, name)

    def show(self):
        self._window.run_command('show_panel', {'panel': 'output.%s' % self.name})

    def write(self, text, edit=None):
        self._panel.set_read_only(False)
        if IS_SUBLIME_TEXT_2:
            if not edit:
                edit = self._panel.begin_edit()
            self._panel.insert(edit, 0, text)
            self._panel.end_edit(edit)
            self._panel.sel().clear()
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
            log("Couldn't get output panel.")
            return window.create_output_panel(name)



class SublimeTextEditorView:
    def __init__(self, view):
        self._view = view

    def get_text(self):
        return self.get_selected_text() or self.get_all_text()

    def has_selected_text(self):
        for region in self._view.sel():
            if not region.empty(): return True
        return False

    def get_selected_text(self):
        if not self.has_selected_text():
            return None
        region = self._get_selected_region()
        return self._view.substr(region)

    def get_all_text(self):
        region = self._get_full_region()
        return self._view.substr(region)

    def _get_selected_region(self):
         return self._view.sel()[0]

    def _get_full_region(self):
        return sublime.Region(0, self._view.size())



class CoffeeCompilationError(Exception):
    """ Raised when something went wrong with the subprocess call """
    def __init__(self, path, message, details):
        self.path = path
        self.message = message
        self.details = details

    def __str__(self):
        output = \
"""# CoffeeCompile Error :(

%(message)s

## Details
```
%(details)s
```

## Halp
If you're sure that you've configured the plugin properly,
please open up an issue and I'll try to help you out!

https://github.com/surjikal/sublime-coffee-compile/issues

## Path
```
%(path)s
```
"""
        return output % {
            'message': self.message
          , 'details': self.details
          , 'path': "\n".join(self.path.split(':'))
        }



class CoffeeCompilationOSError(CoffeeCompilationError):

    def __init__(self, path, osError):
        message = "An OS Error was raised after calling `coffee`:\n"

        if osError.errno is 2:
            message  = "Could not find your `coffee` executable...\n"
            message += "Your `coffee_path` setting is probably not configured properly.\n\n"
            message += "To configure CoffeeCompile, go to:\n"
            message += "`Preferences > Package Settings > CoffeeCompile > Settings - User`"


        super(CoffeeCompilationOSError, self).__init__(
            path=path,
            message=message,
            details=repr(osError)
        )
