import gitlab
import csv
import argparse
import re
import pandas as pd
import yaml
from datetime import datetime
from pprint import pprint


def load_config(number):
    yaml_config = f'''
    labels:
      - "Release::{number}"
      - "Type::Release"
    '''
   
    config = yaml.safe_load(yaml_config)
    return config


def get_epic_details(gl, group_id, config):
    ''' Get the epic '''
    label_filters = set(config["labels"])


    group = gl.groups.get(group_id)
    epics = group.epics.list(all=True)


    all_epics = []
    page = 1
    while True:
        epics = group.epics.list(per_page=100, page=page)  # Request 100 items per page
        if not epics:
            break
        all_epics.extend(epics)
        page += 1


    filtered_epics = []
    for epic in all_epics:

        if epic.labels and all(
            any(label in epic_label for epic_label in epic.labels) for label in label_filters
            ):
            filtered_epics.append(epic)

    return filtered_epics

## probably can remove
def extract_labels(epic):
    """Extracts all labels from the epic and categorizes important ones."""
    print(f"The Data: {epic}")
    all_labels = epic["labels"] if epic["labels"] else []

    # Important labels to prioritize
    important_labels = {"Type": None, "Priority": None, "Status": None, "Release": None, "CR": None}

    # Identify and categorize important labels
    for label in all_labels:
        if label.lower().startswith("type:"):
            important_labels["Type"] = label.split("::", 1)[1].strip()
        elif label.lower().startswith("priority:"):
            important_labels["Priority"] = label.split("::", 1)[1].strip()
        elif "::status::" in label.lower():
            important_labels["Status"] = label.split("Status::", 1)[1].strip()
        elif label.lower().startswith("release:"):
            important_labels["Release"] = label.split("::", 1)[1].strip()
        elif label.lower().startswith("cr:"):
            important_labels["CR"] = label.split("::", 1)[1].strip()

    # Convert None values to 'N/A' if they weren't found
    for key in important_labels:
        if not important_labels[key]:
            important_labels[key] = "N/A"

    return {
        "All Labels": ", ".join(all_labels) if all_labels else "None",
        "Type": important_labels["Type"],
        "Priority": important_labels["Priority"],
        "Status": important_labels["Status"],
        "Release": important_labels["Release"],
        "CR": important_labels["CR"]
    }

# Can remove
def get_latest_note(epic):
    """Get the latest note on the epic"""
    try:
        notes = epic.notes.list(sort="desc", per_page=20)
        for note in notes:
            if not note.system:
                return note.body.strip()

        return "No user comments available"
    except:
        return "No user comments available"


def extract_all_headers(description):
    """Extract specific sections from the description regardless of Markdown level or numbering."""
    if not description:
        return {}

    extracted_data = {}

    # Headers you care about (case-insensitive)
    target_headers = ["Business Objective", "Description", "Module", "Design Document"]

    # Match headers like "# Description", "## 2. Design Document", "### 3.1 Business Objective"
    pattern = r"#+\s*(?:\d+(?:\.\d+)*\.\s*)?([^\n]+)\n([\s\S]*?)(?=\n#+\s*(?:\d+(?:\.\d+)*\.\s*)?[^\n]+\n|\Z)"

    matches = re.findall(pattern, description, re.MULTILINE)

    for header, content in matches:
        header_clean = header.strip().lower()
        for target in target_headers:
            if target.lower() == header_clean:
                extracted_data[target] = content.strip() if content.strip() else "N/A"

    return extracted_data


