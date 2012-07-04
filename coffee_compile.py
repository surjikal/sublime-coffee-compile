import sublime_plugin
import sublime


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        region = self.view.sel()[0] if self._buffer_contains_selected_text(self.view.sel()) \
                 else sublime.Region(0, self.view.size())

        text = self.view.substr(region)
        window = self.view.window()

        panel = window.get_output_panel("exec")
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        window.run_command('exec', {
            'cmd': ['coffee', '--print', '--lint', '--eval', text],
            'quiet': True
        })

    def _buffer_contains_selected_text(self, buffer):
        for region in buffer:
            if not region.empty():
                return True
        return False
