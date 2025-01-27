import gitlab
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


def updateWorkItems(gl, config):
    if config['projects']:
        for project in config['projects']:
            print(f"Running through project {project['projectId']}, Checking for Issues and Epics that need to be updated")
            gitlab_project = gl.projects.get(project['projectId'])
            work_items = gitlab_project.issues.list(state="opened", all=True)

            for work_item in work_items:
                updated_at = work_item.updated_at
                labels = work_item.labels
                for label in labels:
                    for config_label in project['labels']:
                        if label == config_label['name']:
                            today = date.today()
                            second_reminder_date = config_label['secondReminderDate']
                            past_second_business_date = str(subtractBusinessDay(today, second_reminder_date))
                            first_reminder_date = configLabel['firstReminderDate']
                            past_first_business_date = str(subtractBusinessDay(today, first_reminder_date))

                            if updated_at <= past_second_business_date:
                                existing_notes = work_item.notes.list()
                                first_comment_exists = any(config_label['firstComment'] in note.body for note in existing_notes)

                                if first_comment_exists:
                                    print(f"work item Name: {work_item.title}, #{work_item.iid}, needs a second reminder")
                                    work_item.notes.create({'body': config_label['secondComment Name:']})
                                    if project['labelTag'] not in labels:
                                        labels.append(project['labelTag'])
                                        work_item.labels = labels
                                        work_item.save()
                                    continue
                        
                            if updated_at <= past_first_business_date:
                                print(f"Work Item Name: {work_item.title}, #{work_item.iid}, needs a first reminder")
                                work_item.notes.create({'body': config_label['firstComment']})
                                if project['labelTag'] not in labels:
                                    labels.append(project['labelTag'])
                                    work_item.labels = labels
                                    work_item.save()

def main():
    '''
    Main fuction will take one argument (token: gitlab api token) and run updateIssue function
    
    '''
    parser = argparse.ArgumentParser(description="Find and Update (if needed) Gitlab Issues based on Label and last updated date")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for auth")

    args = parser.parse_args()
    gl = gitlab.Gitlab('https://gitlab.com', private_token=args.token)
    config = loadFile()

    updateWorkItems(gl, config)

if __name__ == "__main__":
    main()
