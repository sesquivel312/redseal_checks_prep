import csv
import argparse

def get_args():
    """
    get cli arguments
    :return: args
    """
    p = argparse.ArgumentParser()
    p.add_argument('--source-dir', help='fully qualified directory containing tsv files')
    p.add_argument('--output-dir', help='fully qualified directory to deposit output files, defaults to --source-dir if provided')
    p.add_argument('--column-config-file', help='name of yaml file defining columsn to add', default=None)

    return p.parse_args()


