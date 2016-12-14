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
    p.add_argument('--output-dir', help='fully qualified directory to deposit output files, '
                                        'defaults to --source-dir if provided')
    p.add_argument('--device-name', help='name of device to process', default=None)
    p.add_argument('--reviewer', help='name of person conducting review', default='')
    p.add_argument('--review-date', help='date to apply to review column in the format: yyyy-mm-dd', default='')
    p.add_argument('--ticket-ref', help='service desk ticket number to apply to disposition column', default='')
    p.add_argument('--column-config-file', help='name of yaml file defining columsn to add', default=None)

    return p.parse_args()


def get_files(source_dir, device_name):
    """
    return the list of files in the source directory

    If device_name is None, return all the files in source_dir.  Otherwise, return only those files
    associated with device_name.  It is assumed the file names are of the form <devname>--<checktype>.tsv, e.g.

       myfirewall--usage.tsv

    the device name may contain dashes - hence the double dash separator.  The <checktype> is one of the redseal
    check types

    :param source_dir: (string) path to location of *.tsv check files
    :param device_name: (string or None) name of device for which to process files or None
    :return:
    """

    contents = os.listdir(source_dir)

    if not device_name:
        return [os.path.join(source_dir, item) for item in contents if os.path.isfile(os.path.join(source_dir, item))]
    else:
        return [os.path.join(source_dir, item) for item in contents if os.path.isfile(os.path.join(source_dir, item))
                and device_name in item]


def get_unique_devices(file_list):  # may not need this?

    udevices = set()

    for fname in file_list:
        devname = fname.split('--')[0]
        udevices.add(devname)

    return udevices


def process_tsv_row(row, line_num, **kwargs):

    new_row = []

    if not line_num:  # header row
        new_row.append('ew_id')  # prepend the counter value (it's the ew_id of this row)
        new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
        new_row.extend(['ew_reviewer', 'ew_review_date', 'ew_disposition'])

    elif kwargs['is_redundant_file']:  # extra checks required here
        if not row[0]:  # check this - it should be the rows w/"Made Redundant By" in column 2
            new_row.append(line_num)  # prepend the counter value (it's the ew_id of this row)
            new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
            new_row.extend(['', '', kwargs['reviewer'], kwargs['review_date'],
                            'Additional Info Required: ' + kwargs['ticket_ref']])
        elif row[0] == '>>':
            new_row.append(line_num)  # prepend the counter value (it's the ew_id of this row)
            new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
            new_row.extend(['', '', kwargs['reviewer'], kwargs['review_date'],
                            'Additional Info Required: ' + kwargs['ticket_ref']])
        else:
            new_row.append(line_num)  # prepend the counter value (it's the ew_id of this row)
            new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
            new_row.extend([kwargs['reviewer'], kwargs['review_date'],
                            'Additional Info Required: ' + kwargs['ticket_ref']])

    else:
        new_row.append(line_num)  # prepend the counter value (it's the ew_id of this row)
        new_row.extend(row)  # put the existing rows in todo modify to handle arbitrary inserts
        new_row.extend([kwargs['reviewer'], kwargs['review_date'],
                        'Additional Info Required: ' + kwargs['ticket_ref']])

    return new_row


def process_tsv_file(fname, output_dir='', **kwargs):

    # todo in future add capability to read in a yaml file defining what columns to add and where to insert them
    # the add columns list includes the location and names of the columns to be inserted in a tuple of the form
    # (position, colname).  position = what column number the new column should be - i.e. where to insert it.
    # for columns to be appended the location is given by a string of the form: +n, where n is the position
    # on the right to add, e.g. '+1' means add this immediately after the original rightmost column, etc.

    # add_columns = [(1,'ew_id'),('+1','ew_reviewer'),('+2','ew_review_date'),('+3','ew_disposition')]

    kwargs['is_redundant_file'] = 'redundant' in fname  # if fname contains 'redundant' then True, else False

    tmp_file = tempfile.TemporaryFile(delete=False)
    tmp_csv = csv.writer(tmp_file, dialect='excel-tab')

    f = open(fname, 'rb')  # open the passed in file
    csv_src_reader = csv.reader(f, dialect='excel-tab')  # and convert it to a csv reader (tsv here)

    # read the next line in the tsv file
        # split line on tabs
        # if this is the first line - handle headers
        # otherwise handle the data lines, which means adding the incrementing index value only to the first column

    line_num = 0
    for row in csv_src_reader:

        new_row = process_tsv_row(row, line_num, **kwargs)
        tmp_csv.writerow(new_row)
        line_num += 1

    tmp_file.flush()
    outfile_name = os.path.split(fname)[1]
    outfile_name = os.path.join(output_dir, outfile_name)
    shutil.copy(tmp_file.name, outfile_name)
    tmp_file.close()
