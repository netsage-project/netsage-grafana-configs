#!/usr/bin/env python3

# this script generates updated Grafana files for dashboards based the the TACC dashboards
#
# it looks for all files under netsage-grafana-configs/org_main-org/ with "TACC", and 
#   replaces "TACC" with the org specifed with the -org argument
#   output files will be found in directory: output/ORG
#
# sample use:
#    generate_dashboards.py -org GPN -o output/
#    generate_dashboards.py -org GPN -o output/ --debug
#
#  where ORG must be in the default dict 'org_list' defined below
#
# To Do:
#  need to set defaults for SNMP pages??
#      what-are-the-bandwidth-patterns-in-the-network.json
#      what-is-the-current-state-of-the-network.json
#
#  maybe handle:
#    reformat help text at top of page. See routine 'reformat_content' to use as a starting point.
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
import difflib

# Global allowlist: only these files will be processed
include_files = [
    'what-are-the-top-flows-by-organization.json',
    'what-do-individual-flows-by-organization-look-like.json',
    'what-are-the-slowest-scp-flows-by-organization.json',
]

# list of networks/org abbr, full name, default src site, index name, welcome page template
#     note: 4 types of 'welcome' page: all, flow, ACCESS, or globus
#          - all = flow + snmp + globus
#          - flow = flow + globus
#          - ACCESS = special version of flow for ACCESS 
#          - globus = globus only
#     note: default src based on top src for the month or April 2025
#     note: For FRGP, close 2nd place is NCAR
#     note: for SCN: top src is actually Google and Akamai, but using top University instead

org_list = [
    ('TACC',          'Texas Advanced Computing Center',               'Texas Advanced Computing Center (TACC)',           'tacc-netsage-tacc*',          'all'),
    ('TACC-dev',      'Texas Advanced Computing Center',               'Texas Advanced Computing Center (TACC)',           'tacc-netsage-tacc*',          'all'),
    ('TACC-internal', 'Texas Advanced Computing Center',               'Texas Advanced Computing Center (TACC)',           'tacc-netsage-internal-tacc*', 'all'),
    ('FRGP',          'Front Range GigaPop',                           'National Oceanic and Atmospheric Administration (NOAA)', 'tacc-netsage-frgp*',   'all'),
    ('GPN',           'Great Plains Network',                          'National Center for Atmospheric Research (NCAR)',  'tacc-netsage-gpn*',           'all'),
    ('LEARN',         'Lonestar Education and Research Network',       'Texas Advanced Computing Center (TACC)',           'tacc-netsage-learn*',         'all'),
    ('SoX',           'Southern Crossroads Network',                   'Georgia Institute of Technology (GT)',             'tacc-netsage-sox*',           'all'),
    ('SCN',           'Sun Corridor Network',                          'University of Arizona (UArizona)',                 'tacc-netsage-suncorridor*',   'flow'),
    ('PIREN',         'Pacific Islands Research and Education Network', 'University of Hawaii',                            'tacc-netsage-piren*',         'flow'),
    ('ACCESS',        'ACCESS Project',                                'Texas Advanced Computing Center (TACC)',           'tacc-netsage-access*',        'access'),
    ('Globus',        'All Globus Transfers',                          'Oak Ridge National Laboratory (ORNL)',             'tacc-netsage-globus*',        'globus'),
    ('EPOC',          'All Data Collected by NetSage',                 'Texas Advanced Computing Center (TACC)',           'tacc-netsage-epoc*',          'flow')
]


