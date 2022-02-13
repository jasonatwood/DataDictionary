import pandas as pd
from pathlib import Path
import logging
import re
from .profiler import _FileObj


class ProfileData():
    """
    Create a ProfileData object
    """
    def __init__(self):
        # Initialize logging
        self.log = logging.getLogger()
        self.log.handlers = []
        self.log.setLevel(logging.INFO)
        log_fmt = logging.Formatter('%(levelname)s: %(asctime)s %(thread)d %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        screen = logging.StreamHandler()
        screen.setFormatter(log_fmt)
        self.log.addHandler(screen)
        self.source_filepath = None
        self.source_dir = None
        self.destination_dir = None
        

    def process_file(self, file_path, dest_dir, **kwargs):
        """
        Profile a single file
        parameter: file_path - path to the file to be profiled
        parameter: dest_dir - directory for profile to be written
        parameter: colname_chars_replace_underscore - string of invalid characters to be replaced with an underscore
        parameter: colname_chars_replace_custom - dict of characters and their replacement value
        parameter: colname_chars_remove - string of characters to be removed
        parameter: sample_data - None or integer > 0; number of records to include in a sample_data sheet in output, 
                    default is 500, disable with sample_data=None
        kwargs: pandas keyword arguments to read text files
        """
        self.source_filepath = Path(file_path)
        self.destination_dir = Path(dest_dir)
        self.log.info(f'Processing {self.source_filepath.name}')
        fo = _FileObj(self.source_filepath, **kwargs)
        if fo.df is None:
            pass
        else:
            self._create_profile(fo)

    
    def process_directory(self, source_dir, dest_dir, contain=None, not_contain=None, **kwargs):
        """
        Profile all files in the source directory depending on use of contain and not_contain kwargs
        parameter: source_dir - directory to scan for files to profile
        parameter: dest_dir - directory for profile to be written
        parameter: contain - text string used to search filename, if found the file is profiled
        parameter: not_contain - text string used to search filename, if found the file is not profiled
        parameter: colname_chars_replace_underscore - string of invalid characters to be replaced with an underscore
        parameter: colname_chars_replace_custom - dict of characters and their replacement value
        parameter: colname_chars_remove - string of characters to be removed
        parameter: sample_data - None or integer > 0; number of records to include in a sample_data sheet in output, 
                    default is 500, disable with sample_data=None
        kwargs: pandas keyword arguments to read text files
        """
        # add logic to process all files
        self.source_dir = Path(source_dir)
        self.destination_dir = Path(dest_dir)
        
        if contain is not None and not_contain is not None:
            raise Exception('Cannot use both "contain" and "not_contain" to process a directory')
        elif contain is not None and not isinstance(contain, str):
            raise Exception(f'"contain" expects a string {type(contain)} used.')
        elif not_contain is not None and not isinstance(not_contain, str):
            raise Exception(f'"not_contain" expects a string {type(not_contain)} used.')
        self.contain = contain
        self.not_contain = not_contain
        
        for item in self.source_dir.iterdir():
            if '~$' in item.stem[:2] or item.name.endswith('_profile.xlsx'):
                continue
            if item.is_file() and item.suffix != '.lnk':
                if self.contain is not None and re.search(f'{self.contain}', item.name):
                    self._process_file(item, **kwargs)
                elif self.not_contain is not None and not re.search(f'{self.not_contain}', item.name):
                    self._process_file(item, **kwargs)
                elif self.contain is None and self.not_contain is None:
                    self._process_file(item, **kwargs)

        
    def process_dataframe(self, dest_dir, dataframe=None, dataframe_name=None, **kwargs):
        """
        Profile a pandas dataframe
        parameter: dest_dir - directory for profile to be written        
        parameter: dataframe - a Pandas dataframe
        parameter: dataframe_name - text string used to name the profile created
        parameter: colname_chars_replace_underscore - string of invalid characters to be replaced with an underscore
        parameter: colname_chars_replace_custom - dict of characters and their replacement value
        parameter: colname_chars_remove - string of characters to be removed
        parameter: sample_data - None or integer > 0; number of records to include in a sample_data sheet in output, 
                    default is 500, disable with sample_data=None
        """
        self.destination_dir = Path(dest_dir)
        fo = _FileObj('dataframe', dataframe=dataframe, dataframe_name=dataframe_name)
        self._create_profile(fo)


    def _process_file(self, path_obj, **kwargs):
        self.log.info(f'Processing {path_obj.name}')
        fo = _FileObj(path_obj, **kwargs)
        if fo.df is None:
            pass
        else:
            self._create_profile(fo)


    def _create_profile(self, fo):
        self.log.info('Creating Output File')
        if fo.df_name is not None:
            results_file = self.destination_dir / f'{fo.df_name}_profile.xlsx'
        else:
            results_file = self.destination_dir / f'{fo.path_obj.stem}_profile.xlsx'
        with pd.ExcelWriter(results_file) as excel_writer:
            fo.get_data_types().to_excel(excel_writer, sheet_name='Data_Types', index=False)
            fo.get_text_distinct_values().to_excel(excel_writer, sheet_name='Text_Value_Dist', index=False)
            fo.get_numeric_value_distribution().to_excel(excel_writer, sheet_name='Numeric_Value_Dist', index=False)
            fo.get_primary_keys().to_excel(excel_writer, sheet_name='Potential_Primary_Keys', index=False)
            if fo.sample_data is not None:
                fo.create_sample().to_excel(excel_writer, sheet_name='Sample_Data', index=False)
        self.log.info(f'Output File {results_file} Complete')

        
