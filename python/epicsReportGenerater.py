
import gitlab
import csv
import argparse
import re
import pandas as pd
import yaml
from datetime import datetime


def load_config():
    with open('config/report.yaml', "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)
        return config




def get_epic_details(gl, group_id, config):
    ''' Get the epic '''
    label_filters = set(config["labels"])


    from_date = datetime.strptime(config["fromDate"], "%m-%d-%Y")
    to_date = datetime.strptime(config["toDate"], "%m-%d-%Y")


    group = gl.groups.get(group_id)
    epics = group.epics.list(all=True)


    filtered_epics = []
    for epic in epics:
        if epic.start_date:
            epic_start_at = datetime.strptime(epic.start_date, "%Y-%m-%d")


            if from_date <= epic_start_at <= to_date and any(
                label in epic_label for epic_label in epic.labels for label in label_filters
                ):
                filtered_epics.append(epic)


    return filtered_epics




def extract_labels(epic):
    """Extracts all labels from the epic and categorizes important ones."""
    all_labels = epic.labels if epic.labels else []


    # Important labels to prioritize
    important_labels = {"Type": None, "Priority": None, "Status": None}


    # Identify and categorize important labels
    for label in all_labels:
        if label.lower().startswith("type:"):
            important_labels["Type"] = label.split("::", 1)[1].strip()
        elif label.lower().startswith("priority:"):
            important_labels["Priority"] = label.split("::", 1)[1].strip()
        elif "::status::" in label.lower():
            important_labels["Status"] = label.split("Status::", 1)[1].strip()


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


    for header, content in matches:
        clean_header = header.strip()


        if clean_header in exclude_headers:
            continue  # Skip excluded headers


        extracted_data[clean_header] = content if content.strip() else "N/A"


    return extracted_data




def generate_audit_report(gl, group_id, config, output_file):
    """Generates an audit report and saves it to a CSV file."""
    epics = get_epic_details(gl, group_id, config)
    today = datetime.utcnow().date()

    if not epics:
        print("No epics found")
        return


    extracted_fields = {}
    all_headers = set()
    for epic in epics:
        extracted_fields = extract_all_headers(epic.description)
        all_headers.update(extracted_fields.keys())
   
    fieldnames = ["Epic ID", "Epic Title", "Creation Date", "Created By", "Last Updated", "Type", "Priority", "Status", "Latest Note", "Prod Date", "Days Past Due", "Stakeholders","Start Date"] + sorted(all_headers)


    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()


        for epic in epics:
            participants = ", ".join([p["name"] for p in epic.participants()]) if hasattr(epic, "participants") else "N/A"
            extracted_fields = extract_all_headers(epic.description)
            label_data = extract_labels(epic)
            latest_note = get_latest_note(epic)
            writer.writerow({
                "Epic ID": epic.iid, 
                "Epic Title": epic.title, 
                "Creation Date": epic.created_at, 
                "Created By": epic.author["name"], 
                "Last Updated": epic.updated_at, 
                "Type": label_data["Type"], 
                "Priority": label_data["Priority"], 
                "Status": label_data["Status"], 
                **extracted_fields, 
                "Latest Note": latest_note, 
                "Start Date": epic.start_date if epic.start_date else "N/A",
                "Prod Date": epic.end_date if epic.end_date else "N/A", 
                "Stakeholders": participants,
                "Days Past Due": (
                    (today - datetime.strptime(epic.end_date, "%Y-%m-%d").date()).days
        if epic.end_date else "N/A"
                )
                })


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
    parser.add_argument("-o", "--output", default="gitlab_epic_report", help="Output CSV file name")


    args = parser.parse_args()
       # Authenticate GitLab
    gl = gitlab.Gitlab("https://gitlab.com", private_token=args.token)


    config = load_config()
    output_file = f"{args.output}_{config['fromDate']}_{config['toDate']}.csv"
    # Generate report
    generate_audit_report(gl, args.group, config, output_file)


    clean_csv_content(output_file)


if __name__ == "__main__":
    main()
