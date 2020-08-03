import argparse
from stocker import StockManeger
from commands.follow import add_follow_parser
from commands.allocate import add_allocate_parser
#from actions import AllocateAction, FollowAction, MkbaseAction

def add_rootoption(rootparser):
    rootparser.add_argument(
            '--no-make', action='store_false',
            help='Do not create summary_base.csv after follow.', dest='mkbase'
        )

    rootparser.add_argument(
            '--no-dump', action='store_false',
            help='Do not save any modification for the params.', dest='dump'
        )
    
    rootparser.add_argument(
            '--debug', action='store_true',
            help='Input argument parse test'
        )

def add_subcommands(subparsers):
    add_allocate_parser(subparsers)
    add_follow_parser(subparsers)

def run(root_parser):
    sm = StockManeger()

    namespace = root_parser.parse_args()

    if namespace.debug:
        print(sm)
        print(namespace)
        return

    if hasattr(namespace, 'func'): namespace.func( sm, namespace)
    
    if namespace.mkbase: sm.make_summarybase()
    if namespace.dump: sm._dump()


def main():

    # sytra command
    root_parser = argparse.ArgumentParser(
            description='Some useful tools for Analysis and SystemTrade.',
        )

    add_rootoption(root_parser)

    subparsers = root_parser.add_subparsers(
            title='AVAILABLE SUB-COMMANDS',
            metavar='COMMAND'
        )
    
    add_subcommands(subparsers)

    run(root_parser)
