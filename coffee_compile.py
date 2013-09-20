import os
import traceback

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


PLATFORM_IS_WINDOWS = (sublime.platform() == 'windows')
DEFAULT_COFFEE_CMD = 'coffee.cmd' if PLATFORM_IS_WINDOWS else 'coffee'
DEFAULT_COMPILER = 'vanilla-executable'


def settings_adapter(settings):

    node_path = settings.get('node_path')

    def get_executable_compiler():
        coffee_executable = settings.get('coffee_executable') or DEFAULT_COFFEE_CMD
        coffee_path = settings.get('coffee_path')
        print(coffee_path)
        return CoffeeCompilerExecutableVanilla(
            node_path
          , coffee_path
          , coffee_executable
        )

    def get_module_compiler():
        cwd = settings.get('cwd')
        return CoffeeCompilerModule(node_path, cwd)

    def get_compiler():
        compiler = settings.get('compiler') or DEFAULT_COMPILER
        if compiler == 'vanilla-executable':
            return get_executable_compiler()
        elif compiler == 'vanilla-module':
            return get_module_compiler()
        else:
            raise InvalidCompilerSettingError(compiler)

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
        except InvalidCompilerSettingError as e:
            e = CoffeeCompilationError(path='', message=str(e), details='')
            self._write_compile_error_to_panel(e, edit)
        except Exception as e:
            e = CoffeeCompilationError(path='', message="Unexpected Exception!", details=traceback.format_exc())
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


class InvalidCompilerSettingError(Exception):
    def __init__(self, compiler):
        self.compiler = compiler
        self.available_compilers = [
            'vanilla-executable',
            'vanilla-module'
        ]
    def __str__(self):
        message = "Compiler `%s` is not a valid compiler setting choice.\n\n" % self.compiler
        message+= "Available choices are:\n\n- "
        message+= "\n- ".join(self.available_compilers)
        message+= "\n"
        return message
