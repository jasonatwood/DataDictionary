# DataProfiler
In any data system, the introduction of new data brings questions about the contents. Discovery and documentation of a data set is critical and a lot can be learned through basic data profiling steps. This Python package uses the Pandas library to create a standardized output that provides insights on the contents of a sample data set. The output can provide any data architect, data engineer, business analyst or data analyst with the information they need to make effective and efficient early decisions about the value of and potential issues in a new data set.

## Components of the Output
The output is a XLSX formatted Microsoft Excel workbook with information spread across mutliple worksheets.

- Data Types
- Text Value Distribution
- Numeric Value Distribution
- Potential Primary Keys

### Data Types
This worksheet is a great starting point for a data catalogue or data dictionary. At a glance, this report provides:

- The original field name
  - Presented as the name appears in the sample file
- A 'clean' version of the field name
  - These values are optimized for legibility and compatibility with RDBMS standards (See Column Name Cleanup in this section)
- The presumed data type
  - Data types are simplified into text, integer, decimal, or N/A (See Data Type Detection in this section)
- The minimum and maximum lengths for text fields
- The minimum and maximum values for integer fields
- The precision and scale for decimal fields
- Potential ID flag
  - If based on the pattern of the field name, make a guess to whether or not it's an ID field
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
  - Partial customization (see table 1) 

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
The best source of information for data types from a data source is a physical data model or the DDL used to create the source table. More often than not, that information is either not available or takes a prohibitively long amount of time to obtain from the data owner. This feature is meant to be a helpful suggestion based on the observed records in the sample data. Data types are simplified to avoid prescriptive output.

Data Types in Output |
---------------------|
decimal |
integer |
decimal or integer |
text |
N/A |

\* N/A is assigned to fields that contain only NULL values, no data type can be suggested

\*\* 'decimal or integer' is assigned to fields that may contain integer values in the source file but while processing that file NULL values were detected which Pandas converts to the float data type. Therefore with ambiguous data a loose suggestion is made.

### Text Value Distribution
For each text field, a distribution is appended to this worksheet with the count of NULL values appearing at the top.

### Numeric Value Distribution
The output on this worksheet is from the Pandas DataFrame.describe() method. It shows the distribution of numeric fields and **excludes** potential ID fields.

### Potential Primary Keys
This is one of the less developed features, however can be useful to highlight fields with heterogenous data that may indicate they may be the natural key or part of the natural key for the given sample data.

## Using the DataProfiler
```python
import profiledata
profiler = profiledata.ProfileData()

# profile a single file
profiler.process_file('./tests/test1.csv', dest_dir='./tests/', colname_chars_remove=r'aeiou')

# profile a directory of files
profiler.process_directory('./tests/', dest_dir='./tests/', contain='test1', not_contain='test2')

# profile a Pandas DataFrame
profiler.process_dataframe(dest_dir='./tests/', dataframe=sample_df, dataframe_name='sample_df')

```