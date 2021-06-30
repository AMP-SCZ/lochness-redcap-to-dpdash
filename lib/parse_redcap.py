from datetime import date
import re
import csv
import os
import glob

# Known date variables that do not include the phrase 'interview_date'
date_vars = ['chrcrit_date', 'chrcbc_testdate']

# Regular expression to get start and end days from existing CSVs
date_regex = re.compile(r'(.+)(day)(?P<start>\d+)(to)(?P<end>\d+)\.(csv)')


def to_csv(redcap_pull, subject, study, consent_date, subj_dir, assessments, logger):
    # Iterate through assessments in data dictionary
    for assessment, variable_list in assessments.items():
        # Initialize data CSV row
        data_row = {'day': 1, 'reftime': '',
                    'timeofday': '', 'weekday': ''}
        day_range = '-day1to1'
        max_day = 0
        # Check for existing CSVs for this assessment
        fileglob = subj_dir + '/' + study + '-' + subject + \
            '-' + assessment + '*.csv'
        already_exists = False
        data_for_assessment = 0
        # Find the max day of existing CSVs
        for path in glob.iglob(fileglob):
            basename = os.path.basename(path)
            match = date_regex.match(basename)
            if match and int(match['end']) > max_day:
                max_day = int(match['end'])
        # Start new CSV at max day + 1
        start_day = max_day + 1
        # Iterate through all variables in this assessment
        for variable_name in variable_list:
            # Get value from RedCAP JSON
            if variable_name in redcap_pull and redcap_pull[variable_name]:
                data_for_assessment += 1
                value = redcap_pull[variable_name]
                data_row[variable_name] = value
                # Get date of assessment
                if variable_name in date_vars or 'interview_date' in variable_name:
                    assessment_date = date.fromisoformat(value)
                    date_diff = (assessment_date - consent_date)
                    data_row['day'] = date_diff.days + 1
                    # Final day should be date of most recent assessment
                    day_range = '-day' + str(start_day) + \
                        'to' + str(date_diff.days + 1)
                    if data_row['day'] < start_day:
                        # Date already covered in existing CSVs for this assessment
                        already_exists = True
                        logger.debug('Error in %s', str(fileglob))
                        logger.debug('Date already covered: %s',
                                     str(assessment_date))
        if not already_exists and data_for_assessment != 0:
            data_rows = [data_row]
            if data_row['day'] > start_day:
                for i in range(start_day, data_row['day']):
                    data_rows.append({'day': i})
            filepath = subj_dir + '/' + study + '-' + subject + \
                '-' + assessment + day_range + '.csv'
            with open(filepath, 'w', newline='') as data_file:
                fieldnames = data_row.keys()
                writer = csv.DictWriter(data_file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sorted(data_rows, key=lambda i: i['day']))