def collect_linked_epics(gl, group_id, epic_iid, visited_epics=None, visited_issues=None, depth=1, max_depth=6):
    if visited_epics is None:
        visited_epics = set()
    if visited_issues is None:
        visited_issues = set()

    if epic_iid in visited_epics or depth > max_depth:
        return [], []

    visited_epics.add(epic_iid)
    collected_epics = [f"{'  ' * depth}Epic {epic_iid}"]
    collected_issues = []

    related_epics_url = f"/groups/{group_id}/epics/{epic_iid}/related_epics"
    try:
        related_epics = gl.http_get(related_epics_url)
    except Exception as e:
        print(f"Error fetching related epics for Epic {epic_iid}: {e}")
        return [], []

    for linked in related_epics:
        linked_id = linked["iid"]

        if linked_id in visited_epics:
            continue

        collected_epics.append(f"{'  ' * depth}Linked Epic {linked_id}")

        # Get child issues
        try:
            child_issues_url = f"/groups/{group_id}/epics/{linked_id}/issues"
            child_issues = gl.http_get(child_issues_url)
        except Exception as e:
            print(f"Error fetching issues for Epic {linked_id}: {e}")
            child_issues = []

        issue_refs = [{"project_id": i["project_id"], "iid": i["iid"]} for i in child_issues]

        # Recurse to collect linked issues
        linked_issues = collect_linked_issues(gl, {}, issue_refs, visited_issues, depth + 1, max_depth)
        collected_issues += linked_issues

        # Recurse into deeper epics
        deeper_epics, deeper_issues = collect_linked_epics(gl, group_id, linked_id, visited_epics, visited_issues, depth + 1, max_depth)
        collected_epics += deeper_epics
        collected_issues += deeper_issues

    return collected_epics, collected_issues

        

def collect_linked_issues(gl, project_id_lookup, issue_refs, visited_issues=None, depth=1, max_depth=6, parent_key=None):
    print(f"Starting linked issues flow: {issue_refs}")
    if visited_issues is None:
        visited_issues = set()

    collected_issues = []

    for ref in issue_refs:
        project_id = ref["project_id"]
        issue_iid = ref["iid"]
        unique_key = f"{project_id}:{issue_iid}"
        
        print(visited_issues)
        if unique_key == parent_key:
            pass  # Allow entry issue to pass through
        elif unique_key in visited_issues or depth > max_depth:
            continue

        visited_issues.add(unique_key)

        try:
            print("Trying linked issue loop")
            issue = gl.projects.get(project_id).issues.get(issue_iid)
            collected_issues.append(issue.attributes)
            
            print(f"{'  ' * depth}Linked Issue {issue_iid} in project {project_id}")

            # Get related (linked) issues
            linked_url = f"/projects/{project_id}/issues/{issue_iid}/links"
            linked = gl.http_get(linked_url)
            next_refs = [{"project_id": l["project_id"], "iid": l["iid"]} for l in linked]
            issue_data = issue.attributes.copy()
            issue_data["_links_to"] = next_refs 
            links_data = issue_data["_links_to"]
            print(f"links to data: {links_data}")
            collected_issues.append(issue_data)
            # Recurse
            collected_issues += collect_linked_issues(gl, project_id_lookup, next_refs, visited_issues, depth + 1, max_depth)

        except Exception as e:
            print(f"Error loading issue {project_id}/{issue_iid}: {e}")
            continue

    return collected_issues



def collect_all_linked_items(gl, group_id, epic):
    print(f"Starting with Parent Epic {epic.iid}: {epic.title}")
    visited_epics = set()
    visited_issues = set()

    # Kick off collection
    epics, issues = collect_linked_epics(gl, group_id, epic.iid, visited_epics, visited_issues)

    return {
        "epics": epics,
        "issues": issues
    }


def write_issue_recursive(writer, issue, issue_lookup, visited, all_headers, depth=0):
    issue_key = f"{issue['project_id']}:{issue['iid']}"
    if issue_key in visited:
        return
    visited.add(issue_key)

    label_data = extract_labels(issue)
    extracted_fields = extract_all_headers(issue.get("description", ""))

    all_headers.update(extracted_fields.keys())

    row = {
        "Issue ID": f"{'→' * depth} {issue['iid']}" if depth > 0 else issue["iid"],
        "Release #": label_data["Release"],
        "CR #": label_data["CR"],
        **extracted_fields
    }

    writer.writerow(row)

    # Now handle first linked issue
    linked_refs = issue.get("_links_to", [])
    for linked_ref in linked_refs:
        linked_key = f"{linked_ref['project_id']}:{linked_ref['iid']}"
        linked_issue = issue_lookup.get(linked_key)
        if linked_issue:
            write_issue_recursive(writer, linked_issue, issue_lookup, visited, all_headers, depth + 1)




