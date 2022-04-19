import csv
import pandas as pd

def parse(data_dictionary):
    assessments = {}
    with open(data_dictionary, encoding='utf-8') as redcap_dictionary:
        redcap_reader = pd.read_csv(redcap_dictionary)
        for _, dict_row in redcap_reader.iterrows():
            assessment = dict_row['Form Name']
            if assessment != 'informed_consent':
                variable_name = dict_row['Variable / Field Name']
                if assessment in assessments:
                    assessments[assessment].append(variable_name)
                else:
                    assessments[assessment] = [variable_name]
    return assessments
