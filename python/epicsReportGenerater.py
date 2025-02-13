import gitlab
import csv
import argparse

def get_epic_details(gl, group_id, epic_id):
    group = gl.groups.get(group_id)
    epic = group.epics.get(epic_id)
    return epic

def get_epic_notes(gl, group_id, epic_id):
    group = gl.groups.get(group_id)
    epic = group.epics.get(epic_id)
    return epic.notes.list(all=True)

def get_epic_events(gl, group_id, epic_id):
    """Fetches changes in the epic details (title, description, labels, etc.)."""
    group = gl.groups.get(group_id)
    epic = group.epics.get(epic_id)
    events = epic.resource_state_events.list(all=True)
    
    event_log = []
    for event in events:
        action = "Added" if event.action == "add" else "Removed"
        event_type = event.resource_type.capitalize()
        event_log.append({
            "Type": f"Epic {event_type} {action}",
            "Author": event.user['name'],
            "Date": event.created_at,
            "Content": event.resource_type if event.resource_type else "N/A"
        })
    
    return event_log

def get_epic_issues(gl, group_id, epic_id):
    """Fetches issues linked to an epic."""
    group = gl.groups.get(group_id)
    epic = group.epics.get(epic_id)
    return epic.issues()

def get_issue_events(issue):
    """Fetches label, assignee, and milestone change history for an issue."""
    events = issue.resource_state_events.list(all=True)
    event_log = []

    for event in events:
        action = "Added" if event.action == "add" else "Removed"
        event_type = event.resource_type.capitalize()

        if event_type in ["Label", "Assignee", "Milestone"]:
            event_log.append({
                "Type": f"{event_type} {action}",
                "Author": event.user['name'],
                "Date": event.created_at,
                "Content": event.resource_type if event.resource_type else "N/A"
            })
    
    return event_log

def generate_audit_report(gl, group_id, epic_id, output_file):
    """Generates an audit report and saves it to a CSV file."""
    epic = get_epic_details(gl, group_id, epic_id)
    notes = get_epic_notes(gl, group_id, epic_id)
    epic_events = get_epic_events(gl, group_id, epic_id)
    issues = get_epic_issues(gl, group_id, epic_id)

    with open(output_file, mode="w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["Type", "Author", "Date", "Content", "Last Updated", "Closed Date"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        # Epic details
        writer.writerow({"Type": "Epic Title", "Author": "", "Date": "", "Content": epic.title})
        writer.writerow({"Type": "Epic Description", "Author": "", "Date": "", "Content": epic.description})

        for event in epic_events:
            writer.writerow({
                "Type": event["Type"],
                "Author": event["Author"],
                "Date": event["Date"],
                "Content": event["Content"],
                "Last Updated": "",
                "Closed Date": ""
            })

        for note in notes:
            writer.writerow({
                "Type": "Comment" if note.system is False else "System Note",
                "Author": note.author["name"],
                "Date": note.created_at,
                "Content": note.body
            })

        # Linked Issues
        for issue in issues:
            writer.writerow({
                "Type": "Linked Issue",
                "Author": issue.author["name"],
                "Date": issue.created_at,
                "Last Updated": issue.updated_at,
                "Closed Date": issue.closed_at if issue.state == "closed" else "N/A"
                "Content": f"{issue.title} ({issue.web_url})"
            })

            issue_events = get_issue_events(issue)
            for event in issue_events:
                writer.writerow({
                    "Type": event["Type"],
                    "Author": event["Author"],
                    "Date": event["Date"],
                    "Content": event["Content"],
                    "Last Updated": "",
                    "Closed Date": ""
                })

    print(f"Audit report saved as {output_file}")

def main():
    """Main function to run the GitLab audit script."""
    parser = argparse.ArgumentParser(description="Generate an audit report for a GitLab epic")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-g", "--group", required=True, help="GitLab group ID containing the epic")
    parser.add_argument("-e", "--epic", required=True, help="Epic ID to generate the report for")
    parser.add_argument("-o", "--output", default="gitlab_epic_audit.csv", help="Output CSV file name")

    args = parser.parse_args()
    
    # Authenticate GitLab
    gl = gitlab.Gitlab(GITLAB_URL, private_token=args.token)

    # Generate audit report
    generate_audit_report(gl, args.group, args.epic, args.output)

if __name__ == "__main__":
    main()