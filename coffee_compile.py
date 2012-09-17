import subprocess

import sublime_plugin
import sublime


PLATFORM_IS_WINDOWS = sublime.platform() is 'windows'

class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'
    DEFAULT_COFFEE_EXECUTABLE = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'
    SETTINGS = sublime.load_settings("CoffeeCompile.sublime-settings")

    def run(self, edit):
        text = self._get_text_to_compile()
        javascript, error = self.compile(text)
        self.show(javascript or str(error))

    def compile(self, text):
        args = self._get_coffee_args()

        try:
            process = subprocess.Popen(args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=self._get_startupinfo())
            return process.communicate(text)

        except OSError as e:
            error_message = 'CoffeeCompile error: '
            if e.errno is 2:
                error_message += 'Could not find your "coffee" executable. '
            error_message += str(e)

            sublime.status_message(error_message)
            return ('', error_message)

    def show(self, text):
        window = self.view.window()
        output = self._get_output()
        syntax = 'Packages/JavaScript/JavaScript.tmLanguage'

        output.show(window, text, syntax)

    def _get_output(self):
        output_name = self.SETTINGS.get('output')
        return OUTPUT_FROM_SETTINGS_VALUE.get(output_name, 'panel')()

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
        coffee_executable = self._get_coffee_executable()

        args = [coffee_executable, '--stdio', '--print', '--lint']
        if self.SETTINGS.get('bare'):
            args.append('--bare')

        return args

    def _get_coffee_executable(self):
        return self.SETTINGS.get('coffee_executable') or self.DEFAULT_COFFEE_EXECUTABLE

    def _get_startupinfo(self):
        if PLATFORM_IS_WINDOWS:
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = subprocess.SW_HIDE
            return info
        return None



class OutputWrapper(object):

    def show(self, window, text, syntax):
        output = self._get_output(window)
        output.set_syntax_file(syntax)
        self._write_to_output(output, text)
        self._show_output(window)

    def _get_output(self, window):
        raise NotImplementedError

    def _show_output(self, window):
        pass

    def _write_to_output(self, output, text):
        output.set_read_only(False)
        edit = output.begin_edit()
        output.insert(edit, 0, text)
        output.end_edit(edit)
        output.sel().clear()
        output.set_read_only(True)


class ScratchWindowOutputWrapper(OutputWrapper):

    def _get_output(self, window):
        output = window.new_file()
        output.set_scratch(True)
        output.set_name('CoffeeCompile')
        return output


class PanelOutputWrapper(OutputWrapper):

    PANEL_NAME = 'coffeecompile_output'

    def _get_output(self, window):
        return window.get_output_panel(self.PANEL_NAME)

    def _show_output(self, window):
        window.run_command('show_panel', {'panel': 'output.%s' % self.PANEL_NAME})


OUTPUT_FROM_SETTINGS_VALUE = {
    'panel': PanelOutputWrapper,
    'window': ScratchWindowOutputWrapper
}