def clone_dashboards(input_dir, output_dir, debug=False):
    print(f"[INFO] Copying files from '{input_dir}' to '{output_dir}'")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files_copied = 0
    for root, dirs, files in os.walk(input_dir):
        # Remove subdirectories with 'Archive' and 'General' in name from traversal
        #  (welcome file in General gets copied over separately)
        dirs[:] = [d for d in dirs if 'Archive' not in d and d != 'General']

        # Compute destination path
        relative_path = os.path.relpath(root, input_dir)
        dest_root = os.path.join(output_dir, relative_path)
        os.makedirs(dest_root, exist_ok=True)

        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)
            if debug:
                print(f"  [DEBUG] Copying: {src_file} -> {dest_file}")
            shutil.copy2(src_file, dest_file)
            files_copied += 1

    print(f"[INFO] Cloned {files_copied} file(s) to '{output_dir}'")


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
    # Replace specific characters with their Unicode escape sequences
    # & seems to be most important? 
    replacements = {
        '&': r'\u0026',
        '<': r'\u003c',
        '>': r'\u003e',
        #"'": r'\u0027',
        #'"': r'\u0022'
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


def update_text_value_fields(dash, default_src, filepath, debug=False):
    """
    Update templating.list[0].current.text and .value to default_src.

    BUG FIX: Grafana stores these fields as either a plain string or a list
    (e.g. ["Texas Advanced Computing Center (TACC)"]). We must preserve the
    original container type when writing back, otherwise Grafana will reject
    the dashboard or silently mis-apply the default variable.
    """
    changed = False
    try:
        templating = dash.get("templating", {})
        lst = templating.get("list", [])
        if not lst:
            if debug:
                print(f"  [DEBUG] {filepath}: no templating.list entries found")
            return changed

        item = lst[0]  # Only check the first item
        if "current" not in item:
            if debug:
                print(f"  [DEBUG] {filepath}: templating.list[0] has no 'current' key")
            return changed

        current = item["current"]
        old_text = current.get("text")
        old_value = current.get("value")

        # Remember whether original values were lists so we can preserve that type
        text_is_list = isinstance(old_text, list)
        value_is_list = isinstance(old_value, list)

        # Normalize to scalar for comparison
        cmp_text = old_text[0] if text_is_list and old_text else old_text
        cmp_value = old_value[0] if value_is_list and old_value else old_value

        if debug:
            print(f"  [DEBUG] {filepath}: current.text  = {old_text!r}  (list={text_is_list})")
            print(f"  [DEBUG] {filepath}: current.value = {old_value!r}  (list={value_is_list})")

        # Update text if it differs and is not the "All" wildcard
        if isinstance(cmp_text, str) and cmp_text != default_src and cmp_text != "All":
            new_text = [default_src] if text_is_list else default_src
            print(f"  [UPDATE] {filepath}")
            print(f"           current.text:  {old_text!r}")
            print(f"                      ->  {new_text!r}")
            current["text"] = new_text
            changed = True

        # Update value if it differs (no "All" carve-out needed here)
        if isinstance(cmp_value, str) and cmp_value != default_src:
            new_value = [default_src] if value_is_list else default_src
            print(f"  [UPDATE] {filepath}")
            print(f"           current.value: {old_value!r}")
            print(f"                      ->  {new_value!r}")
            current["value"] = new_value
            changed = True

    except Exception as e:
        print(f"[ERROR] Exception while processing templating section in {filepath}: {e}")

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


def show_diff(original_lines, new_data, filepath, outpath):
    """Print a unified diff between the original file lines and the new content."""
    new_lines = new_data.splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile=f'ORIGINAL: {filepath}',
        tofile=f'UPDATED:   {outpath}',
        n=0
    ))
    if diff_lines:
        print(f"  [DIFF] Changes in {os.path.basename(filepath)}:")
        print(''.join(diff_lines))
    else:
        print(f"  [DIFF] No textual diff detected for {filepath} despite changed=True")


