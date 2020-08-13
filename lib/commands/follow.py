import argparse

def FollowAction( stck, namespace):

    stck.follow_interface(**vars(namespace))

def add_follow_parser( subparsers ):
    parser_follow = subparsers.add_parser(
            'follow', 
            help='Control the following list.As default, deploy the \'prepare/\' and follow the codes with given codes.'
        )

    parser_follow.add_argument(
            'codes', nargs='*', type=int,
            metavar='CODE'
        )

    parser_follow.add_argument(
            '-d', '--defollow', 
            action='store_true', 
            help='Change mode to defollow.Removes the given codes from following list.', dest='defollow'
        )

    parser_follow.add_argument(
            '-i', '--immediate',
            action='store_false',
            help='Ignore the \'prepare\'/ directory, add only given codes into following list.', dest='deploy'
        )

    parser_follow.add_argument(
            '-f', '--force', action='store_true',
            help='Forcibly execute follow process.', dest='force'
        )

    parser_follow.add_argument(
            '-c', '--clutter',
            action='store_false',
            help='Leave following list in disorder after process.', dest='sort'
        )

    parser_follow.add_argument(
            '--rename', type=str, default='',
            action='store', 
            help='This depend on defollow option. Stocker renames \'stock.csv\' to given string.',
            dest='renames'
        )

    parser_follow.set_defaults(func=FollowAction) 
