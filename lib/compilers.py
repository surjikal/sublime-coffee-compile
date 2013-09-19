import os
try:                import JSON
except ImportError: import json as JSON

try:
    from .execute import execute
    from .exceptions import CoffeeCompilationUnknownError, CoffeeCompilationOSError, CoffeeModuleNotFoundError, CoffeeExecutableNotFoundError
except ValueError:
    from execute import execute
    from exceptions import CoffeeCompilationUnknownError, CoffeeCompilationOSError, CoffeeModuleNotFoundError, CoffeeExecutableNotFoundError


class CoffeeCompiler(object):

    def __init__(self, node_path=None):
        self.node_path = node_path

    def compile(self, coffeescript, options={}):
        raise NotImplementedError()

    def _execute(self, args, coffeescript='', cwd=None):
        path = self._get_path()
        self.path = path # FIXME: Side effect... required by exceptions raised from derived classes.
        try:
            javascript, error = execute(args=args, message=coffeescript, path=path, cwd=cwd)
            if error: raise CoffeeCompilationUnknownError(path, error)
            return javascript
        except OSError as e:
            raise CoffeeCompilationOSError(self.path, e)

    def _get_path(self):
        path = os.environ.get('PATH', '').split(os.pathsep)
        if self.node_path: path.append(self.node_path)
        return path


class CoffeeCompilerModule(CoffeeCompiler):

    def __init__(self, node_path=None, cwd=None):
        CoffeeCompiler.__init__(self, node_path)
        self.cwd = cwd

    def compile(self, coffeescript, options={}):
        bootstrap  = self._get_bootstrap_script(options)
        javascript = self._execute(
            args=['node', '-e', bootstrap]
          , coffeescript=coffeescript
          , cwd=self.cwd
        )
        if javascript.startswith('module.js'):
            require_search_paths = self._get_require_search_paths()
            raise CoffeeModuleNotFoundError(self.path, javascript, require_search_paths)
        return javascript

    def _get_bootstrap_script(self, options={}):
        return """
        var coffee = require('coffee-script');
        var buffer = "";
        process.stdin.on('data', function(d) { buffer += d; });
        process.stdin.on('end',  function()  { console.log(coffee.compile(buffer, %s)); });
        process.stdin.read();
        """ % self._options_to_json(options)

    def _get_require_search_paths(self):
        return self._execute(
            args=['node', '-e', "console.log(module.paths)"]
          , cwd=self.cwd
        )

    def _options_to_json(self, options={}):
        return 'null'
        return JSON.dumps({
            'bare': options.get('bare', False)
        })


class CoffeeCompilerExecutable(CoffeeCompiler):

    def __init__(self, node_path=None, coffee_path=None, coffee_executable=None):
        CoffeeCompiler.__init__(self, node_path)
        self.coffee_path       = coffee_path
        self.coffee_executable = coffee_executable

    def compile(self, coffeescript, args):
        javascript = self._execute(
            coffeescript=coffeescript
          , args=([self.coffee_executable] + args)
        )
        if javascript == "env: node: No such file or directory":
            raise CoffeeExecutableNotFoundError(self.path, javascript)
        return javascript

    def _get_path(self):
        path = CoffeeCompiler._get_path(self)
        if self.coffee_path: path.append(self.coffee_path)
        return path


class CoffeeCompilerExecutableVanilla(CoffeeCompilerExecutable):

    def compile(self, coffeescript, options):
        return CoffeeCompilerExecutable.compile(self,
            coffeescript=coffeescript
          , args=self._options_to_args(options)
        )

    def _options_to_args(self, options):
        args = ['--stdio', '--print']
        if options.get('bare'): args.append('--bare')
        return args