def process_file(filepath, org, org_abbr, default_src, netsage_org_part, encoded_org, output_dir, debug=False):
    """
    Process a single dashboard JSON file:
      1. Replace TACC-specific title/link phrases with org-specific equivalents.
      2. Update templating.list[0].current.text / .value to the new default_src.
      3. Write the modified file to output_dir (only if changes were made).
    """
    changed = False
    phrase_changes = 0
    json_changed = False

    phrases = [
        r'Data Sources to TACC',
        r'TACC Links at a Glance',
        r'Welcome to Netsage - TACC'
    ]

    print(f"[INFO] Processing: {filepath}")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_text = f.read()

        data = original_text  # working copy; original_text kept for diff

        # ------------------------------------------------------------------
        # Step 1: String-level phrase replacements
        # ------------------------------------------------------------------
        pattern = r'(' + '|'.join(re.escape(p) for p in phrases) + r')'
        matches = re.findall(pattern, data)
        if matches:
            for match in matches:
                new_phrase = match.replace('TACC', org_abbr)
                if debug:
                    print(f"  [DEBUG] Phrase replace: {match!r} -> {new_phrase!r}")
                else:
                    print(f"  [PHRASE] {match!r} -> {new_phrase!r}")
                data = data.replace(match, new_phrase)
                phrase_changes += 1
            changed = True

        # ------------------------------------------------------------------
        # Step 2: JSON-level templating.current.text / .value update
        # ------------------------------------------------------------------
        try:
            dash = json.loads(data)
        except json.JSONDecodeError as e:
            print(f"  [ERROR] Could not parse '{filepath}' as JSON: {e}")
            sys.exit(1)

        json_changed = update_text_value_fields(dash, default_src, filepath, debug=debug)
        if json_changed:
            data = json.dumps(dash, indent=2, ensure_ascii=True)
 
            # keep JSON list in compact form, like which grafana generates
            # note: I dont think this is necessary, but it makes it easier to see key changes in debug output
            data = compact_short_arrays(data)

            # note: json.dumps leaves characters like &, <, > alone.
            # The files generated by Grafana convert those characters to unicode.
            data = force_ascii_escape(data)

            changed = True

        # ------------------------------------------------------------------
        # Step 3: Write output (only once, only if something changed)
        # ------------------------------------------------------------------
        if changed:
            parent_dir = os.path.basename(os.path.dirname(filepath))
            filename = os.path.basename(filepath)
            outpath = os.path.join(output_dir, parent_dir, filename)
            os.makedirs(os.path.dirname(outpath), exist_ok=True)

            if debug:
                show_diff(original_text.splitlines(keepends=True), data, filepath, outpath)

            with open(outpath, 'w', encoding='utf-8') as f:
                f.write(data)

            summary_parts = []
            if phrase_changes:
                summary_parts.append(f"{phrase_changes} phrase replacement(s)")
            if json_changed:
                summary_parts.append("templating current updated")
            print(f"  [WRITTEN] {outpath}  ({', '.join(summary_parts)})\n")
        else:
            print(f"  [SKIP] No changes needed in: {filepath}\n")

    except Exception as e:
        print(f"[ERROR] Failed to process file '{filepath}': {e}")
        sys.exit(1)


def compact_short_arrays(s, max_length=80):
    """Collapse multi-element arrays of simple scalars onto one line if they fit."""
    def replacer(m):
        # Strip the matched block and re-join compactly
        inner = re.sub(r'\s+', ' ', m.group(1).strip())
        compact = f'[{inner}]'
        return compact if len(compact) <= max_length else m.group(0)

    return re.sub(
        r'\[(\n\s+(?:"[^"]*"|[\d.eE+\-]+|true|false|null)(?:,\n\s+(?:"[^"]*"|[\d.eE+\-]+|true|false|null))*\n\s+)\]',
        replacer,
        s
    )


