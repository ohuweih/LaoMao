import requests
import argparse
import yaml
import re
from itertools import cycle

color_palette = ['#cc338b','#dc143c','#c21e56','#cd5b45','#ed9121',
                 '#eee600','#009966','#8fbc8f','#6699cc','#e6e6fa',
                 '#9400d3','#330066','#36454f','#808080']
color_cycle = cycle(color_palette)

def loadFile():
    with open('./config/labelsConfig.yaml', 'r') as file:
        labels = yaml.safe_load(file)
    return labels


def get_labels(project_id, token, base_url):
    headers = {"PRIVATE-TOKEN": token}
    params = {"per_page": "100"}
    response = requests.get(base_url, params=params, headers=headers)
    labels = response.json()
    while "next" in response.links:
        print("Iterating though project labels")
        response = requests.get(response.links["next"]["url"], headers=headers)
        labels.extend(response.json())
    return labels


def labelActions(token):
    labels = loadFile()
    headers = {"PRIVATE-TOKEN": token}
    pattern = r'^[a-zA-Z]+([A-Z][a-z]+)+$'

    ## Runs through our deleteLabels list and deletes them. 
    if labels['deleteLabels']:
        print("Running thourgh the delete labels list")
        for label in labels['deleteLabels']:
            base_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels"
            createdLabels = get_labels(label['projectNumber'], token, base_url)
            if any(createdLabel["name"] == label['name'] for createdLabel in createdLabels):
                delete_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels/{label['name']}"
                response = requests.delete(delete_url, headers=headers)
                if response.status_code == 204:
                    print(f"Deleted label {label['name']}")
                else:
                    print(f"Failed to delete label {label['name']}, Status Code: {response.status_code}, Response Text: {response.text}")
            else:
                print(f"Label {label['name']} is already deleted")

    ## Runs through our Labels list and creates them
    if labels['labels']:
        print("Running thourgh the create labels list")
        for label in labels['labels']:
            for child in label['children']:
#                isCamelCase = bool(re.match(pattern, label['name']))
#                if isCamelCase == True:
                    base_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels"
                    createdLabels = get_labels(label['projectNumber'], token, base_url)
                # Check for existing label and differences 
                    matching_label = next( 
                        ( createdLabel for createdLabel in createdLabels 
                        if createdLabel["name"] == label['name'] + child['name'] ), None )
                    if matching_label: 
                        print(matching_label)
                        if ( matching_label['description'] != child['description'] or matching_label['priority'] != child.get('priority', None) or matching_label['color'] != label['color']): 
                            print(f"Label {label['name']}{child['name']} already exists but needs updating.") 
                            print("Updating label with config file.")
                            update_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels/{label['name']}{child['name']}"
                            label_data = {"color": label.get('color', matching_label['color']), "description": child['description'], "id": label['projectNumber'], "priority": child.get('priority', '')}
                            response = requests.put(update_url, data=label_data, headers=headers)
                            if response.status_code == 200:
                                print(f"Updated label {label['name']}{child['name']}") 
                                if child.get('groupLabel', False) == True:
                                    print('Promoting to Group Label')
                                    promote_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels/{label['name']}{child['name']}/promote"
                                    response = requests.put(promote_url, headers=headers)
                                    if response.status_code == 200:
                                        print(f"Label {label['name']}{child['name']} promoted to group label")
                                    else:
                                        print(f"Failed to Promote label {label['name']}{child['name']}, State Code: {response.status_code}, Response Text: {response.text}")
                            else:
                                print(f"Failed to update label {label['name']}{child['name']}, State Code: {response.status_code}, Response Text: {response.text}")
                        else:
                            print(f"Label {label['name']}{child['name']} already exists and nothing to update")
                    else:
                        print(f"Label {label['name']}{child['name']} not created, Creating")
                        assigned_color = next(color_cycle)
                        label_data = {"name": label['name'] + child['name'], "color": label['color'], "description": child['description'], "id": label['projectNumber'], "priority": child.get('priority', '')}
                        response = requests.post(base_url, data=label_data, headers=headers)
                        if response.status_code == 201:
                            print(f"Created label {label['name']}{child['name']}")
                            if child.get('groupLabel', False) == True:
                                print('Promoting to Group Label')
                                promote_url = f"https://gitlab.com/api/v4/projects/{label['projectNumber']}/labels/{label['name']}{child['name']}/promote"
                                response = requests.put(promote_url, headers=headers)
                                if response.status_code == 200:
                                    print(f"Label {label['name']}{child['name']} promoted to group label")
                                else:
                                    print(f"Failed to Promote label {label['name']}{child['name']}, State Code: {response.status_code}, Response Text: {response.text}")
                        else:
                            print(f"Failed to create label {label['name']}{child['name']}, State Code: {response.status_code}, Response Text: {response.text}")
#                else:
#                    print(f"Label name {label['name']}{child['name']} is not Camel Cased Please make it Camel Cased in order to proceed.")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create / Update / or Delete Gitlab labels")
    parser.add_argument("-t", "--token", required=True, help="GitLab private token for auth")

    args = parser.parse_args()

    labelActions(args.token)

if __name__ == "__main__":
    main()
