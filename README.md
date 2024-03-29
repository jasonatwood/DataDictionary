# DataDictionary Overview
In any data environment, the introduction of new data brings questions about the contents. Discovery and documentation is critical and a lot can be learned of a new data set through basic data profiling. This Python package reads data from a file, directory of files, or a Pandas dataframe and creates a standardized output (Excel workbook) that provides insights on each file's contents. The output can provide any data architect, data engineer, business analyst or data analyst with the information they need to make effective and efficient early decisions about the value of and potential issues in a new data set.

The file processor is able to read any text or Excel file that can be opened with Pandas. Any argument that can be passed to pandas.read_csv() or pandas.read_excel() is valid and used to direct the file processor.

[DataDictionary Class and Methods](#datadictionary)

## Get Started

[Install DataDictionary](#installation) 

[Sample Code](#using-datadictionary)

## Components of the Output File
The output is an XLSX Microsoft Excel workbook with information spread across mutliple worksheets. Each bullet corresponds to a worksheet in the output file.

- [Data Types](#data-types)
- [Text Value Distribution](#text-value-distribution)
- [Numeric Value Distribution](#numeric-value-distribution)
- [Potential Primary Keys](#potential-primary-keys)
- [Sample Data](#sample-data)

### Data Types
This worksheet is a great starting point for a data catalogue or data dictionary. At a glance, this report provides:

- The original field name
  - Presented as the name appears in the sample file
- A 'clean' version of the field name
  - These values are optimized for legibility and compatibility with RDBMS standards (See [Column Name Cleanup](#column-name-cleanup))
- The presumed data type
  - Data types are simplified into text, integer, decimal, or N/A (See [Data Type Detection](#data-type-detection))
- The minimum and maximum lengths for text fields
- The minimum and maximum values for integer fields
- The precision and scale for decimal fields
- Potential ID flag
  - Based on the contents of the field name, make a guess to whether or not it's an ID field
- Potential PII flag
  - First, look at the contents of the field name, make a guess to whether or not it contains PII
  - Second, look at the values in the field and make a guess to whether or not the contents contain PII
    - If even a single value in a field is presumed to be PII, the entire field is flagged 
- Nullable flag
  - If one or more values are found to be NULL, set to 1 or True

#### Column Name Cleanup
The cleansing process uses two steps:
1. Remove unwanted characters
2. Replace unwanted characters

When processing a dataframe, file, or directory of files, the output of both steps can be controlled through parameters.
- colname_chars_remove
  - Full customization
- colname_chars_replace_custom
  - Partial customization (see Table 1) 

Target Character(s) | Replacement Character(s) | Affected by Custom Parameter 
--------------------|--------------------------|------------------------------
\\/()[]{},.!?:;\-^~`\\s+ | _ | Yes, characters can be added
\# | num | Yes, replacement can be changed
$ | usd | Yes, replacement can be changed
% | pct | Yes, replacement can be changed
& | and | Yes, replacement can be changed
\| | or | Yes, replacement can be changed
@ | at | Yes, replacement can be changed
\+ | plus | Yes, replacement can be changed
\* | times | Yes, replacement can be changed
= | equals | Yes, replacement can be changed
\< | lt | Yes, replacement can be changed
\> | gt | Yes, replacement can be changed
Custom | Custom | Yes, target and replacement characters can be added

Table 1

#### Data Type Detection
The best source of information for data types from a data source is a physical data model or the DDL used to create the source table. More often than not, that information is either not available or takes a prohibitively long amount of time to obtain from the data owner. This feature is meant to be a helpful suggestion based on the observed records in the sample data. Data types are simplified to avoid prescriptive output (see Table 2).

Data Types in Output |
---------------------|
date/datetime |
decimal |
integer |
decimal or integer** |
text |
N/A* |

Table 2

\* N/A is assigned to fields that contain only NULL values, no data type can be suggested\
\*\* 'decimal or integer' is assigned to fields that may contain integer values in the source file but while processing that file NULL values were detected which Pandas converts to the float data type. Therefore with ambiguous data a loose suggestion is made.

### Text Value Distribution
For each text field, a distribution is appended to this worksheet with the count of NULL values appearing at the top.

### Numeric Value Distribution
The output on this worksheet is from the Pandas DataFrame.describe() method. It shows the distribution of numeric fields and **excludes** potential ID fields.

### Potential Primary Keys
This is one of the less developed features, however can be useful to highlight fields with heterogenous data that may indicate they may be the natural key or part of the natural key for the given sample data.

### Sample Data
This optional sheet takes a number of records from a file and writes them to Sample_Data.

## Get Started
### Installation
```python
pip install datadictionary
```

### Using DataDictionary
```python
import datadictionary
profiler = datadictionary.ProfileData()

# profile a single file
profiler.process_file('./tests/test1.csv', dest_dir='./tests/', colname_chars_remove=r'aeiou')

# profile a directory of files
profiler.process_directory('./tests/', dest_dir='./tests/', contain='test1', not_contain='test2')

# profile a Pandas DataFrame
profiler.process_dataframe(dest_dir='./tests/', dataframe=sample_df, dataframe_name='sample_df')
```
## DataDictionary
class datadictionary.**ProfileData**()\
**process_file**(file_path=*filepath*, dest_dir=*filepath*, **kwargs)\
file_path: path to the file to be profiled\
dest_dir: directory for profile to be written\
**kwargs includes:
- colname_chars_replace_underscore: string of invalid characters to be replaced with an underscore
- colname_chars_replace_custom: dict of characters and their replacement value
- colname_chars_remove: string of characters to be removed
- sample_data: None or integer > 0, default 500; number of records to include in a sample_data sheet in output file. If None is passed, the sheet is omitted from the output file.
- parameter: interpret_date_timestamp - boolean default False, attempt to convert string fields to date or timestamp 
- parameter: interpret_date_timestamp_errors - text default "raise", options are "raise", "ignore", "coerce". "raise" will raise errors on values that cannot be converted, "ignore" will not raise errors and returns the input data, "coerce" will return NaT values when they cannot be converted.
- pandas.read_csv() or pandas.read_excel() arguments

**process_directory**(source_dir=*filepath*, dest_dir=*filepath*, **kwargs)\
source_dir: path to the file to be profiled\
dest_dir: directory for profile to be written\
**kwargs includes:
- colname_chars_replace_underscore: string of invalid characters to be replaced with an underscore
- colname_chars_replace_custom: dict of characters and their replacement value
- colname_chars_remove: string of characters to be removed
- sample_data: None or integer > 0, default 500; number of records to include in a sample_data sheet in output file. If None is passed, the sheet is omitted from the output file.
- parameter: interpret_date_timestamp - boolean default False, attempt to convert string fields to date or timestamp 
- parameter: interpret_date_timestamp_errors - text default "raise", options are "raise", "ignore", "coerce". "raise" will raise errors on values that cannot be converted, "ignore" will not raise errors and returns the input data, "coerce" will return NaT values when they cannot be converted.
- pandas.read_csv() or pandas.read_excel() arguments

**process_dataframe**(dest_dir=*filepath*, dataframe=*pandas DataFrame*, dataframe_name=*string*, **kwargs)\
dest_dir: directory for profile to be written\
**kwargs includes:
- colname_chars_replace_underscore: string of invalid characters to be replaced with an underscore
- colname_chars_replace_custom: dict of characters and their replacement value
- colname_chars_remove: string of characters to be removed
- sample_data: None or integer > 0, default 500; number of records to include in a sample_data sheet in output file. If None is passed, the sheet is omitted from the output file.
- parameter: interpret_date_timestamp - boolean default False, attempt to convert string fields to date or timestamp 
- parameter: interpret_date_timestamp_errors - text default "raise", options are "raise", "ignore", "coerce". "raise" will raise errors on values that cannot be converted, "ignore" will not raise errors and returns the input data, "coerce" will return NaT values when they cannot be converted.
