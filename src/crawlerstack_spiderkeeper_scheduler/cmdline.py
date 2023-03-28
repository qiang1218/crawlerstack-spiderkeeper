# encoding: utf-8
"""
Cmdline.
"""
import asyncio

import click

from crawlerstack_spiderkeeper_scheduler import __version__
from crawlerstack_spiderkeeper_scheduler.config import settings
from crawlerstack_spiderkeeper_scheduler.manage import SpiderKeeperScheduler


@click.group(invoke_without_command=True)
@click.pass_context
@click.option('-V', '--version', is_flag=True, help='Show version and exit.')
@click.option('-v', '--verbose', is_flag=True, help='Get detailed output')
def main(ctx, version, verbose):
    """Main cmd."""
    if version:
        click.echo(__version__)
    elif verbose:
        settings.set('VERBOSE', verbose)
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.option('-h', '--host', default='0.0.0.0', show_default=True, help='Host IP')
@click.option('-p', '--port', default=8081, show_default=True, help='Port')
@click.option('--level', help='Log level')
@click.option('--file', help='logfile')
def api(host, port, level, file):
    """Api cmd."""
    kwargs = {
        'LOGLEVEL': level,
        'LOGFILE': file,
        'HOST': host,
        'PORT': port,
    }
    for name, value in kwargs.items():
        if value:
            settings.set(name, value)
    # 程序调度入口
    asyncio.run(SpiderKeeperScheduler(settings).run())


if __name__ == '__main__':
    main()  # pylint: disable=no-value-for-parameter
