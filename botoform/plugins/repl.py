import code

interpreter = None

try:
    import IPython
    interpreter = 'ipython'
except ImportError:
    pass

try:
    import bpython
    interpreter = 'bpython'
except ImportError:
    pass

def REPL(args, evpc):
    """
    Open an interactive REPL (read-eval-print-loop) with access to evpc object
    """
    msg = '\nYou now have access to the evpc object, for example: evpc.roles\n'
    if interpreter == 'bpython':
        bpython.embed(locals_ = locals(), banner = msg)
    elif interpreter == 'ipython':
        IPython.embed(banner2 = msg)
    elif interpreter is None:
        code.interact(local = locals(), banner = msg)


