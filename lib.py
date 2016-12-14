import csv
import argparse
import os
import os.path
import tempfile
import shutil

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


def get_files(source_dir):

    contents = os.listdir(source_dir)

    return [os.path.join(source_dir, item) for item in contents if os.path.isfile(os.path.join(source_dir, item))]


def process_tsv_file(tsv_file_name, column_defs=None, output_dir=''):

    # todo in future add capability to read in a yaml file defining what columns to add and where to insert them
    # the add columns list includes the location and names of the columns to be inserted in a tuple of the form
    # (position, colname).  position = what column number the new column should be - i.e. where to insert it.
    # for columns to be appended the location is given by a string of the form: +n, where n is the position
    # on the right to add, e.g. '+1' means add this immediately after the original rightmost column, etc.

    # add_columns = [(1,'ew_id'),('+1','ew_reviewer'),('+2','ew_review_date'),('+3','ew_disposition')]

    tmp_file = tempfile.NamedTemporaryFile()
    tmp_csv = csv.writer(tmp_file)

    f = open(tsv_file_name,'rb')  # open the passed in file
    csv_src_reader = csv.reader(f, dialect='excel-tab')  # and convert it to a csv reader (tsv here)

    # read the next line in the tsv file
        # split line on tabs
        # if this is the first line - handle headers
        # otherwise handle the data lines, which means adding the incrementing index value only to the first column

    counter = 0
    for row in csv_src_reader:

        new_row = []

        if not counter:  # header row
            new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
            new_row.insert('ew_id')  # prepend the counter value (it's the ew_id of this row)
            new_row.append(['ew_reviewer', 'ew_review_date', 'ew_disposition'])
        else:
            new_row.extend(row)  #put the existing rows in todo modify to handle arbitrary inserts
            new_row.insert(counter)  # prepend the counter value (it's the ew_id of this row)
            new_row.append(['','',''])

        tmp_csv.write(new_row)

        counter += 1

    tmp_file.flush()
    outfile_name = os.path.split()[1]
    shutil.copy(tmp_file, os.path.join(output_dir,outfile_name))
    tmp_file.close()