import csv


def parse(data_dictionary):
    assessments = {}
    with open(data_dictionary) as redcap_dictionary:
        redcap_reader = csv.DictReader(redcap_dictionary)
        for dict_row in redcap_reader:
            assessment = dict_row['Form Name']
            if assessment != 'informed_consent':
                variable_name = dict_row['Variable / Field Name']
                if assessment in assessments:
                    assessments[assessment].append(variable_name)
                else:
                    assessments[assessment] = [variable_name]
    return assessments
