# lochness REDCap to DPdash

Python scripts to convert REDCap survey JSON files produced by lochness into
DPdash/DPimport-ready CSVs

- [lochness REDCap to DPdash](#lochness-redcap-to-dpdash)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Input](#input)
    - [Output](#output)
  - [Additional notes](#additional-notes)
    - [Date variables](#date-variables)
    - [Output dates](#output-dates)


## Requirements

Python 3

## Installation

No installation required, just clone the git repo or download the code.

```sh
git clone https://github.com/AMP-SCZ/lochness-redcap-to-dpdash.git
```

## Usage

```
convert.py [-h] -d DICT -o OUTDIR [-v] expr

positional arguments:
  expr                  double-quoted path to a single JSON file, or
                        glob matching several JSON files

optional arguments:
  -h, --help            show this help message and exit
  -d DICT, --dict DICT  path to the data dictionary CSV file from REDCap
  -o OUTDIR, --outdir OUTDIR
                        output directory for all DPdash formatted CSVs
  -v, --verbose
```

Example usage:

```sh
python convert.py \
--dict /dict.csv \
--outdir /RED-PHOENIX/GENERAL \
"/RED-PHOENIX/PROTECTED/**/*.json"
```

Where `/RED-PHOENIX/PROTECTED/**/*.json` matches all JSON files to be parsed.

You may also use a single `*` glob expression, such as `/RED-PHOENIX/PROTECTED/STUDY_ID/SUBJECT_ID/DATA_TYPE/*.json`, or a path to a single file.

<details>
<summary>Details about the pattern /**/</summary>
<br>

`directory/*/*.json` matches only `directory/[subdirectory]/[filename].json`. With a [recursive glob pattern](https://docs.python.org/3/library/glob.html#glob.glob), `directory/**/*.json` will additionally match:

* `directory/[filename].json` (no subdirectory)
* `directory/[subdirectory1]/[subdirectory2]/[filename].json` (sub-subdirectory)

and so on, for as many levels deep as exist in the directory tree.

</details>


### Input

The input JSON files must be formatted as `SUBJECT_ID.STUDY_ID.json`,
for example, `HK06989.FAKE_HK.json`.

The input data dictionary CSV must have columns called `Variable / Field Name`
and `Form Name`.

### Output 

The output is a directory or set of directories containing CSV files,
with the following structure:

```
├── STUDY_ID
│   └── processed
│       └── surveys
│           ├── SUBJECT_ID
│           │   ├── STUDY_ID-SUBJECT_ID-assessment-day1to121.csv
│           │   ├── STUDY_ID-SUBJECT_ID-assessment-day122to165.csv
```

## Additional notes

### Date variables

Dates for assessments are ascertained according to specific variable names. 
In particular, a date variable must either contain the phrase `interview_date`, or 
be one of `chrcrit_date` or `chrcbc_testdate`. Since we expect REDCap forms for the
AMP-SCZ study to follow this convention, they have been hard-coded.

If different variables must be added to correspond to assessment dates, they can be
added to the list `date_vars` in `lib/parse_redcap.py`.

### Output dates

Assessments will be not be processed into output if their date is already covered in 
existing dayXtoY CSV files for that particular assessment. This is to prevent overwriting
existing data.

If the date of the assessment is not in the existing range, output CSVs will be created 
with the range starting from the end of the previous day range (if existing) and ending
with the date of the assessment. The existing files will not be modified.

For example, in the [above directory tree](#output), `assessment` was conducted for this
subject on days 121 and 165 since consent, so the first output file starts at day 1 and
the second output file starts at day 122. Moreover, days 1-120 and 122-164 contain no data.
