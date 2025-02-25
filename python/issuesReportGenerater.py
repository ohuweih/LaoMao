import gitlab
import csv
import argparse
import re
import pandas as pd
import yaml
from datetime import datetime


def load_config():
    """Load YAML config for filtering labels and date range."""
    with open('config/report.yaml', "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_issues_details(gl, project_id, config):
    """Retrieve all issues in a GitLab project matching labels and date range."""
    label_filters = set(config["labels"])
    print(label_filters)

    from_date = datetime.strptime(config["fromDate"], "%m-%d-%Y")
    to_date = datetime.strptime(config["toDate"], "%m-%d-%Y")

    project = gl.projects.get(project_id)

    all_issues = []
    page = 1
    while True:
        issues = project.issues.list(per_page=100, page=page)  # Request 100 issues per page
        if not issues:
            break
        all_issues.extend(issues)
        page += 1

    filtered_issues = []
    for issue in all_issues:
        issue_created_at = datetime.strptime(issue.created_at, "%Y-%m-%dT%H:%M:%S.%fZ")

        if from_date <= issue_created_at <= to_date and issue.labels and any(
            label in issue_label for issue_label in issue.labels for label in label_filters
        ):
            filtered_issues.append(issue)
    return filtered_issues


def extract_labels(issue):
    """Extracts all labels from the issue and categorizes important ones."""
    all_labels = issue.labels if issue.labels else []

    important_labels = {"Type": None, "Priority": None, "Status": None, "Release": None}

    for label in all_labels:
        if label.lower().startswith("type:"):
            important_labels["Type"] = label.split("::", 1)[1].strip()
        elif label.lower().startswith("priority:"):
            important_labels["Priority"] = label.split("::", 1)[1].strip()
        elif "::status::" in label.lower():
            important_labels["Status"] = label.split("Status::", 1)[1].strip()
        elif label.lower().startswith("release:"):
            important_labels["Release"] = label.split("::", 1)[1].strip()

    for key in important_labels:
        if not important_labels[key]:
            important_labels[key] = "N/A"

    return {
        "All Labels": ", ".join(all_labels) if all_labels else "None",
        "Type": important_labels["Type"],
        "Priority": important_labels["Priority"],
        "Status": important_labels["Status"],
        "Release": important_labels["Release"]
    }


def get_latest_comment(issue):
    """Get the latest user comment (not system notes)."""
    try:
        page = 1
        while True:
            notes = issue.notes.list(sort="desc", per_page=50, page=page)
            if not notes:
                break
            for note in notes:
                if not note.system:
                    return note.body.strip()
            page += 1
    except:
        return "No user comments available"


def extract_all_headers(description):
    """Extracts all sections dynamically and filters out unwanted ones."""
    if not description:
        return {}

    extracted_data = {}

    exclude_headers = ["Change History", "References", "Attachments"]

    pattern = r"##\s*\d+\.\s*([^\n]+)\n([\s\S]*?)(?=\n## |\Z)"
    matches = re.findall(pattern, description, re.MULTILINE)

    for header, content in matches:
        clean_header = header.strip()
        if clean_header in exclude_headers:
            continue  # Skip excluded headers
        extracted_data[clean_header] = content if content.strip() else "N/A"

    return extracted_data


def get_related_issues(issue, label_filters):
    """Retrieve related issues that match specified labels."""
    try:
        all_related = []
        page = 1
        while True:
            related_issues = issue.related_issues(per_page=100, page=page)
            if not related_issues:
                break
            all_related.extend(related_issues)
            page += 1

        filtered_related = [
            f"{related.iid}: {related.title}"
            for related in all_related
            if related.labels and any(label in related.labels for label in label_filters)
        ]

        return ", ".join(filtered_related) if filtered_related else "N/A"
    except:
        return "N/A"


def generate_issues_report(gl, project_id, config, output_file):
    """Generates an issue report and saves it to a CSV file."""
    issues = get_issues_details(gl, project_id, config)
    today = datetime.utcnow().date()

    if not issues:
        print("No issues found")
        return

    extracted_fields = {}
    all_headers = set()
    for issue in issues:
        extracted_fields = extract_all_headers(issue.description)
        all_headers.update(extracted_fields.keys())

    fieldnames = ["Issue ID", "Issue Title", "Assignees", "Created Date", "Created By", "Last Updated", "Type", "Priority", "Status", "Release", "Latest Comment", "Due Date", "Days Past Due", "Related Issues"] + sorted(all_headers)

    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for issue in issues:
            extracted_fields = extract_all_headers(issue.description)
            label_data = extract_labels(issue)
            latest_comment = get_latest_comment(issue)
            related_issues = get_related_issues(issue, set(config["labels"]))
            assignees = ", ".join([assignee["name"] for assignee in issue.assignees]) if issue.assignees else "Unassigned"
            
            writer.writerow({
                "Issue ID": issue.iid,
                "Issue Title": issue.title,
                "Created Date": issue.created_at,
                "Assignees": assignees,
                "Created By": issue.author["name"],
                "Last Updated": issue.updated_at,
                "Type": label_data["Type"],
                "Priority": label_data["Priority"],
                "Status": label_data["Status"],
                "Release": label_data["Release"],
                **extracted_fields,
                "Latest Comment": latest_comment,
                "Due Date": issue.due_date if issue.due_date else "N/A",
                "Days Past Due": (
                    (today - datetime.strptime(issue.due_date, "%Y-%m-%d").date()).days
                    if issue.due_date else "N/A"
                ),
                "Related Issues": related_issues
            })

    print(f"Report saved as {output_file}")


def clean_csv_content(file_path):
    """Cleans CSV content after writing."""
    df = pd.read_csv(file_path, dtype=str)

    def clean_text(text):
        if pd.isna(text):
            return ""
        text = text.replace("\u00A0", " ").replace("\r", "").strip()
        text = re.sub(r"<!--[\s\S]*?-->", "", text, flags=re.DOTALL)
        text = re.sub(r"(?i)`Insert\s*date\s*here:`\s*", "", text)
        text = re.sub(r"`([\w\s,]+)`", r"\1", text)
        text = re.sub(r"_([\w\s()]+)_", r"\1", text)
        text = re.sub(r"- \[\s?\] .*", "", text, flags=re.IGNORECASE)
        return text.strip()

    df = df.applymap(clean_text)
    df.to_csv(file_path, index=False, encoding="utf-8")
    print(f"Cleaned report saved as {file_path}")


def main():
    """Main function to run the GitLab issues report."""
    parser = argparse.ArgumentParser(description="Generate an issue report for a GitLab project")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-p", "--project", required=True, help="GitLab project ID")
    parser.add_argument("-o", "--output", default="gitlab_issues_report", help="Output CSV file name")

    args = parser.parse_args()
    gl = gitlab.Gitlab("https://gitlab.com", private_token=args.token)

    config = load_config()
    output_file = f"{args.output}_{config['fromDate']}_{config['toDate']}.csv"

    generate_issues_report(gl, args.project, config, output_file)
    clean_csv_content(output_file)


if __name__ == "__main__":
    main()
