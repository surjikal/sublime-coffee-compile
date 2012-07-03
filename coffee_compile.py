import sublime_plugin


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        region = self.view.sel()[0]
        selectedText = self.view.substr(region)
        window = self.view.window()

        panel = window.get_output_panel("exec")
        panel.set_syntax_file('Packages/JavaScript/JavaScript.tmLanguage')

        window.run_command('exec', {
            'cmd': ['coffee', '--print', '--lint', '--eval', selectedText],
            'quiet': True
        })
        window.run_command("echo", {"panel": "output.exec"})

    def is_visible(self):
        buffer = self.view.sel()
        return self._buffer_contains_selected_text(buffer)

    def is_enabled(self):
        return self.is_visible()

    def _buffer_contains_selected_text(self, buffer):
        for region in buffer:
            if not region.empty():
                return True
        return False