def update_connection_index(output_dir, org_dict, org_abbr, debug=False):
    """Walk output_dir looking for connections/netsage.json and connections/netsage-snmp.json
    and update their jsonData.index to match the org's configured index pattern."""
    print("[INFO] Looking for connections/netsage*.json to update index...")
    updated = 0
    for root, dirs, files in os.walk(output_dir):
        if 'connections' in dirs:
            for filename in ['netsage.json', 'netsage-snmp.json']:
                json_path = os.path.join(root, 'connections', filename)
                if not os.path.isfile(json_path):
                    if debug:
                        print(f"  [DEBUG] Not found (skipping): {json_path}")
                    continue

                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        conn_data = json.load(f)

                    if "jsonData" not in conn_data or "index" not in conn_data["jsonData"]:
                        print(f"  [WARN] No jsonData.index found in {json_path}")
                        continue

                    old_index = conn_data["jsonData"]["index"]
                    base_index = org_dict[org_abbr]["index"]
                    new_index = base_index.replace("netsage", "snmp") if filename == "netsage-snmp.json" else base_index

                    if old_index == new_index:
                        print(f"  [SKIP] Index already correct in {json_path}: '{old_index}'")
                        continue

                    conn_data["jsonData"]["index"] = new_index
                    #output = json.dumps(conn_data, indent=2, ensure_ascii=True)
                    output = force_ascii_escape(json.dumps(conn_data, indent=2, ensure_ascii=True))
                    with open(json_path, "w", encoding="utf-8") as f:
                        f.write(output)
                    print(f"  [UPDATE] {json_path}")
                    print(f"           index: '{old_index}' -> '{new_index}'")
                    updated += 1

                except Exception as e:
                    print(f"  [ERROR] Failed to update index in {json_path}: {e}")

    print(f"[INFO] Connection index update complete: {updated} file(s) modified")

def update_connection_index_old(output_dir, org_dict, org_abbr, debug=False):
    """Walk output_dir looking for connections/netsage.json and connections/netsage-snmp.json
    and update their jsonData.index to match the org's configured index pattern."""
    print("[INFO] Looking for connections/netsage*.json to update index...")
    updated = 0
    for root, dirs, files in os.walk(output_dir):
        if 'connections' in dirs:
            for filename in ['netsage.json', 'netsage-snmp.json']:
                json_path = os.path.join(root, 'connections', filename)
                if not os.path.isfile(json_path):
                    if debug:
                        print(f"  [DEBUG] Not found (skipping): {json_path}")
                    continue

                try:
                    with open(json_path, 'r', encoding='utf-8') as f:
                        conn_data = json.load(f)

                    if "jsonData" not in conn_data or "index" not in conn_data["jsonData"]:
                        print(f"  [WARN] No jsonData.index found in {json_path}")
                        continue

                    old_index = conn_data["jsonData"]["index"]
                    base_index = org_dict[org_abbr]["index"]
                    new_index = base_index.replace("netsage", "snmp") if filename == "netsage-snmp.json" else base_index

                    if old_index == new_index:
                        print(f"  [SKIP] Index already correct in {json_path}: '{old_index}'")
                        continue

                    conn_data["jsonData"]["index"] = new_index
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(conn_data, f, indent=2)
                    print(f"  [UPDATE] {json_path}")
                    print(f"           index: '{old_index}' -> '{new_index}'")
                    updated += 1

                except Exception as e:
                    print(f"  [ERROR] Failed to update index in {json_path}: {e}")

    print(f"[INFO] Connection index update complete: {updated} file(s) modified")


