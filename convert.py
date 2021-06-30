import argparse
import glob
import json
import os
import logging
import re
from datetime import date
from lib import parse_dict, parse_redcap

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='Convert REDCap-via-lochness JSON into DPdash formatted data.')
    parser.add_argument('-d', '--dict', required=True,
                        help='path to the data dictionary CSV file from REDCap')
    parser.add_argument('-o', '--outdir', required=True,
                        help='output directory for all DPdash formatted CSVs')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument(
        'expr', help='double-quoted path to a single JSON file, or glob matching several JSON files')

    args = parser.parse_args()

    outdir = args.outdir
    if outdir[-1] != '/':
        outdir = outdir + '/'

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    level = logging.INFO
    if args.verbose:
        level = logging.DEBUG
    logging.basicConfig(level=level)

    # Parse assessments from data dictionary CSV
    assessments = parse_dict.parse(args.dict)

    # Regex to parse subject and study from filename
    json_regex = re.compile(r'(?P<subject>\w+)\.(?P<study>\w+)\.(json)')

    # Subdirectories that will be placed between study/site ID and subject ID
    subdirectory = '/processed/surveys/'

    # Get files from path glob
    for path in glob.iglob(args.expr, recursive=True):
        if not os.path.exists(path):
            logger.debug('file not found: %s', path)
            continue
        basename = os.path.basename(path)
        match = json_regex.match(basename)
        info = match.groupdict()
        if not info:
            logger.info('filename does not match expected format: %s', path)
            continue
        logger.info('Processing: %s', path)
        subject = info['subject']
        study = info['study']
        subj_dir = outdir + study + subdirectory + subject
        try:
            os.makedirs(subj_dir)
        except FileExistsError:
            pass
        with open(path, 'r') as f:
            loaded_json = json.load(f)
        if isinstance(loaded_json, list):
            # First loop through to find consent date
            for redcap_pull in loaded_json:
                if redcap_pull['chric_consent_date']:
                    consent_date = date.fromisoformat(
                        redcap_pull['chric_consent_date'])
            # Then loop again to fill out data CSV
            for redcap_pull in loaded_json:
                parse_redcap.to_csv(redcap_pull, subject,
                                    study, consent_date, subj_dir, assessments, logger)
        elif isinstance(loaded_json, dict):
            if loaded_json['chric_consent_date']:
                consent_date = date.fromisoformat(
                    loaded_json['chric_consent_date'])
            parse_redcap.to_csv(loaded_json, subject, study,
                                consent_date, subj_dir, assessments, logger)
            print('hi')
        else:
            logger.debug('json is neither array nor object: %s', path)
            continue


if __name__ == '__main__':
    main()
