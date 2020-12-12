def add_init_parser(subparsers):
    parser_init = subparsers.add_parser(
            'init',
            help='Sytra execute system initial process.'
        )

    parser_init.add_argument(
            '--root-directory', default='', type=str,
            help='Set STOCK ROOT directory by given path.',
            dest='rootdir'
        )

    parser_init.add_argument(
            '--latest-update', default='', type=str,
            help='Set latest update day from string. Format: \'YYYY-mm-dd\'.',
            dest='daystr'
        )

    parser_init.add_argument(
            '--follows-list', default=[], nargs='+', type=int,
            help='Add given list to follows as already following list.',
            dest='follows'
        )
