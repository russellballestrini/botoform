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

BANNER = """
You are now connected to {} ({}) in {}

You now have access to the evpc object, for example: evpc.roles
"""

def REPL(args, evpc):
    """
    Open an interactive REPL (read-eval-print-loop) with access to evpc object
    """
    msg = BANNER.format(evpc.id, evpc.name, evpc.region_name)
    if interpreter == 'bpython':
        bpython.embed(locals_ = locals(), banner = msg)
    elif interpreter == 'ipython':
        IPython.embed(banner2 = msg)
    elif interpreter is None:
        code.interact(local = locals(), banner = msg)


