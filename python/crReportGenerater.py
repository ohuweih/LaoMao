import gitlab
import argparse
import re
import pandas as pd
import yaml
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def load_config():
    """Load YAML config for filtering labels and date range."""
    with open('config/report.yaml', "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_issues_details(gl, project_id, config):
    """Retrieve all issues in a GitLab project matching labels and date range."""
    cr_filter = f"CR::{config['CR Number']}"
    label_filter = "Type::Requirement"
    print(cr_filter)
    print(label_filter)

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


        if from_date <= issue_created_at <= to_date and issue.labels:
            for label in issue.labels:
                if cr_filter == label:
                    print(label)
                    if label_filter in issue.labels:
                        print(label)
                        filtered_issues.append(issue)
    print(filtered_issues)
    return filtered_issues


def clean_text(text):
    """Applies regex to remove comments and 'Insert date here:' from text fields."""
    if pd.isna(text):
        return ""  # Handle NaN values

    text = text.replace("\u00A0", " ").replace("\r", "").strip()  # Normalize spaces & line endings
    text = re.sub(r"^##\s*(.*)", r"<b>\1</b><br/>", text, flags=re.MULTILINE)
    text = re.sub(r"(<b>.*?</b><br/>(.*?))(?=(<b>|$))", r"\1<br/><br/>", text, flags=re.DOTALL)
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


def generate_brd_pdf(gl, project_id, config, output_file):
    """Generates an issue report and saves it to a PDF file."""
    issues = get_issues_details(gl, project_id, config)
    today = datetime.utcnow().date()

    if not issues:
        print("No issues found")
        return
    
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # Define custom styles for modern look
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Title'],
        fontSize=18,
        alignment=1,  # Center alignment
        textColor=colors.HexColor("#333333")
    )

    header_style = ParagraphStyle(
        'Header',
        parent=styles['Heading2'],
        fontSize=12,
        alignment=1,  # Center alignment
        textColor=colors.whitesmoke,
        spaceAfter=10
    )

    cell_style = ParagraphStyle(
        'Cell',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=1,  # Center alignment
        textColor=colors.HexColor("#333333")
    )

    # Title
    title = Paragraph(f"BR Report for CR {config['CR Number']}", title_style)
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Table headers
    data = [
        [Paragraph("<b>Issue ID</b>", header_style), 
         Paragraph("<b>Issue Title</b>", header_style), 
         Paragraph("<b>Issue Description</b>", header_style)]
    ]

    # Set a character limit per cell for wrapping
    character_limit = 150

    # Add issue details to the data with text wrapping
    for issue in issues:
        clean_description = clean_text(issue.description or "N/A")
        wrapped_description = "<br/>".join([clean_description[i:i + character_limit] for i in range(0, len(clean_description), character_limit)])
        wrapped_title = "<br/>".join([issue.title[i:i + character_limit] for i in range(0, len(issue.title), character_limit)])
        
        data.append([
            Paragraph(str(issue.iid), cell_style),
            Paragraph(wrapped_title, cell_style),
            Paragraph(wrapped_description, cell_style)
        ])

    # Create a modern-style table
    data = [data[0]] + data[1:][::-1] 
    table = Table(data, colWidths=[50, 150, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#CCCCCC")),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#f9f9f9")),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)

    doc.build(elements)
    print(f"PDF report saved as {output_file}")
        

def main():
    """Main function to run the GitLab issues report."""
    parser = argparse.ArgumentParser(description="Generate an issue report for a GitLab project")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for authentication")
    parser.add_argument("-p", "--project", required=True, help="GitLab project ID")
    parser.add_argument("-o", "--output", default="gitlab_brd_report", help="Output CSV file name")

    args = parser.parse_args()
    gl = gitlab.Gitlab("https://gitlab.com", private_token=args.token)

    config = load_config()
    output_file = f"{args.output}_CR{config['CR Number']}_{config['fromDate']}_{config['toDate']}.pdf"

    generate_brd_pdf(gl, args.project, config, output_file)


if __name__ == "__main__":
    main()
