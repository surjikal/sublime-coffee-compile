import os
import subprocess
import sublime
import sys

try:
    from .utils import log
except ValueError:
    from utils import log


PLATFORM_IS_WINDOWS = (sublime.platform() == 'windows')


def execute(args, message='', path=None, cwd=None):
    # This is needed for Windows... not sure why. See:
    # https://github.com/surjikal/sublime-coffee-compile/issues/13
    if path:
        log('Path:')
        log("\n".join(path))
        path = os.pathsep.join(path)
        if PLATFORM_IS_WINDOWS:
            log('Platform is Windows!')
            os.environ['PATH'] = path
            path = None

    env = {'PATH': path} if path else None
    log('Env:')
    log(env)
    log('Args:')
    log(args)

    process = subprocess.Popen(args,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        startupinfo=_get_startupinfo(),
        env=env,
        cwd=cwd)

    output, error = process.communicate(message)

    if output:
        output = output.decode('utf8')
        output = output.strip()

    return (output, error)


def _get_startupinfo():
    if PLATFORM_IS_WINDOWS:
        info = subprocess.STARTUPINFO()
        info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        info.wShowWindow = subprocess.SW_HIDE
        return info
    return None

