"""
script to add columns the redseal rule usage/check tsv-files necessary for completing the semiannual FW rule review

You specify a directory containing the tsv files and a directory in which to place the altered files generated by
this script.  You can also specify a yaml file containing the columns to be added to the files.  This script will
add certain fields by default if no yaml file is specified on the command line.

options are:
  --source-dir
  --output-dir
  --column-config-file
  --device-name
  --reviewer
  --review-date
  --ticket-ref
"""

# todo possibly process unused check files separately - remove packet counter columns & extract unused lines only
# the above would require a change to the procedure (which currently keeps all lines)

import yaml
import pprint as pp

import lib

args = lib.get_args()  # get command line args

file_list = lib.get_files(args.source_dir, args.device_name)  # list of the tsv files to process

column_defs = None
if args.column_config_file:  # if provided parse column config file to a dict (doesn't do anything yet)
    f = open(args.column_config_file)
    # todo currently not used, future - add ability to specify column names and where to insert them
    column_defs = yaml.load(f)

for fname in file_list:
    lib.process_tsv_file(fname, output_dir=args.output_dir, reviewer=args.reviewer, review_date=args.review_date,
                         ticket_ref=args.ticket_ref)