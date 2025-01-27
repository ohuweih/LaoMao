import requests
import argparse
from datetime import date, datetime, timedelta
import yaml


def loadFile():
    '''
    Loads a file and returns a yaml object
    
        Parameters:
            file: Current hard coded to ./config/issuesConfig.yaml
            
        Returns:
            config: Yaml object
    '''
    with open('./config/issuesConfig.yaml', 'r') as file:
        config = yaml.safe_load(file)
    return config


def isBusinessDay(check_date):
    '''
    Returns a date if its a business day and not a holiday 
    
        Parameters:
            check_date: The date of we will alert on if a weekday or not a holiday 
            
        Returns:
            check_date.weekday(): dateTime
    '''
    business_days = {0, 1, 2, 3, 4} # Monday to Friday
    holidays= {
        date(2025, 1, 1),       # New Years day
        date(2025, 1, 20),      # Martin Luther King Jr. Day
        date(2025, 4, 18),      # State Holiday
        date(2025, 5, 26),      # Memorial Day
        date(2025, 6, 19),      # Juneteenth
        date(2025, 7, 4),       # Independence Day
        date(2025, 9, 1),       # Labor Day
        date(2025, 10, 13),     # Columbus Day
        date(2025, 11, 11),     # Veterans Day
        date(2025, 11, 27),     # Thanksgiving Day
        date(2025, 11, 28),     # State Holiday
        date(2025, 12, 25),     # Christmas day
        date(2025, 12, 26),     # Washington's Birthday

    }
    return check_date.weekday() in business_days and check_date not in holidays


def subtractBusinessDay(start_date, business_days_to_subtract):
    '''
    Returns a date if its a business day and not a holiday 
    
        Parameters:
            start_date: Todays date
            business_days_to_subtract: The amount of days we set as a threshold for alerting
            
        Returns:
            current_date: the current date as long as its not a weekend or holiday
    '''
    current_date = start_date
    days_subtracted = 0
    while days_subtracted < business_days_to_subtract:
        current_date -= timedelta(days=1)
        if isBusinessDay(current_date):
            days_subtracted += 1
    return current_date


def getIssues(project_id, inital_date, base_url, headers):
    '''
    Returns a list of issues from gitlab
    
        Parameters:
            project_id: Gitlabs project id
            inital_date: The date we start checking for issues.
            base_url: Gitlab api endpoint
            headers: The headers we pass to our request.get, In our case its just our api token
            
        Returns:
            issues: A list of issues from Gitlab
    '''
    params = {"created_before": inital_date}
    response = requests.get(base_url, params=params, headers=headers)
    issues = response.json()
    if response.status_code == 200:
        while "next" in response.links:
            print("Iterating though project Issues")
            response = requests.get(response.links["next"]["url"], headers=headers)
            issues.extend(response.json())
    else:
        print(f"Error fetching issues, Status Code: {response.status_code}, Response Text: {response.text}")
        return response
    return issues


def addComment(comment, base_url, issueId, headers, title, label, web_url):
    '''
    Puts a comment on an issue in gitlab
    
        Parameters:
            comment: The comment to add to the issue in gitlab
            base_url: Gitlab api endpoint
            issueId: The uniq id of our gitlab issue
            headers: The headers we pass to our request.post, In our case its just our api token
            title: the title of the gitlab issue
    '''
    print("Last auto comment past date theshold")
    print("Adding new comment")

    comment_data = {
        "body": f"~{label}<br> {web_url}<br> {comment}"
    }
    comment_response = requests.post(
    f"{base_url}/{issueId}/notes",
        headers=headers,
        json=comment_data
    )
    if comment_response.status_code == 201 or comment_response.status_code == 202:
        print(f"Comment added to issue {issueId} Title: {title} successfully")
    else:
        print(f"Failed to add comment to issue {issueId} Title: {title}, Status Code: {comment_response.status_code}, Response Text: {comment_response.text}")


