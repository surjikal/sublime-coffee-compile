import os

import sublime_plugin
import sublime


try:
    from .lib.compilers import CoffeeCompilerModule, CoffeeCompilerExecutableVanilla
    from .lib.exceptions import CoffeeCompilationError, CoffeeCompilationCompilerNotFoundError
    from .lib.sublime_utils import SublimeTextOutputPanel, SublimeTextEditorView
    from .lib.utils import log
except ValueError:
    from lib.compilers import CoffeeCompilerModule, CoffeeCompilerExecutableVanilla
    from lib.exceptions import CoffeeCompilationError, CoffeeCompilationCompilerNotFoundError
    from lib.sublime_utils import SublimeTextOutputPanel, SublimeTextEditorView
    from lib.utils import log


DEFAULT_COFFEE_CMD = 'coffee.cmd' if sublime.platform() is 'windows' else 'coffee'


# if we have a `coffee_path` setting set, then we use the executable-
# based compiler. Otherwise, we use the module-based one.
def settings_adapter(settings):

    def get_compiler():
        node_path   = settings.get('node_path')
        coffee_path = settings.get('coffee_path')

        # We are using an executable-based compiler
        if bool(coffee_path):
            coffee_executable = settings.get('coffee_executable') or DEFAULT_COFFEE_CMD
            return CoffeeCompilerExecutableVanilla(
                node_path
              , coffee_path
              , coffee_executable
            )
        # We are using a module-based compiler
        else:
            cwd = settings.get('cwd')
            return CoffeeCompilerModule(node_path, cwd)

    # (compiler, options)
    return (get_compiler(), {
        'bare': settings.get('bare')
    })


class CoffeeCompileCommand(sublime_plugin.TextCommand):

    PANEL_NAME = 'coffeecompile_output'

    def run(self, edit):
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
        filename = self.view.file_name()

        if filename:
            self.settings.set('cwd', os.path.dirname(filename))
        elif not self.settings.get('coffee_path', None):
            raise CoffeeCompilationCompilerNotFoundError()

        (compiler, options) = settings_adapter(self.settings)
        return compiler.compile(coffeescript, options)

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