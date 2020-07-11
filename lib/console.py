import argparse
from stocker import StockManeger
#from actions import AllocateAction, FollowAction, MkbaseAction

def AllocateAction(sm: StockManeger, args: argparse.Namespace):
    sm.allocate()

def FollowAction(sm: StockManeger, args: argparse.Namespace):
    for code in args.codes:
        print('{0}... '.format(code), end='')
        try:
            sm.follow_stock( code )
        except Exception as e:
            print('Failed!', end='-- ')
            print(e)
        else:
            print('Complete!')
        

def MkbaseAction(sm: StockManeger, args: argparse.Namespace):
   sm.make_summarybase() 

def main():

    # sytra command
    root_parser = argparse.ArgumentParser(
            description='Some useful tools for Analysis and SystemTrade.',
        )
    subparsers = root_parser.add_subparsers(
            title='AVAILABLE SUB-COMMANDS',
            dest='com',
            metavar='COMMAND'
        )


    # subcommads
    # allocate
    parser_allocate = subparsers.add_parser(
            'allocate',
            help='allocate data based on following codes by using \'summary.csv\'.'
        )
    parser_allocate.set_defaults(func=AllocateAction)
    
    # follow
    parser_follow = subparsers.add_parser(
            'follow',
            help='add the codes given by agguments to following list.'
        )
    parser_follow.add_argument(
            'codes', type=int,
            nargs='+',help='codes add new',metavar='CODE'
        )
    parser_follow.set_defaults(func=FollowAction)

    # mkbase (make summary base)
    parser_mkbase = subparsers.add_parser(
            'mkbase',
            help='make summary_base.csv based on following list.'
        )
    parser_mkbase.set_defaults(func=MkbaseAction)

    # load StockManeger
    sm = StockManeger()

    args = root_parser.parse_args()
    args.func(sm, args)

    sm._dump()
