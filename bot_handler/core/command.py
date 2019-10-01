import collections
import importlib
import importlib.util
import logging
import os

from bot_handler import CONFIG
from bot_handler.CONFIG import ENABLED_MODULES, MODULES_SOURCES
from bot_handler.utils.argument_parser import ArgumentParser
from lib.Tools import get_exc_info

# from lib.Notifier import notify
MSG_MAX_PART = 4000


def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


# todo autodiscover commands in other django apps \ in scripts
def methods_with_decorator(cls, decorator):
    """
        Returns all methods in CLS with DECORATOR as the
        outermost decorator.

        DECORATOR must be a "registering decorator"; one
        can make any decorator "registering" via the
        makeRegisteringDecorator function.
    """
    for maybe_decorated in cls.__dict__.values():
        if hasattr(maybe_decorated, 'decorator'):
            if maybe_decorated.decorator == decorator:
                # print(maybeDecorated)
                yield maybe_decorated


class PartedMsg:
    good_split_chr = ['\n', '    ', '.', ' ']

    def __init__(self, msg, max_part):
        self.msg = msg
        self.max_part = max_part

    def __next__(self):
        if not self.msg:
            raise StopIteration
        searcher = -1
        for c in self.good_split_chr:
            searcher = self.msg.rfind(c, int(self.max_part * 0.8), self.max_part)
            if searcher != -1:
                break
        if searcher == -1:
            searcher = self.max_part

        part = self.msg[:searcher]
        self.msg = self.msg[searcher:]
        return part


def import_file_commands(path):
    # print(path)
    pmod_name = path[:-3].replace('/', '.')
    # print(pmod_name)
    spec = importlib.util.spec_from_file_location(pmod_name, path)
    file = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(file)
    return methods_with_decorator(file, Command)


def get_module_commands(module_path):
    files = os.listdir(module_path)
    files_commands = {}

    for filename in files:
        if filename[0] != '_' and filename[-3:] == '.py':
            file_path = os.path.join(module_path, filename)

            fn = filename[:-3]
            files_commands[fn] = import_file_commands(file_path)
    return files_commands


# todo refact
def get_source_cmds(modules_source):
    cmds_list = {"main": {}, "_replace_user_": {}, "_replace_peer_": {}}
    maybe_modules = os.listdir(modules_source)
    for module in maybe_modules:
        module_path = os.path.join(modules_source, module)
        if not os.path.isdir(module_path):
            continue

        if module not in ENABLED_MODULES:
            continue

        module_commands = get_module_commands(module_path)
        for filename, file_commands in module_commands.items():
            if module in ['_replace_peer_', '_replace_user_']:
                if filename not in cmds_list[module]:
                    cmds_list[module][filename] = {}
                cur_list = cmds_list[module][filename]
            else:
                cur_list = cmds_list['main']

            for command in file_commands:
                if (CONFIG.ALLOWED_CMDS is not None) and (command.name not in CONFIG.ALLOWED_CMDS):
                    if (CONFIG.ALLOWED_BLOCKS is not None) and (command.block not in CONFIG.ALLOWED_BLOCKS):
                        continue

                if command.name in cur_list:
                    raise Exception("Сommand overwriting  within  one source is not allowed. {}: {}".
                                    format(module_path, command.name))
                cur_list[command.name] = command
    return cmds_list


def load_commands():
    result_cmds_list = {"main": {}, "_replace_user_": {}, "_replace_peer_": {}}
    for modules_source in MODULES_SOURCES:
        if not os.path.exists(modules_source):
            logging.error('{} is invalid modules source'.format(modules_source))
            continue

        source_cmds_list = get_source_cmds(modules_source)

        result_cmds_list = dict_update(result_cmds_list, source_cmds_list)

    return result_cmds_list


# todo allow all with some from block?
class Command:
    def __init__(self, name, block=None, help=None,
                 disable_parser=False, allow_default=False,
                 hidden=False, description=None, epilog=None,
                 disable_log=False, cnt_func=lambda parser_p: 1,
                 allow_group_owner=False, supported_messengers=None):
        self.name = name
        self.block = block

        self.description = description
        self.help = help

        self.parser = ArgumentParser(name, description=description, epilog=epilog)

        self.allow_default = allow_default
        self.allow_group_owner = allow_group_owner

        self.hidden = hidden
        self.disable_log = disable_log
        self.disable_parser = disable_parser

        self.cnt_func = cnt_func

        self.supported_messengers = supported_messengers

        self.decorator = Command
        self._mode = "decorating"
        # print(self.help)

    def __call__(self, *args, **kw):
        if self._mode == "decorating":
            # if not inspect.isfunction(args[0]):
            #     text = 'Not a function obj\nfile: {}\nname: {}'.format(abspath, self.name)
            self.func = args[0]
            self._mode = "calling"
            return self
        # result = self.func(*args, **kw)
        # return result

    def get_help(self):
        if self.help:
            return self.help
        else:
            return self.parser.format_help()

    def run(self, current_use):
        no_errors = True
        try:
            response = self.func(current_use)
        except:
            no_errors = False
            current_use.traceback = get_exc_info()
            response = 'Error while <{}> execution\n'.format(self.name)
            if not current_use.in_conversation:
                if current_use.user.is_admin:
                    response += current_use.traceback

        if response is None:
            return no_errors

        if type(response) != dict:
            response = {'message': str(response)}

        if CONFIG.FORWARD and not current_use._responses and \
                not current_use.in_conversation and not current_use.is_action:
            if 'forward_messages' not in response:
                response['forward_messages'] = current_use.msg_id

        # last_msg_text = response['message']
        # todo send big by parts
        current_use.send_msg(response)
        return no_errors