def generate_audit_report(gl, group_id, config, output_file):
    epics = get_epic_details(gl, group_id, config)
    if not epics:
        print("No epics found")
        return

    all_issues = []
    print("Traversing epics and collecting issues...")

    for epic in epics:
        linked_items = collect_all_linked_items(gl, group_id, epic)
        all_issues.extend(linked_items["issues"])

    issue_lookup = {
        f"{i['project_id']}:{i['iid']}": i for i in all_issues
    }

    visited = set()
    all_headers = set()
    all_rows = []

    # Recursively walk and collect all rows
    def walk_and_collect(issue, depth=0):
        issue_key = f"{issue['project_id']}:{issue['iid']}"
        if issue_key in visited:
            return
        visited.add(issue_key)

        label_data = extract_labels(issue)
        extracted_fields = extract_all_headers(issue.get("description", ""))
        all_headers.update(extracted_fields.keys())

        row = {
            "Issue ID": f"{'→' * depth} {issue['iid']}" if depth > 0 else issue["iid"],
            "Issue Title": issue['title'],
            "Release #": label_data["Release"],
            "CR #": label_data["CR"],
            **extracted_fields
        }
        all_rows.append(row)

        linked_refs = issue.get("_links_to", [])
        for linked_ref in linked_refs:
            linked_key = f"{linked_ref['project_id']}:{linked_ref['iid']}"
            linked_issue = issue_lookup.get(linked_key)
            if linked_issue:
                walk_and_collect(linked_issue, depth + 1)

    for issue in all_issues:
        walk_and_collect(issue)

    # Now we know all headers
    fieldnames = ["Issue ID", "Issue Title", "Release #", "CR #"] + sorted(all_headers)

    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Report saved as {output_file}")




def clean_csv_content(file_path):
    """Loads CSV, cleans all fields, and rewrites it."""
    df = pd.read_csv(file_path, dtype=str)  # Load CSV as a DataFrame (all text)

    def clean_text(text):
        """Applies regex to remove comments and 'Insert date here:' from text fields."""
        if pd.isna(text):
            return ""  # Handle NaN values

        text = text.replace("\u00A0", " ").replace("\r", "").strip()  # Normalize spaces & line endings
        text = re.sub(r"<!--[\s\S]*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"(?i)`Insert\s*date\s*here:`\s*", "", text)
        checkedCheckboxes = re.findall(r"- \[x\] (.+)", text)  # Extract only checked items
        text = re.sub(r"- \[\s?\] .*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"_([\w\s()]+)_", r"\1", text)
        text = re.sub(r"`(\d{2}-\d{2}-\d{4})`", r"\1", text)
        text = re.sub(r" \\", "", text)
        text = re.sub(r"Enter Text here","",text, flags=re.IGNORECASE)
        text = re.sub(r"`([\w\s,]+)`", r"\1", text)
        if checkedCheckboxes:
          text = ", ".join(checkedCheckboxes)  # Keep checked items as a comma-separated string
        else:
           text = text.strip()
        return text.strip()

    # Apply cleaning to every text field in the DataFrame
    df = df.applymap(clean_text)

    # Save cleaned CSV
    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"Cleaned report saved as {file_path}")

def main():
    """Main function to run the GitLab audit script."""
    parser = argparse.ArgumentParser(description="Generate an audit report for a GitLab epic")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-g", "--group", required=True, help="GitLab group ID containing the epic")
    parser.add_argument("-o", "--output", default="release", help="Output CSV file name")
    parser.add_argument("-n", "--number", required=True, help="Release number to report on")

    args = parser.parse_args()
       # Authenticate GitLab
    gl = gitlab.Gitlab("https://gitlab.com", private_token=args.token)

    config = load_config(args.number)
    output_file = f"{args.output}_{args.number}_report.csv"
    # Generate report
    generate_audit_report(gl, args.group, config, output_file)
    clean_csv_content(output_file)

if __name__ == "__main__":
    main()

