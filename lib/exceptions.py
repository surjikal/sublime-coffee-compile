

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
          , 'path': "\n".join(self.path)
        }


class CoffeeCompilationOSError(CoffeeCompilationError):

    def __init__(self, path, osError):
        message = "An OS Error was raised after calling your `coffee` executable\n"

        if osError.errno is 2:
            message  = "Could not find your `coffee` executable...\n"
            message += "Your `coffee_path` setting is probably not configured properly.\n\n"
            message += "To configure CoffeeCompile, go to:\n"
            message += "`Preferences > Package Settings > CoffeeCompile > Settings - User`"


        super(CoffeeCompilationOSError, self).__init__(
            path=path
          , message=message
          , details=repr(osError)
        )


class CoffeeCompilationCompilerNotFoundError(CoffeeCompilationError):

    def __init__(self):
        message = "Couldn't compile your coffee... can't find your coffee compiler!"

        details  = "CoffeeCompile can't use the nodejs/module-based compiler because you're\n"
        details += "editing an unsaved file, and therefore don't have a current working directory.\n\n"

        details += "You probably want to use the `coffee_path` setting, since it lets you\n"
        details += "explicitly set a path to your coffee script compiler.\n\n"

        details += "To configure CoffeeCompile and the `coffee_path` setting, go to:\n"
        details += "`Preferences > Package Settings > CoffeeCompile > Settings - User`"

        super(CoffeeCompilationCompilerNotFoundError, self).__init__(
            path=''
          , message=message
          , details=details
        )



class CoffeeModuleNotFoundError(CoffeeCompilationError):
    def __init__(self, path, details, require_search_paths):
        message  = "NodeJS cannot find your `coffee-script` module.\n\n\n"

        message += "## `module.paths`:\n"
        message += require_search_paths
        message += "\n"

        super(CoffeeModuleNotFoundError, self).__init__(
            path=path
          , message=message
          , details=details
        )


class CoffeeExecutableNotFoundError(CoffeeCompilationError):
    def __init__(self, path, details):
        message  = "Your `coffee` executable couldn't find NodeJS in his path.\n"
        message += "Your `node_path` setting is probably not configured properly.\n\n"
        message += "To configure CoffeeCompile, go to:\n"
        message += "`Preferences > Package Settings > CoffeeCompile > Settings - User`"

        super(CoffeeExecutableNotFoundError, self).__init__(
            path=path
          , message=message
          , details=details
        )


class CoffeeCompilationUnknownError(CoffeeCompilationError):
    def __init__(self, path, details):
        super(CoffeeCompilationUnknownError, self).__init__(
            path=path
          , message='Something went horribly wrong compiling your coffee D:'
          , details=details
        )
