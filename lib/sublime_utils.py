import sublime


def get_sublime_version():
    if int(sublime.version()) < 3000: return 2
    return 3


def is_sublime_text_2():
    return get_sublime_version() == 2


class SublimeTextOutputPanel:

    def __init__(self, window, name):
        self.name = name
        self._window = window
        self._panel = self._get_or_create_panel(window, name)

    def show(self):
        self._window.run_command('show_panel', {'panel': 'output.%s' % self.name})

    def write(self, text, edit=None):
        self._panel.set_read_only(False)
        if is_sublime_text_2():
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
