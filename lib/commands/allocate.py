import argparse
import shutil

def AllocateAction( stck, namespace):

    stck.allocate_interface()

def add_allocate_parser(subparsers):
    parser_allocate = subparsers.add_parser(
            'allocate',
            help='Allocate data based on following codes by using \'summary.csv\'.'
        )

    parser_allocate.set_defaults(func=AllocateAction)
