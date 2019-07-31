# Getting the module responsible for reading csvs and excels
import pandas
import pandas_profiling
import numpy as np
import argparse
import inspect

# The function that will transform the file


def treat_transform_generate(in_file, out_file, report_metrics=None, report_column=None, group_column=None, 
                            generate_report=False, treat_text=False, remove_constant=False):

    def treat_string_data(df):
        # Removing spaces and double from headers
        df.columns = df.columns.str.strip().str.replace('  ', ' ')
        # Removing spaces and replacing duplicate spaces for single spaces.
        # Text columns are considere of type "object" that's why the if val.dtype == object
        return df.apply(lambda val: val.str.strip().str.replace('  ', ' ').str.upper() if val.dtype == object else val)

    def separate_important_values(df):
        # Getting the column values
        headers = df.columns.values
        const_columns = {header: df[header].unique(
        ) for header in headers if len(df[header].unique()) <= 1}
        good_columns = [header for header in headers if len(
            df[header].unique()) > 1]
        return const_columns, good_columns

    if in_file.split('.')[-1] == 'csv':
        df_file = pandas.read_csv(in_file)
        out_html = in_file.replace('.csv', 'profile.html')
    elif in_file.split('.')[-1].startswith('xls'):
        df_file = pandas.read_excel(in_file)
        out_html = in_file.replace('.xls', 'profile.html')
    else:
        raise Exception('File type not implemented yet.')

    # Generate profile
    if generate_report:
        print('Generating report')
        profile = df_file.profile_report(title='Material Data Profile')
        profile.to_file('./%s' % out_html)

    # Treating the text values
    if treat_text:
        print('Treating Text')
        df_file = treat_string_data(df_file)

    # Removing unvalued data

    if remove_constant:
        print('Removing constant values')
        const_columns, good_columns = separate_important_values(df_file)
        df_file = df_file[good_columns]
        print('Removed columns %s' %(','.join([str(key) for key in const_columns.keys()])))


    # Creating a report excel output file
    writer = pandas.ExcelWriter(out_file)
    df_file.to_excel(writer, sheet_name='data')
    # Grouping data and generating a report
    if report_metrics is not None and report_column is not None and group_column is not None:
        print('Generating Metrics')
        df_report = df_consumer_sample[[group_column, report_column]].groupby(
            group_column).agg({report_column: report_metrics.split(',')})

        df_report.to_excel(writer, sheet_name='report')


# in_file = r'C:\Users\lpllour\project\aGame\DataFrame\material_master.csv'
# out_file = "./material_treated.xlsx"
# obj = {'remove_constant':True,'generate_report':False,'treat_text':True}
# treat_transform_generate(in_file,out_file,**obj)

parser = argparse.ArgumentParser()
parser.add_argument('--in_file')
parser.add_argument('--out_file')
parser.add_argument('--report_metrics',nargs='?',type=str)
parser.add_argument('--report_column',nargs='?',type=str)
parser.add_argument('--group_column',nargs='?',type=str)
parser.add_argument('--generate_report',nargs='?',type=bool)
parser.add_argument('--treat_text',nargs='?',type=bool)
parser.add_argument('--remove_constant',nargs='?',type=bool)
args = parser.parse_args()
treat_transform_generate(**vars(args))