def AnalyzeAction( stck, namespace):
    opt = vars(namespace)
    if opt['withbatch']: opt['checkconf']=True
    stck.analyze_interface(**opt)

def add_analyze_parser(subparsers):
    parser_analyze = subparsers.add_parser(
            'analyze',
            help='Generate data as Multi-Stem with Branch for analysis.'
        )

    parser_analyze.add_argument(
        '-c', '--check-config',
        action='store_true',
        help='Check if the analyconf settings are correct.', dest='checkconf'
    )

    parser_analyze.add_argument(
        '-C', '--check-with-batch',
        action='store_true',
        help='Check config with batch process.', dest='withbatch'
    )

    parser_analyze.set_defaults(func=AnalyzeAction)
