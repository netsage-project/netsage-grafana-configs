#!/usr/bin/env python3

# this script generates updated Grafana files for dashboards based the the TACC dashboards
#
# it looks for all files under netsage-grafana-configs/org_main-org/ with "TACC", and
#   replaces "TACC" with the org specifed with the -org argument
#   output files will be found in directory: output/ORG
#
# sample use:
#    generate_dashboards.py -org GPN
#
#  where ORG must be in the default dict 'org_list' defined below
#
# To Do:
#  need to set defaults for SNMP pages??
#      what-are-the-bandwidth-patterns-in-the-network.json
#      what-is-the-current-state-of-the-network.json
#
#  maybe handle:
#    reformate help text at top of page. See routine 'reformat_content' to use as a starting point.
#
#  maybe handle:
#    - currently this file is hardcoded to TACC: what-are-the-top-globus-tasks-by-organization.json:
#        "value": "AND (!(meta.src_organization:\"Texas Advanced Computing Center (TACC)\" AND meta.dst_organization:\"Texas Advanced Computing Center (TACC)\"))"
#        currently TACC (and ORNL) is usually the top site, so OK to use TACC as the default everywhere?
#

import os
import argparse
import re
import json
from bs4 import BeautifulSoup
import html
import sys
import shutil

# Global file skip list: the code below does not work on these (for now)
skip_files = [
# Flow files
    'individual-flow-information.json',
    'what-are-the-flows-by-project.json',
    'what-are-the-globus-tasks-by-project.json',
    'what-are-the-top-flows-by-country.json',
    'what-are-the-flows-by-project-resources.json',
    'what-are-the-top-globus-tasks-by-country.json',
    'individual-globus-task-information.json',
# SNMP files
    'what-are-the-bandwidth-patterns-in-the-network.json',
    'what-is-the-current-state-of-the-network.json',
    'advanced-flow-analysis.json'
]

# list of networks/org abbr, full name, default src site, index name, welcome page template
#     note: 3 types of 'welcome' page: all, flow, or globus
#          - all = flow + snmp + globus
#          - flow = flow + globus
#          - globus = globus only
#     note: default src based on top src for the month or April 2025
#     note: For FRGP, close 2nd place is NCAR
#     note: for SCN: top src is actually Google and Akamai, but using top University instead

