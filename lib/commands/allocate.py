import argparse
import shutil

def AllocateAction( sm, namespace):
    if not sm.stock_filepath('summary.csv').exists():
        print('Error: summary.csv has not exists.')
        return

    summary, summary_path, date_str = sm.allocate_init()
    flist = sm.allocate( summary )

    if flist:
        print('Failure codes: {0}'.format(flist))

    if namespace.advance: sm.get_markeddays()._day_advance()

    logpath = sm.stock_filepath( 'log', date_str.replace('-','') )
    shutil.move(summary_path, logpath)

    print('Allocate this dataframe:\n{0}'.format(summary))

def add_allocate_parser(subparsers):
    parser_allocate = subparsers.add_parser(
            'allocate',
            help='allocate data based on following codes by using \'summary.csv\'.'
        )
    parser_allocate.set_defaults(func=AllocateAction)

    parser_allocate.add_argument(
            '--no-advance', action='store_false',
            help='Not advance next update day.', dest='advance'
        )
