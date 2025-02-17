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
        elif "::status::" in label.lower():
            parts = label.partition("::status::")
            important_labels["Status"] = parts[0].strip() if parts[0] else "N/A"


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


def get_latest_note(epic):
    """Get the latest note on the epic"""
    notes = epic.notes.list(sort="desc", per_page=1)  # Get the most recent note
    return notes[0].body.strip() if notes else "No notes available"


def clean_content(content):
    """Format content to look clean"""
    cleaned_content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)  
    cleaned_content = re.sub(r"Insert date here:\s*", "", content, flags=re.IGNORECASE)

    return cleaned_content.strip()


def extract_all_headers(description):
    """Extracts all sections dynamically and filters out unwanted ones."""
    if not description:
        return {}

    extracted_data = {}

    # List of headers we want to ignore
    exclude_headers = [
        "Change History", "References", "Attachments"
    ]

    # Find all headers in the description
    pattern = r"##\s*\d+\.\s*([^\n]+)\n([\s\S]*?)(?=\n## |\Z)"
    matches = re.findall(pattern, description, re.MULTILINE)

    for full_match, header, content in matches:
        clean_header = header.strip()

        if clean_header in exclude_headers:
            continue  # Skip excluded headers

        extracted_data[clean_header] = content.strip() if content.strip() else "N/A"

    return extracted_data


def generate_audit_report(gl, group_id, epic_id, output_file):
    """Generates an audit report and saves it to a CSV file."""
    epic = get_epic_details(gl, group_id, epic_id)
    extracted_fields = extract_all_headers(epic.description)
    label_data = extract_labels(epic)
    latest_note = get_latest_note(epic) 

    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Epic Title", "Creation Date", "Created By", "Last Updated", "Type", "Priority", "Status", "Latest Note"] + list (extracted_fields.keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow({"Epic Title": epic.title, "Creation Date": epic.created_at, "Created By": epic.author["name"], "Last Updated": epic.updated_at, "Type": label_data["Type"], "Priority": label_data["Priority"], "Status": label_data["Status"], **extracted_fields, "Latest Note": latest_note,})


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
