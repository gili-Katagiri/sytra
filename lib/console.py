import argparse
from commands.follow import add_follow_parser
from commands.allocate import add_allocate_parser

from stocker import Stocker

def add_rootoption(rootparser, STOCK_ROOT):

    rootparser.add_argument(
            '--debug', action='store_true',
            help='Input argument parse test for develop.'
        )

    rootparser.add_argument(
            '--no-create', action='store_false',
            help='Do not create summary_base.csv after process.', dest='create'
        )

    rootparser.add_argument(
            '--stock-root', action='store', default=STOCK_ROOT, type=str,
            help='Process execute as stock root directory is given path.',
            dest='rootpath', metavar='STOCKROOT'
        )


def add_subcommands(subparsers):
    add_allocate_parser(subparsers)
    add_follow_parser(subparsers)

def run(root_parser):

    namespace = root_parser.parse_args()
    stck = Stocker(namespace.rootpath)

    if namespace.debug:
        print(stck.get_follows_tuple(), stck.get_lateststr())
        print(namespace)
        return

    if hasattr(namespace, 'func'): namespace.func( stck, namespace)
    
    if namespace.create: stck.create_sbase()
    stck.dump()


def main(STOCK_ROOT):

    # sytra command
    root_parser = argparse.ArgumentParser(
            description='Some useful tools for Analysis and SystemTrade.',
        )

    add_rootoption(root_parser, STOCK_ROOT)

    subparsers = root_parser.add_subparsers(
            title='AVAILABLE SUB-COMMANDS',
            metavar='COMMAND'
        )
    
    add_subcommands(subparsers)

    run(root_parser)