org_list = [
    ('TACC', 'Texas Advanced Computing Center', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-tacc*', 'all'),
    ('TACC-dev', 'Texas Advanced Computing Center', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-tacc*', 'all'),
    ('TACC-internal', 'Texas Advanced Computing Center', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-internal-tacc*', 'all'),
    ('FRGP', 'Front Range GigaPop', 'National Oceanic and Atmospheric Administration (NOAA)', 'tacc-netsage-frgp*', 'all'),
    ('GPN', 'Great Plains Network', 'National Center for Atmospheric Research (NCAR)', 'tacc-netsage-gpn*', 'all'),
    ('LEARN', 'Lonestar Education and Research Network', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-learn*', 'all'),
    ('SoX', 'Southern Crossroads Network', 'Georgia Institute of Technology (GT)', 'tacc-netsage-sox*', 'all'),
    ('SCN', 'Sun Corridor Network', 'University of Arizona (UArizona)', 'tacc-netsage-suncorridor*', 'flow'),
    ('PIREN', 'Pacific Islands Research and Education Network', 'University of Hawaii', 'tacc-netsage-piren*', 'flow'),
    ('ACCESS', 'ACCESS Project', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-access*', 'flow'),
    ('Globus', 'All Globus Transfers', 'Oak Ridge National Laboratory (ORNL)', 'tacc-netsage-globus*', 'globus'),
    ('EPOC', 'All Data Collected by NetSage', 'Texas Advanced Computing Center (TACC)', 'tacc-netsage-epoc*', 'flow')
]

def clone_dashboards(input_dir, output_dir):
    print(f"Copying files from {input_dir} to {output_dir}")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files_copied = 0
    for root, dirs, files in os.walk(input_dir):
        # Remove subdirectories with 'Archive' in name from traversal
        dirs[:] = [d for d in dirs if 'Archive' not in d]

        # Compute destination path
        relative_path = os.path.relpath(root, input_dir)
        dest_root = os.path.join(output_dir, relative_path)
        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            shutil.copy2(src_file, dest_file)
            files_copied += 1

    print(f"  Copied {files_copied} files to {output_dir}")

def initialize_org_dict(org_list):
    org_dict = {}
    for org_abbr, org_name, default_src, index, welcome in org_list:
        org_dict[org_abbr] = {
            'org_name': org_name,
            'default_src': default_src,
            'index': index,
            'welcome': welcome
        }
    return org_dict

def force_ascii_escape(json_str):
    # Replace specific characters with their Unicode escape
    replacements = {
        '&': r'\u0026',
        '<': r'\u003c',
        '>': r'\u003e',
        "'": r'\u0027',
        '"': r'\u0022'
        # add more if needed
    }
    for char, escaped in replacements.items():
        json_str = json_str.replace(char, escaped)
    return json_str

def extract_parenthesized_part(org):
    match = re.search(r'\(([^)]+)\)', org)
    return match.group(1) if match else org

def encode_org_for_url(org):
    return org.replace(' ', '%20').replace('(', '%28').replace(')', '%29')

def update_text_value_fields(dash, default_src, filepath):
    """
    Update templating.list[0].current.text and .value to default_src.
    Returns True if any change was made.
    """
    changed = False
    try:
        templating = dash.get("templating", {})
        lst = templating.get("list", [])
        if not lst:
            return False

        item = lst[0]  # Only check the first item
        if "current" not in item:
            return False

        current = item["current"]
        old_text = current.get("text")
        old_value = current.get("value")

        # Normalize lists to first element
        if isinstance(old_text, list):
            old_text = old_text[0] if old_text else None
        if isinstance(old_value, list):
            old_value = old_value[0] if old_value else None

        if isinstance(old_text, str) and old_text not in (default_src, "All"):
            print(f'  [JSON] templating.current.text: "{old_text}" -> "{default_src}"')
            current["text"] = default_src
            changed = True

        if isinstance(old_value, str) and old_value != default_src:
            print(f'  [JSON] templating.current.value: "{old_value}" -> "{default_src}"')
            current["value"] = default_src
            changed = True

    except Exception as e:
        print(f"  [ERROR] Exception in update_text_value_fields for {filepath}: {e}")

    return changed


def reformat_content(data):
    """
    Takes a JSON-like dict with a 'content' field containing HTML,
    reformats it by:
    - Removing <center> tags.
    - Wrapping items in <li> inside a <blockquote>.
    - Keeping the heading <h1> and font color styling.
    - Returns a new dict with the reformatted 'content'.

    Sample use:     new_data = reformat_content(original_data)
    """
    # Unescape unicode HTML entities
    html_content = html.unescape(data.get("content", ""))

    # Parse with BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract the first <h1> inside <center> for the title
    title_tag = soup.find('h1')
    if not title_tag:
        raise ValueError("No <h1> tag found in content")

    # Extract text from the remaining <center> tags into <li> items
    li_items = []
    for center_tag in soup.find_all('center'):
        # Skip if this <center> has the <h1> (the title)
        if center_tag.find('h1'):
            continue
        # Clean text and wrap in <li>
        text = center_tag.get_text(strip=True)
        if text:  # skip empty centers
            li_items.append(f"<li>{text}")

    # Build the new HTML structure
    new_html = f'<font color="#5794f2"><blockquote>{str(title_tag)}'
    new_html += ''.join(li_items)
    new_html += '</blockquote>'

    # Return the new JSON structure
    return {"content": new_html}



def process_file(filepath, org, org_abbr, default_src, netsage_org_part, encoded_org, output_dir, debug=False):
    """
    Process a single dashboard JSON file:
      1. Apply phrase-level string replacements (TACC label phrases).
      2. Parse JSON and update templating.current.text/value.
      3. Write modified file to output_dir if anything changed.
    """

    phrases = [
        r'Data Sources to TACC',
        r'TACC Links at a Glance',
        r'Welcome to Netsage - TACC'
    ]

    # Derive a short relative label for display
    display_path = filepath

    print(f"\n{'='*70}")
    print(f"Processing: {display_path}")

    # --- Read source file ---
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_data = f.read()
    except OSError as e:
        print(f"  [ERROR] Cannot read file {filepath}: {e}")
        return

    data = original_data
    changed = False
    phrase_changed = False
    json_changed = False

    # --- Step 1: Phrase-level string replacements ---
    pattern = r'(' + '|'.join(re.escape(p) for p in phrases) + r')'
    matches = re.findall(pattern, data)
    if matches:
        for match in matches:
            new_line = match.replace('TACC', org_abbr)
            print(f'  [PHRASE] "{match}" -> "{new_line}"')
            data = data.replace(match, new_line)
        phrase_changed = True
        changed = True
    else:
        print(f'  [PHRASE] No phrase matches found.')

    # --- Step 2: JSON parse and update templating.current ---
    try:
        dash = json.loads(data)
    except json.JSONDecodeError as e:
        print(f"  [ERROR] Cannot parse as JSON: {e}")
        print(f"  [ERROR] Skipping file: {filepath}")
        return

    try:
        json_changed = update_text_value_fields(dash, default_src, filepath)
    except Exception as e:
        print(f"  [ERROR] Unexpected error in update_text_value_fields: {e}")
        return

    if json_changed:
        # FIX: serialize the modified dash back into data so the written file
        # reflects the JSON changes. Previously json_data was computed but
        # never assigned back, so the original string was written unchanged.
        try:
            data = json.dumps(dash, indent=2, ensure_ascii=True)
        except (TypeError, ValueError) as e:
            print(f"  [ERROR] json.dumps failed for {filepath}: {e}")
            print(f"  [ERROR] Skipping file — JSON changes not applied.")
            return

        # note: json.dumps leaves characters like &, <, > alone.
        #  the files generated by Grafana convert those characters to unicode
        #  if this is a problem, uncomment this:
        # data = force_ascii_escape(data)

        changed = True
    else:
        print(f'  [JSON]  No templating.current changes needed.')

    # --- Step 3: Write output if changed ---
    if not changed:
        print(f'  [SKIP] No changes made.')
        return

    # Build output path
    parent_dir = os.path.basename(os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    outpath = os.path.join(output_dir, parent_dir, filename)

    # Ensure the output subdirectory exists
    out_subdir = os.path.dirname(outpath)
    try:
        os.makedirs(out_subdir, exist_ok=True)
    except OSError as e:
        print(f"  [ERROR] Cannot create output directory {out_subdir}: {e}")
        return

    try:
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f'  [WRITE] Output written to: {outpath}')
    except OSError as e:
        print(f"  [ERROR] Cannot write output file {outpath}: {e}")
        return


def main():
    input_dir = 'dashboards'
    defaults_file = '/var/opt/netsage-grafana/default.json'

    parser = argparse.ArgumentParser(description='Replace Netsage strings in dashboard JSON files.')
    parser.add_argument('-org', required=True, help='Organization abbreviation (e.g., TACC, FRGP, GPN).')
    parser.add_argument('-o', '--output-dir', required=True, help='Path to the output directory')
    args = parser.parse_args()

    org_abbr = args.org
    output_dir = os.path.join(args.output_dir, org_abbr)

    org_dict = initialize_org_dict(org_list)

    if org_abbr not in org_dict:
        print(f"Error: '{org_abbr}' is not a valid organization abbreviation.")
        print("Valid options are:", ', '.join(org_dict.keys()))
        sys.exit(1)

    org_full_name = org_dict[org_abbr]['org_name']
    default_src = org_dict[org_abbr]['default_src']
    netsage_org_part = extract_parenthesized_part(org_full_name)
    encoded_org = encode_org_for_url(org_full_name)

    print(f"\nOrg:         {org_abbr}")
    print(f"Full name:   {org_full_name}")
    print(f"Default src: {default_src}")
    print(f"Index:       {org_dict[org_abbr]['index']}")
    print(f"Output dir:  {output_dir}")

    if not os.path.isdir(input_dir):
        print(f"\nError: Input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    current_dir = os.getcwd()
    # --- Clone dashboards directory first so output tree exists ---
    print()
    clone_dashboards(current_dir, output_dir + '/org_main-org')

    # --- Copy welcome page directly into output tree ---
    welcome_type = org_dict[org_abbr]["welcome"]
    welcome_map = {
        "globus": "../homepage/welcome-globus.json",
        "all":    "../homepage/welcome-all.json",
        "flow":   "../homepage/welcome-flow.json"
    }

    if welcome_type not in welcome_map:
        print(f"\n[ERROR] Unknown welcome type '{welcome_type}' for org {org_abbr}", file=sys.stderr)
        sys.exit(1)

    src_welcome = os.path.join(current_dir, welcome_map[welcome_type])
    dest_welcome = os.path.join(output_dir, 'org_main-org', 'dashboards', 'General', 'welcome.json')
    try:
        os.makedirs(os.path.dirname(dest_welcome), exist_ok=True)
        shutil.copy2(src_welcome, dest_welcome)
        print(f"\nCopied welcome file:")
        print(f"         src:  {src_welcome}")
        print(f"         dest: {dest_welcome}")
    except OSError as e:
        if not os.path.exists(src_welcome):
            print(f"\n[ERROR] Welcome file copy failed — SOURCE not found:", file=sys.stderr)
            print(f"         src:  {src_welcome}", file=sys.stderr)
        elif isinstance(e, PermissionError):
            print(f"\n[ERROR] Welcome file copy failed — PERMISSION DENIED on destination:", file=sys.stderr)
            print(f"         src:  {src_welcome}", file=sys.stderr)
            print(f"         dest: {dest_welcome}", file=sys.stderr)
        else:
            print(f"\n[ERROR] Welcome file copy failed ({type(e).__name__}):", file=sys.stderr)
            print(f"         src:  {src_welcome}", file=sys.stderr)
            print(f"         dest: {dest_welcome}", file=sys.stderr)
            print(f"         err:  {e}", file=sys.stderr)
        sys.exit(1)


    # --- Create secure dir and copy defaults ---
    secure_dir = output_dir + '/secure'
    try:
        os.makedirs(secure_dir, exist_ok=True)
        print(f"Created directory: {secure_dir}")
    except OSError as e:
        print(f"[ERROR] Cannot create directory {secure_dir}: {e}", file=sys.stderr)
        sys.exit(1)

    df = os.path.join(secure_dir, 'default.json')
    try:
        shutil.copy(defaults_file, df)
        print(f"Copied {defaults_file} -> {df}")
    except OSError as e:
        print(f"[ERROR] Cannot copy defaults file {defaults_file}: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Process each dashboard JSON ---
    files_processed = 0
    files_changed = 0

    for root, _, files in os.walk(input_dir):
        if 'Archive' in root:
            continue

        for filename in files:
            if filename.endswith('.json') and filename not in skip_files:
                filepath = os.path.join(root, filename)
                files_processed += 1
                try:
                    process_file(
                        filepath,
                        org_full_name,
                        org_abbr,
                        default_src,
                        netsage_org_part,
                        encoded_org,
                        output_dir + '/org_main-org/dashboards',
                    )
                except Exception as e:
                    import traceback
                    print(f"\n  [FATAL] Unhandled exception processing {filepath}: {e}")
                    print(f"  [FATAL] Skipping — continuing to next file...")
                    traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"Processed {files_processed} files.")

    # --- Update connections/netsage.json index ---
    print("\nLooking for connections/netsage.json to update index...")
    for root, dirs, files in os.walk(output_dir):
        if 'connections' in dirs:
            for conn_filename in ['netsage.json', 'netsage-snmp.json']:
                json_path = os.path.join(root, 'connections', conn_filename)
                if not os.path.isfile(json_path):
                    continue

                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        conn_data = json.load(f)

                    if "jsonData" not in conn_data or "index" not in conn_data["jsonData"]:
                        print(f"  [SKIP] No jsonData.index found in {json_path}")
                        continue

                    old_index = conn_data["jsonData"]["index"]
                    base_index = org_dict[org_abbr]["index"]
                    new_index = base_index.replace("netsage", "snmp") if conn_filename == "netsage-snmp.json" else base_index

                    if old_index == new_index:
                        print(f"  [SKIP] Index already correct in {json_path}: '{old_index}'")
                        continue

                    conn_data["jsonData"]["index"] = new_index
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(conn_data, f, indent=2)
                    print(f"  [UPDATE] {json_path}: index '{old_index}' -> '{new_index}'")

                except json.JSONDecodeError as e:
                    print(f"  [ERROR] Cannot parse JSON in {json_path}: {e}")
                except OSError as e:
                    print(f"  [ERROR] Cannot read/write {json_path}: {e}")

    print("\nDone.\n")

if __name__ == '__main__':
    main()