def main():
    input_dir = 'dashboards'
    defaults_file = '/var/opt/netsage-grafana/default.json'

    parser = argparse.ArgumentParser(description='Replace Netsage strings in dashboard JSON files.')
    parser.add_argument('-org', required=True,
                        help='Organization abbreviation (e.g., TACC, FRGP, GPN).')
    parser.add_argument('-o', '--output-dir', required=True,
                        help='Path to the output directory.')
    parser.add_argument('--debug', action='store_true',
                        help='Print unified diffs and extra diagnostic info for each modified file.')
    args = parser.parse_args()

    org_abbr   = args.org
    debug      = args.debug
    output_dir = os.path.join(args.output_dir, org_abbr)

    org_dict = initialize_org_dict(org_list)

    if org_abbr not in org_dict:
        print(f"[ERROR] '{org_abbr}' is not a valid organization abbreviation.")
        print("Valid options:", ', '.join(sorted(org_dict.keys())))
        sys.exit(1)

    org_full_name    = org_dict[org_abbr]['org_name']
    default_src      = org_dict[org_abbr]['default_src']
    netsage_org_part = extract_parenthesized_part(org_full_name)
    encoded_org      = encode_org_for_url(org_full_name)

    print(f"[INFO] Organization : {org_abbr} ({org_full_name})")
    print(f"[INFO] Default src  : {default_src}")
    print(f"[INFO] Output dir   : {output_dir}")
    if debug:
        print(f"  [DEBUG] netsage_org_part : {netsage_org_part}")
        print(f"  [DEBUG] encoded_org      : {encoded_org}")
        print(f"  [DEBUG] index pattern    : {org_dict[org_abbr]['index']}")
        print(f"  [DEBUG] welcome type     : {org_dict[org_abbr]['welcome']}")

    if not os.path.isdir(input_dir):
        print(f"[ERROR] Input directory '{input_dir}' not found.", file=sys.stderr)
        sys.exit(1)

    current_dir = os.getcwd()

    # ------------------------------------------------------------------
    # Copy the correct welcome-*.json to dashboards/General/welcome.json
    # ------------------------------------------------------------------
    welcome_type = org_dict[org_abbr]["welcome"]
    welcome_map = {
        "all":    "../homepage/welcome-all.json",
        "flow":   "../homepage/welcome-flow.json",
        "globus": "../homepage/welcome-globus.json",
        "access": "../homepage/welcome-access.json"
    }

    if welcome_type not in welcome_map:
        print(f"[ERROR] Unknown welcome type '{welcome_type}' for org {org_abbr}")
        sys.exit(1)

    src_welcome  = os.path.join(current_dir, welcome_map[welcome_type])
    dest_welcome = os.path.join(input_dir, "org_main-org/dashboards/General", "welcome.json")

    try:
        os.makedirs(os.path.dirname(dest_welcome), exist_ok=True)
        shutil.copy2(src_welcome, dest_welcome)
        print(f"[INFO] Copied welcome file: {src_welcome} -> {dest_welcome}")
        process_file(
            dest_welcome, org_full_name, org_abbr, default_src,
            netsage_org_part, encoded_org,
            output_dir + '/org_main-org/dashboards',
            debug=debug
        )
    except Exception as e:
        print(f"[ERROR] Failed to copy welcome file: {e}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Clone the dashboard tree into the output directory
    # ------------------------------------------------------------------
    clone_dashboards(current_dir, output_dir + '/org_main-org', debug=debug)

    # ------------------------------------------------------------------
    # Create secure/ dir and copy the defaults file
    # ------------------------------------------------------------------
    secure_dir = output_dir + '/secure'
    try:
        os.makedirs(secure_dir, exist_ok=True)
        print(f"[INFO] Created directory: {secure_dir}")
    except OSError as e:
        print(f"[ERROR] Could not create secure directory: {e}", file=sys.stderr)
        sys.exit(1)

    df = os.path.join(secure_dir, 'default.json')
    print(f"[INFO] Copying defaults: {defaults_file} -> {df}")
    try:
        shutil.copy(defaults_file, df)
    except Exception as e:
        print(f"[WARN] Could not copy defaults file: {e}")

    # ------------------------------------------------------------------
    # Walk input_dir and process each eligible JSON file
    # ------------------------------------------------------------------
    processed = skipped = 0
    for root, _, files in os.walk(input_dir):
        if 'Archive' in root:
            if debug:
                print(f"  [DEBUG] Skipping Archive dir: {root}")
            continue

        for filename in files:
            if not filename.endswith('.json'):
                continue
            if filename not in include_files:
                if debug:
                    print(f"  [DEBUG] Skipping (not in include_files): {filename}")
                skipped += 1
                continue

            filepath = os.path.join(root, filename)
            process_file(
                filepath, org_full_name, org_abbr, default_src,
                netsage_org_part, encoded_org,
                output_dir + '/org_main-org/dashboards',
                debug=debug
            )
            processed += 1

    print(f"[INFO] Dashboard processing complete: {processed} processed, {skipped} skipped.")

    # ------------------------------------------------------------------
    # Update connection index patterns in output tree
    # ------------------------------------------------------------------
    update_connection_index(output_dir, org_dict, org_abbr, debug=debug)

    print("\n[INFO] Done.\n")


if __name__ == '__main__':
    main()

