import pandas as pd
import numpy as np
from pathlib import Path
import logging
import re

class _FileObj:
    def __init__(self, path_obj, dataframe=None, dataframe_name=None, 
    colname_chars_replace_underscore="", colname_chars_replace_custom={},
    colname_chars_remove="", **kwargs):
        """
        Create a FileObj instance that has a single attribute, df which is a pandas dataframe
        supports xls, xlsx, csv, tsv files. Only the first worksheet in an Excel workbook
        with multiple sheets will be read.
        param: use any keyword parameters valid in pandas.read_csv()
        parameter: dataframe - default None; a pandas DataFrame object to be profiled
        parameter: dataframe_name - default None; a unique string for the DataFrame, will be used as the
            filename for the dataframe profile ex. DataFrame_Name_profile.xlsx
        parameter: colname_chars_replace_underscore - string of invalid characters to be replaced with an underscore
        parameter: colname_chars_replace_custom - dict of characters and their replacement value
        parameter: colname_chars_remove - string of characters to be removed
        """
        # Initialize logging
        self.log = logging.getLogger()
        self.log.handlers = []
        self.log.setLevel(logging.INFO)
        log_fmt = logging.Formatter('%(levelname)s: %(asctime)s %(thread)d %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        screen = logging.StreamHandler()
        screen.setFormatter(log_fmt)
        self.log.addHandler(screen)
        
        self.df = None
        # df_name must be unique to create unique output filenames
        self.df_name = None

        # update default replace with underscore characters with user-defined characters
        escape_string = r'\/()[]{},.!?:;-^~`' + colname_chars_replace_underscore
        self.colname_chars_replace_underscore = re.escape(escape_string) + r'\s+'
        colname_chars_replace_custom_default = {'#': 'num', '$': 'usd', '%': 'pct', '&': 'and', '+': 'plus', 
        '*': 'times', '=': 'equals', '<': 'lt', '>': 'gt', '@': 'at', '|': 'or'}
        
        # update colname_chars_replace_custom with user-defined dict
        colname_chars_replace_custom_default.update(colname_chars_replace_custom)

        # create new colname chars replace dict with properly escaped values as needed
        self.colname_chars_replace_custom = {}
        for key, value in colname_chars_replace_custom_default.items():
            self.colname_chars_replace_custom[re.escape(key)] = value

        # set attribute for characters to be removed
        self.colname_chars_remove = colname_chars_remove
        
        # log.info('Creating FileObj')
        if path_obj == 'dataframe':
            if dataframe is None:
                raise Exception('No dataframe was assigned to the "dataframe=" argument.')
            else:
                self.df = dataframe
                if dataframe_name is None:
                    raise Exception('If profiling a dataframe, argument dataframe_name must be a unique string')
                else:
                    self.df_name = dataframe_name
        elif path_obj.is_file():
            if path_obj.suffix in('.xls', '.xlsx'):
                try:
                    self.df = pd.read_excel(path_obj, **kwargs)
                except Exception as error:
                    self.log.exception(error)

            elif path_obj.suffix in ['.csv', '.tsv', '.txt']:
                try:
                    self.df = pd.read_csv(path_obj, **kwargs)
                except Exception as error:
                    self.log.exception(error)
        else:
            raise Exception(f'{path_obj.name} is not a file.  Please use a valid text or excel file')
            
        if self.df is None:
            self.log.warning(f'{path_obj.name} was not parsed, please check file format and kwargs')
        else:
            # log.info('Created FileObj')
            self.id_cols = []
            self.dim_cols = []
            self.path_obj = path_obj
        
        
    def get_columns(self):
        """
        Not currently used as the column list is contained in the more comprehensive Data Types output 
        returns: dataframe of columns from file
        """
        self.log.info('Retrieving Columns')
        return pd.DataFrame(self.df.columns, columns=['Columns'])
    
    
    def get_data_types(self):
        """
        method that sets values for self.id_cols and self.dim_cols, additionally the 
        returns: dataframe of column names and their data types
        """
        self.log.info('Retrieving Data Types')
                
        df = pd.DataFrame(self.df.dtypes, columns=['Data Type'])
        df.index.name = 'Column Name'
        df = df.reset_index()

        df['Clean Column Name'] = self.clean_column_names(df['Column Name'])
            
        # identify ID columns
        id_col_pat = re.compile(r"(?:^id$|^ID$)|(?:[-_\s]+id|[-_\s]+ID$)|(?:[a-z]+ID$)|(?:[-_\s]+code)",)
        df['Potential ID Column'] = df['Column Name'].apply(lambda x: True if re.search(id_col_pat, x) else None)
        # set FileObj attribute "ID Columns", referenced in dim_cols below
        self.id_cols = df.loc[df['Potential ID Column'] == True, 'Column Name'].tolist()
        
        # identify the proper data type
        for col in self.df.columns:
            # set string representation of pandas series dtype
            col_dtype = str(self.df[col].dtype)

            if self.df[col].count() > 0:
                if col_dtype in ['object', 'bool'] or 'datetime' in col_dtype:
                    col_values_precision_series = self.df[col].astype('str').str.len()
                    max_precision_value = max(col_values_precision_series)
                    min_precision_value = min(col_values_precision_series)
                elif col_dtype in ['int', 'int64', 'int32']:
                    max_precision_value = self.df[col].max()
                    min_precision_value = self.df[col].min()
                elif col_dtype in ['float', 'float64', 'float32']:
                    col_values_precision_series = self.df[col].astype('str')
                    col_values_precision_df = col_values_precision_series.str.split('.', expand=True)
                    # precision
                    min_precision_value = max(col_values_precision_df[0].str.len() + col_values_precision_df[1].str.len())
                    # scale
                    max_precision_value = max(col_values_precision_df[1].str.len())
                    # check if the Data Type could be int
                    try:
                        if col_values_precision_df[1].fillna('0').astype('int64').sum() == 0:
                            df.loc[df['Column Name'] == col, 'Data Type'] = 'decimal or integer'
                    except ValueError:
                        # pass because this should catch INT overflow that has no negative affect on output
                        pass
                else:
                    min_precision_value = 'dtype not supported'
                    max_precision_value = 'dtype not supported'
            else:
                min_precision_value = 0
                max_precision_value = 0
                df.loc[df['Column Name'] == col, 'Data Type'] = 'N/A'
                
            df.loc[df['Column Name'] == col, 'Min Length|Value/Precision'] = min_precision_value
            df.loc[df['Column Name'] == col, 'Max Length|Value/Scale'] = max_precision_value

            # check for NULL values
            if sum(self.df[col].isna()) > 0:
                df.loc[df['Column Name'] == col, 'Nullable'] = True

            # set FileObj attribute "Dim Columns"
            if self.df[col].dtype == 'object' and col not in self.id_cols:
                self.dim_cols.append(col)

        # replace obscure data type names with clear names
        replace_dict = {'datetime64[ns]': 'date/datetime', 'object':'text', 'int': 'integer',
        'int8': 'integer', 'int32': 'integer', 'int64': 'integer', 'float': 'decimal', 
        'float32': 'decimal', 'float64': 'decimal',}
        df['Data Type'] = df['Data Type'].replace(to_replace=replace_dict)
        
        return df[['Column Name', 'Clean Column Name', 'Data Type', 'Min Length|Value/Precision', 
            'Max Length|Value/Scale', 'Potential ID Column', 'Nullable']]


    def clean_column_names(self, colname_series):
        """
        Take a pandas series of column names and apply cleansing steps
        Returns: pandas series of cleaned column names
        """

        # remove unwanted characters
        if self.colname_chars_remove != "":
            colname_series_clean = colname_series_clean.str.replace(f'[{self.colname_chars_remove}]+', '', regex=True)

        # Replace unacceptable characters in column names with undercores
        colname_series_clean = colname_series.str.replace(f'[{self.colname_chars_replace_underscore}]+', '_', regex=True)
        # replace chars with custom values
        for char, replacement in self.colname_chars_replace_custom.items():
            colname_series_clean = colname_series_clean.str.replace(f'{char}', f'_{replacement}_', regex=True)

        # replace multiple underscores with a single underscore
        colname_series_clean = colname_series_clean.str.replace(r'_+', '_', regex=True)
        # remove leading and trailing underscores
        colname_series_clean = colname_series_clean.str.strip('_')

        # insert underscore for column names that might be IDs and use camel case
        colname_series_clean = colname_series_clean.apply(lambda x: _modify_camel_case_id_names(x))

        # lower case the clean column name
        colname_series_clean = colname_series_clean.str.lower()

        return colname_series_clean
    
    
    def get_text_distinct_values(self):
        """
        returns: dataframe of column names and series of distinct values
        """
        self.log.info('Retrieving Text Value Distribution')
        results_dict = {}
        pandas_numeric_dtype_list = ['int', 'int64', 'int32', 'float', 'float64', 'float32']
        for col in self.df.columns:
            if self.df[col].dtype in pandas_numeric_dtype_list and col not in self.id_cols:
                results_dict[col] = pd.DataFrame(['NA for numeric columns'], columns=[col])
            else:
                df = pd.DataFrame(self.df[col].value_counts())
                df_null = pd.DataFrame({col: len(self.df[self.df[col].isna()])}, index=['NULL'])
                df = pd.concat([df_null, df], sort=False)
                df.index.name = col
                df.rename(index=str, columns={col: f'{col}_counts'}, inplace=True)
                results_dict[col] = df.reset_index()

        distinct_text_values_df = pd.concat(results_dict.values(), axis=1, join='outer', sort=True)

        distinct_text_values_df = replace_xml_illegal_characters(distinct_text_values_df)
        
        return distinct_text_values_df
    
    
    def get_numeric_value_distribution(self):
        """
        returns: dataframe of descriptive stats for numeric columns
        """
        self.log.info('Retrieving Numeric Value Distribution')
        df = pd.DataFrame(self.df.describe()).reset_index()
        df.rename(index=str, columns={'index': 'Stat'}, inplace=True)
        return df
    
    
    def get_primary_keys(self):
        """
        analyzes dataframe to see the maximum number of non-metric columns that can be part of a primary key
        this is done by checking for columns that when grouped, retain the same number of distinct records as the
        oringinal dataframe
        returns: dataframe of suggested primary key(s) and dataframe of potential ID fields"""
        self.log.info('Looking for Potential Primary Key(s)')

        pk_1 = []
        pk_2 = []
        df_len = 0
        id_cols = self.id_cols.copy()
        dim_cols = self.dim_cols.copy()
        for col in id_cols + dim_cols:
            new_len = len(self.df.groupby(pk_1 + [col], sort=False).count())
            if new_len > df_len:
                df_len = new_len
                pk_1.append(col)
            else:
                pass
            
        id_cols.reverse()
        dim_cols.reverse()
        df_len = 0
        for col in id_cols + dim_cols:
            if len(self.df.groupby(pk_2 + [col], sort=False).count()) < df_len:
                pk_2.append(col)
            else:
                pass
            
        return pd.DataFrame({'Column Name': list(set(pk_1 + pk_2))})

def _modify_camel_case_id_names(x):
    results = re.search(r'([a-z]+ID$)', x)
    if results:
        for group in results.groups():
            if group:
                return x.replace(group, group[:-2] + '_ID')
    else:
        return x


def replace_xml_illegal_characters(df):
    """
    replace characters that throw ILLEGAL_CHARACTER_ERROR in openpyxl 
    when writing to XLS(X) formats, found regex pattern in openpyxl source here: 
    https://openpyxl.readthedocs.io/en/stable/_modules/openpyxl/cell/cell.html
    """
    ILLEGAL_CHARACTERS_RE = re.compile(r'[\000-\010]|[\013-\014]|[\016-\037]')

    return df.replace(to_replace=ILLEGAL_CHARACTERS_RE, value='~', regex=True)
