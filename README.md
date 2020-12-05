# DataProfiler
In any data system, the introduction of new data brings questions about the contents. Discovery and documentation of a data set is critical and a lot can be learned through basic data profiling steps. This package uses the Pandas library to create a standardized output that provides insights on the contents of a sample data set. The output can provide any data architect, data engineer, business analyst or data analyst with the information they need to make effective and efficient early decisions about the value of and potential issues in a new data set.

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
  - This name is optimized for legibility and compatibility with RDBMS standards (See Additional Info in this section)
- The presumed data type
  - Data types are simplified into text, integer, decimal, or N/A for fields composed entirely of NULL values (See Additional Info in this section)
- The minimum and maximum lengths for text fields
- The minimum and maximum values for integer fields
- The precision and scale for decimal fields
- Potential ID flag
  - If based on the pattern of the field name, make a guess to whether or not it's an ID field
- Nullable flag
  - If one or more values are found to be NULL, set to 1 or True

**Additional Info**
There are two parameters that can be used to customize the clean column name output. The default functionality of the cleansing process makes the following replacements using Regular Expressions:
Target Character(s) | Replacement Character(s)
--------------------|-------------------------
\\/()[]{},.!@?:;\|-^~`\\s+ | _ 
\# | num
$ | usd
% | pct
& | and
\+ | plus
\* | times
= | equals
\< | lt
\> | gt

colname_chars_replace_custom
colname_chars_remove
