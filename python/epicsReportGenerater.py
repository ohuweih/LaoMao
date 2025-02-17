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


def extract_checkboxes(description, section_title):
    """Extracts checked items from a specific checkbox section."""
    pattern = fr"## {section_title}.*?<!--.*?-->\s*\n([\s\S]*?)(?=\n## |\Z)"
    match = re.search(pattern, description, re.DOTALL)

    if not match:
        return "N/A"

    section_content = match.group(1)
    checked_items = re.findall(r"- \[x\] ([\w\s(),]+)", section_content)  # Match checked items

    return ", ".join(checked_items) if checked_items else "None"

def extract_description_points(description):
    ''' this is to regex out all things in the descriptions that does not have check boxes associated'''
    if not description:
        return {}


    extracted_data = {}


    patterns = {
        "Submission Date": r"## 2\. Submission Date.*?Insert date here:\s*`([\d]{2}-[\d]{2}-[\d]{4})`",
        "Business Owner": r"## 3\. Business Owner.*?<!--.*?-->\s*\n_([\w\s()@-]+)_",
        "Target Timeline": r"## 13\. Target Timeline.*?Insert date here:\s*`([\w]+\s+\d{1,2},\s*\d{4})`",
        "Detail Description": r"## 4\. Detailed Description\s*?<!--.*?-->\s*\n([\s\S]*?)(?=\n## |\Z)",
        "Justification": r"## 5\. Justification\s*<!--.*?-->\s*\n([\s\S]*?)(?=\n## |\Z)"
    }
   
    for key, pattern in patterns.items():
        match = re.search(pattern, description, re.DOTALL)
        extracted_data[key] = match.group(1).strip() if match else "N/A"

    extracted_data["Selected Programs"] = extract_checkboxes(description, "8. Program \\(Required\\)")
    extracted_data["Expedited"] = extract_checkboxes(description, "6. Expedited")
    extracted_data["Area"] = extract_checkboxes(description, "7. Area \\(Required\\)")
    extracted_data["Reason"] = extract_checkboxes(description, "9. Reason \\(Optional\\)")
    extracted_data["SOW"] = extract_checkboxes(description, "10. SOW \\(Optional\\)")
    extracted_data["Business Requirements"] = extract_checkboxes(description, "14. Business Requirements")
    extracted_data["Gate 1 Approvers"] = extract_checkboxes(description, "16. Gate 1 Approvers")
    extracted_data["BRD Approvers"] = extract_checkboxes(description, "19. BRD Approvers")
    extracted_data["Gate 2 Approvers"] = extract_checkboxes(description, "20. Gate 2 Approvers")
    extracted_data["Gate 3 Approvers"] = extract_checkboxes(description, "21. Gate 3 Approvers")
    extracted_data["Proceed to production Approvers"] = extract_checkboxes(description, "22. Proceed to production Approvers.")

    return extracted_data


def generate_audit_report(gl, group_id, epic_id, output_file):
    """Generates an audit report and saves it to a CSV file."""
    epic = get_epic_details(gl, group_id, epic_id)
    extracted_fields = extract_description_points(epic.description)
    label_data = extract_labels(epic)




    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Epic Title", "Creation Date", "Created By", "Last Updated", "Type", "Priority", "Status"] + list (extracted_fields.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"Epic Title": epic.title, "Creation Date": epic.created_at, "Created By": epic.author["name"], "Last Updated": epic.updated_at, "Type": label_data["Type"], "Priority": label_data["Priority"], "Status": label_data["Status"], **extracted_fields})

def main():


    """Main function to run the GitLab audit script."""
    parser = argparse.ArgumentParser(description="Generate an audit report for a GitLab epic")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-g", "--group", required=True, help="GitLab group ID containing the epic")
    parser.add_argument("-e", "--epic", required=True, help="Epic ID to generate the report for")
    parser.add_argument("-o", "--output", default="gitlab_epic_report.csv", help="Output CSV file name")


    args = parser.parse_args()
   
    # Authenticate GitLab
    gl = gitlab.Gitlab("https://gitlab.com", private_token=args.token)


    # Generate report
    generate_audit_report(gl, args.group, args.epic, args.output)


if __name__ == "__main__":
    main()
