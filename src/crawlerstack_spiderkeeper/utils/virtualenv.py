"""
重新实现 virtualenv.run.__init.py 中的三个调用方法。主要移除了源文件中第 50 行 `_do_report_setup(parser, args)`
由于该方法中直接把  root logger 清理了，会导致后续无法正常使用 log ，所以手动移除代码
对于此问题讨论详见： https://github.com/pypa/virtualenv/issues/1896
"""
from virtualenv.config.cli.parser import VirtualEnvConfigParser
from virtualenv.run import (ActivationSelector, CreatorSelector,
                            SeederSelector, Session, add_version_flag,
                            get_discover, handle_extra_commands, load_app_data)


def cli_run(args, options=None):
    """Create a virtual environment given some command line interface arguments

    :param args: the command line arguments
    :param options: passing in a ``VirtualEnvOptions`` object allows return of the parsed options
    :return: the session object of the creation (its structure for now is experimental and might change on short notice)
    """
    session = session_via_cli(args, options)
    with session:
        session.run()
    return session


# noinspection PyProtectedMember
def session_via_cli(args, options=None):
    parser, elements = build_parser(args, options)
    options = parser.parse_args(args)
    creator, seeder, activators = tuple(e.create(options) for e in elements)  # create types
    session = Session(options.verbosity, options.app_data, parser._interpreter, creator, seeder, activators)
    return session


# noinspection PyProtectedMember
def build_parser(args=None, options=None):
    parser = VirtualEnvConfigParser(options)
    add_version_flag(parser)
    parser.add_argument(
        "--with-traceback",
        dest="with_traceback",
        action="store_true",
        default=False,
        help="on failure also display the stacktrace internals of virtualenv",
    )
    options = load_app_data(args, parser, options)
    handle_extra_commands(options)

    discover = get_discover(parser, args)
    parser._interpreter = interpreter = discover.interpreter
    if interpreter is None:
        raise RuntimeError("failed to find interpreter for {}".format(discover))
    elements = [
        CreatorSelector(interpreter, parser),
        SeederSelector(interpreter, parser),
        ActivationSelector(interpreter, parser),
    ]
    options, _ = parser.parse_known_args(args)
    for element in elements:
        element.handle_selected_arg_parse(options)
    parser.enable_help()
    return parser, elements