def addLabel(existing_labels, label, base_url, issueId, headers):
    '''
    Puts a label on an issue in gitlab
    
        Parameters:
            existing_labels: A list of labels that are already attached to the gitlab issue
            label: The label to add to the gitlab issue
            base_url: Gitlab api endpoint
            issueId: The uniq id of our gitlab issue
            headers: The headers we pass to our request.post, In our case its just our api token
    '''
    update_labels = existing_labels + [label] if label not in existing_labels else existing_labels

    label_data = {"labels": ",".join(update_labels)}
    label_response = requests.put(
        f"{base_url}/{issueId}",
        headers=headers,
        json=label_data
    )

    if label_response.status_code == 200:
        print(f"Label '{label}' added to issue {issueId} seccessfully!")
    else:
        print(f"Failed to add label to issue {issueId}, Status Code: {label_response.status_code}, Response Text: {label_response.text}")


def getComments(base_url, issueId, headers):
    '''
    Return the comments on a gitlab issue
    
        Parameters:
            base_url: Gitlab api endpoint
            issueId: The uniq id of our gitlab issue
            headers: The headers we pass to our request.post, In our case its just our api token

        Returns:
            comment_response: the comments on a git lab issue
    '''
    comments_url = f"{base_url}/{issueId}/notes"
    comment_response = requests.get(comments_url, headers=headers)

    return comment_response


def updateIssues(token):
    '''
    Updates issues in gitlab based of label and updated date
    
        Parameters:
            token: Auth token for gitlab api
    '''
    config = loadFile()
    if config['projects']:
        headers = {"PRIVATE-TOKEN": token}
        print(f"Projects found, Iterating through them")
        for project in config['projects']:
            print(f"Running through project {project['projectId']}, Checking for issues that need to be updated")
            base_url = f"https://gitlab.com/api/v4/projects/{project['projectId']}/issues"

            # finding date time for 10 days ago
            inital_date = str((datetime.now() - timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%S'))
            createdIssues = getIssues(project['projectId'], inital_date, base_url, headers)
            for issue in createdIssues:
                # Match on open issues
                if issue['state'] == "opened":
                    issueId = issue['iid']
                    updated_at = issue['updated_at']
                    labels = issue['labels']
                    for label in labels:
                        for configLabel in project['labels']:
                            if label == configLabel['name']:
                                secondReminderDate = configLabel['secondReminderDate']
                                today = date.today()
                                past_second_business_date = str(subtractBusinessDay(today, secondReminderDate))
                                secondReminderDate = configLabel['firstReminderDate']
                                past_first_business_date = str(subtractBusinessDay(today, secondReminderDate))

                                ### Second update here ###
                                if updated_at <= past_second_business_date:
                                    print("Checking for second update")
                                    ### Start matching on comments here ###
                                    comment_response = getComments(base_url, issueId, headers)
                                

                                    if comment_response.status_code == 200:
                                        comments = comment_response.json()
                                        matched_comment = None

                                        for comment in comments:
                                            if configLabel['firstComment'] in comment['body']:
                                                matched_comment = comment
                                                break

                                        if matched_comment:
                                            comment_date =  matched_comment['created_at']
                                            if str(datetime.now()) > comment_date + str(timedelta(days=secondReminderDate)):
                                                comment = configLabel['secondComment']
                                                title = issue['title']
                                                web_url = issue['web_url']

                                                addComment(comment, base_url, issueId, headers, title, label, web_url)
                                                
                                                # Add label to ticket just in case its not on there already.
                                                label = project['labelTag']
                                                existing_labels = issue.get("labels",[])
                                                addLabel(existing_labels, label, base_url, issueId, headers)
                                
                                ### Initial update here ###
                                if updated_at <= past_first_business_date:
                                    print("Checking if we need to do initial update")
                                    print("Found one")
                                    print(f"Issue ID: {issueId}, Title: {issue['title']}, needs to be updated.")
                                        
                                    # This is the comment we will add to the ticket we matched on
                                    comment = configLabel['secondComment']
                                    title = issue['title']
                                    web_url = issue['web_url']
                                    addComment(comment, base_url, issueId, headers, title, label, web_url)
                                    
                                    # Add label to ticket. This is set for tracking purpose.
                                    label = project['labelTag']
                                    existing_labels = issue.get("labels",[])
                                    addLabel(existing_labels, label, base_url, issueId, headers)

                                else:
                                    print("No Issues found to update") 

def main():
    '''
    Main fuction will take one argument (token: gitlab api token) and run updateIssue function
    
    '''
    parser = argparse.ArgumentParser(description="Find and Update (if needed) Gitlab Issues based on Label and last updated date")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for auth")

    args = parser.parse_args()

    updateIssues(args.token)

if __name__ == "__main__":
    main()
