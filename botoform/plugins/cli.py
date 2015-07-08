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

class cli(object):

    description="Open an Interactive prompt with access to evpc object"

    @staticmethod
    def setup_parser(parser):
        pass

    @staticmethod
    def main(args, evpc):
        """Main plugin application logic."""
        msg = 'You now have access to the evpc object, for example: evpc.roles'
        print('\n' + msg + '\n')
        if interpreter == 'bpython':
            bpython.embed(locals_ = locals(), banner = '\n' + msg + '\n')
        elif interpreter == 'ipython':
            IPython.embed()
        elif interpreter is None:
            code.interact(local = locals())


