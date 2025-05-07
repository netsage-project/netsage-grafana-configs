#!/usr/bin/env python3

# this script generated updated Grafana files for dashboards based the the TACC dashboards
#
# it looks for all files under netsage-grafana-configs/org_1/dashboards with TACC, and 
#   replaces TACC with the org specifed with the -org argument, and generates updated files ending in .updated
#
# sample use:
#    generate_dashboards.py -org "Great Plains Network (GPN)"
#
#  where ORG must be in the default dict defined below
#
# To Do:
#  need to set defaults for SNMP pages??
#      what-are-the-bandwidth-patterns-in-the-network.json
#      what-is-the-current-state-of-the-network.json
#
# Questions:
#    does uid need to change depending on org?

import os
import argparse
import re
import json

# Global file skip list: the code below does not work on these
skip_files = [
    'individual-flow-information.json',
    'what-are-the-top-flows-by-country.json',
    'what-are-the-top-globus-tasks-by-country.json',
    'individual-globus-task-information.json',
    'advanced-flow-analysis.json'
]

# list of networks/org abbr, full name, and default src site
#     note: default src based on top src for the month or April 2025
#     note: For FRGP, close 2nd place is NCAR
#     note: for SCN: top src is actually Google and Akamai, but using top University instead
org_list = [
    ('TACC', 'Texas Advanced Computing Center', 'Texas Advanced Computing Center (TACC)'),
    ('FRGP', 'Front Range GigaPop', 'National Oceanic and Atmospheric Administration (NOAA)'),
    ('GPN', 'Great Plains Network', 'National Center for Atmospheric Research (NCAR)'),
    ('LEARN', 'Lonestar Education and Research Network', 'Texas Advanced Computing Center (TACC)'),
    ('SoX', 'Southern Crossroads Network', 'Georgia Institute of Technology (GT)'),
    ('SCN', 'Sun Corridor Network', 'University of Arizona (UArizona)'),
    ('ACCESS', 'ACCESS Project', 'Texas Advanced Computing Center (TACC)'),
    ('Globus', 'All Globus Transfers', 'Oak Ridge National Laboratory (ORNL)'),
    ('EPOC', 'All Data Collected by NetSage', 'Texas Advanced Computing Center (TACC)')
]

def initialize_org_dict(org_list):
    org_dict = {}
    for org_abbr, org_name, default_src in org_list:
        org_dict[org_abbr] = {
            'org_name': org_name,
            'default_src': default_src
        }
    return org_dict

def extract_parenthesized_part(org):
    match = re.search(r'\(([^)]+)\)', org)
    return match.group(1) if match else org

def encode_org_for_url(org):
    return org.replace(' ', '%20').replace('(', '%28').replace(')', '%29')

def update_text_value_fields(dash, default_src, filepath):
    changed = False
    try:
        templating = dash.get("templating", {})
        lst = templating.get("list", [])
        if lst:
            item = lst[0]  # Only check the first item
            if "current" in item:
                current = item["current"]
                old_text = current.get("text")
                old_value = current.get("value")
                if isinstance(old_text, str) and old_text != default_src:
                    print(f'[FILE: {filepath}]\nOLD text: {old_text}\nNEW text: {default_src}\n')
                    current["text"] = default_src
                    changed = True
                if isinstance(old_value, str) and old_value != default_src:
                    print(f'[FILE: {filepath}]\nOLD value: {old_value}\nNEW value: {default_src}\n')
                    current["value"] = default_src
                    changed = True
    except Exception as e:
        print(f"Error processing templating section in {filepath}: {e}")
    return changed

def process_file(filepath, org, org_abbr, default_src, netsage_org_part, encoded_org):
    changed = False

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = f.read()

        # Replace only if both 'Welcome to Netsage' and 'content' are on the line, and replace with org_abbr
        pattern = r'(.*content.*Welcome to Netsage - )TACC'
        matches = re.findall(pattern, data)
        if matches:
            for match in matches:
                old_line = match + 'TACC'
                new_line = match + org_abbr
                print(f'[FILE: {filepath}]\nOLD line: {old_line}\nNEW line: {new_line}\n')
                data = data.replace(old_line, new_line)
            changed = True

        # Try parsing JSON and modifying templating.current.text/value
        try:
            dash = json.loads(data)
            json_changed = update_text_value_fields(dash, default_src, filepath)
            if json_changed:
                data = json.dumps(dash, indent=2)
                changed = True
        except Exception as e:
            print(f"Warning: {filepath} could not be parsed as JSON: {e}")

        # Write updated file if changed
        if changed:
            outpath = f"{filepath}.{org_abbr}"
            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(data)
            print(f'Updated file written to: {outpath}\n')
        else:
            print(f'No changes made in file: {filepath}\n')

    except Exception as e:
        print(f"Failed to process file {filepath}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Replace Netsage strings in dashboard JSON files.')
    parser.add_argument('-org', required=True, help='Organization abbreviation (e.g., TACC, FRGP, GPN).')
    args = parser.parse_args()
    org_abbr = args.org

    org_dict = initialize_org_dict(org_list)

    if org_abbr not in org_dict:
        print(f"Error: '{org_abbr}' is not a valid organization abbreviation.")
        print("Valid options are:", ', '.join(org_dict.keys()))
        exit(1)

    org_full_name = org_dict[org_abbr]['org_name']
    default_src = org_dict[org_abbr]['default_src']
    netsage_org_part = extract_parenthesized_part(org_full_name)
    encoded_org = encode_org_for_url(org_full_name)

    for root, _, files in os.walk('.'):
        for filename in files:
            if filename.endswith('.json') and filename not in skip_files:
                filepath = os.path.join(root, filename)
                process_file(filepath, org_full_name, org_abbr, default_src, netsage_org_part, encoded_org)

if __name__ == '__main__':
    main()

