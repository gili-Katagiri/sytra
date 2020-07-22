import argparse

class SetSpecFollow(argparse.Action):
    def __call__( self, parser, namespace, values, option_string=None):
        namespace.funcstr='spec'
        setattr(namespace, self.dest, values)

class SetDefollow(argparse.Action):
    def __call__( self, parser, namespace, values, option_string=None):
        namespace.funcstr='defl'
        setattr(namespace, self.dest, values)

def FollowAction( sm, namespace):

    defollow = False
    
    if namespace.funcstr=='init':
        codes = sm.follow_init()
    elif namespace.funcstr=='spec':
        codes = namespace.fcodes
    elif namespace.funcstr=='defl':
        defollow = True
        codes = namespace.dcodes
    else:
        raise Exception('Unexpected Error has occurred!')

    flist = sm.itr_follow( codes, defollow=defollow)
    if flist: # flist is not empty
        print("Failure codes: {0}".format(flist))

    if namespace.mkbase:
        sm.make_summarybase()

def add_follow_parser( subparsers ):
    parser_follow = subparsers.add_parser(
            'follow',
            help='add the codes to follows.'
        )
    parser_follow.set_defaults(funcstr='init')

    parser_follow.add_argument(
            '-s', '--specific',
            action=SetSpecFollow, default=argparse.SUPPRESS,
            nargs='+', type=int, 
            help='Specify the stock code to follow.', metavar='CODE', dest='fcodes'
        )

    parser_follow.add_argument(
            '-d', '--defollow',
            action=SetDefollow, default=argparse.SUPPRESS,
            nargs='+', type=int,
            help='Removes the given following code.', metavar='CODE', dest='dcodes'
        )

    parser_follow.add_argument(
            '--no-make', action='store_false', 
            help='Do not create summary_base.csv after follow.', dest='mkbase'
        )

    parser_follow.set_defaults( func=FollowAction) 
