import gitlab
import csv
import argparse

import re


def get_epic_details(gl, group_id, epic_id):
    ''' Get the epic '''
    group = gl.groups.get(group_id)
    epic = group.epics.get(epic_id)
    return epic

def extract_labels(epic):
    """Extracts all labels from the epic and categorizes important ones."""
    all_labels = epic.labels if epic.labels else []

    # Important labels to prioritize
    important_labels = {"Type": None, "Priority": None, "Status": None}

    # Identify and categorize important labels
    for label in all_labels:
        if label.lower().startswith("type:"):
            important_labels["Type"] = label.split(":", 1)[1].strip()
        elif label.lower().startswith("priority:"):
            important_labels["Priority"] = label.split(":", 1)[1].strip()
        elif "::Status::" in label.lower():
            important_labels["Status"] = label.strip()

    # Convert None values to 'N/A' if they weren't found
    for key in important_labels:
        if not important_labels[key]:
            important_labels[key] = "N/A"

    return {
        "All Labels": ", ".join(all_labels) if all_labels else "None",
        "Type": important_labels["Type"],
        "Priority": important_labels["Priority"],
        "Status": important_labels["Status"],
    }

def extract_selected_programs(description):
    ''' this is to regex out all things in the description that has check boxes associated'''
    pattern = r"## 8\. Program \(Required\).*?<!--.*?-->\s*\n([\s\S]*?)(?=\n## |\Z)"  # Capture the list until the next header
    match = re.search(pattern, description, re.DOTALL)

    if not match:
        return "N/A"

    program_section = match.group(1)
    checked_items = re.findall(r"- \[x\] ([\w\s]+)", program_section)  # Match checked items
    return ", ".join(checked_items) if checked_items else "None"

def extract_description_points(description):
    ''' this is to regex out all things in the descriptions that does not have check boxes associated'''
    if not description:
        return {}

    extracted_data = {}

    patterns = {
        "Detail Description": r"## 4\. Detailed Description\s*?<!--.*?-->\s*\n([\s\S]*?)(?=\n## |\Z)",
        "Submission Date": r"## 2\. Submission Date.*?Insert date here:\s*`([\d]{2}-[\d]{2}-[\d]{4})`",
        "Business Owner": r"## 3\. Business Owner.*?<!--.*?-->\s*\n_([\w\s()@-]+)_"
    }
    
    for key, pattern in patterns.items():
        match = re.search(pattern, description, re.DOTALL)
        extracted_data[key] = match.group(1).strip() if match else "N/A"


    extracted_data["Selected Programs"] = extract_selected_programs(description)
   
    return extracted_data


def generate_audit_report(gl, group_id, epic_id, output_file):
    """Generates an audit report and saves it to a CSV file."""
    epic = get_epic_details(gl, group_id, epic_id)
    extracted_fields = extract_description_points(epic.description)
    label_data = extract_labels(epic) 


    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Epic Title", "Creation Date", "Last Updated", "Type", "Priority", "Status"] + list (extracted_fields.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


                # Epic details
        writer.writerow({"Epic Title": epic.title, "Creation Date": epic.created_at, "Last Updated": epic.updated_at, "Type": label_data["Type"], "Priority": label_data["Priority"], "Status": label_data["Status"], **extracted_fields})


def main():

    """Main function to run the GitLab audit script."""
    parser = argparse.ArgumentParser(description="Generate an audit report for a GitLab epic")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-g", "--group", required=True, help="GitLab group ID containing the epic")
    parser.add_argument("-e", "--epic", required=True, help="Epic ID to generate the report for")
    parser.add_argument("-o", "--output", default="gitlab_epic_report.csv", help="Output CSV file name")

    args = parser.parse_args()
    
    # Authenticate GitLab
    gl = gitlab.Gitlab(GITLAB_URL, private_token=args.token)

    # Generate report
    generate_audit_report(gl, args.group, args.epic, args.output)

if __name__ == "__main__":
    main()