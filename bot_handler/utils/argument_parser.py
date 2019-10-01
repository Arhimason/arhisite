import argparse


class WrongArguments(Exception):
    pass


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        kwargs['add_help'] = False
        kwargs['prog'] = args[0]
        kwargs['prog'] = '/' + kwargs['prog']

        super(ArgumentParser, self).__init__(**kwargs)

    def _get_action_from_name(self, name):
        """Given a name, get the Action instance registered with this parser.
        If only it were made available in the ArgumentError object. It is
        passed as it's first arg...
        """
        container = self._actions
        if name is None:
            return None
        for action in container:
            if '/'.join(action.option_strings) == name:
                return action
            elif action.metavar == name:
                return action
            elif action.dest == name:
                return action

    def error(self, message):
        errstr = self.format_usage() + '\n' + \
                 '{}: error: {}'.format(self.prog, message)
        raise WrongArguments(errstr)
