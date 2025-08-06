import os
from youtrack_lap.Connection import Connection
from youtrack_lap.Issue import Issue
from youtrack_lap.Project import Project
from datetime import datetime

YOUTRACK_URL = "https://r3recube.myjetbrains.com/youtrack/"

def read_token_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Token file not found: {file_path}")
        exit(1)
        return None

#Initialize the Authenticated Client
token_file = os.path.expanduser("secrets/yt_token.txt")
YOUTRACK_TOKEN = read_token_from_file(token_file)
client = Connection(base_url=YOUTRACK_URL, token=YOUTRACK_TOKEN)

def get_projects():
    has_more = True
    items_limit = 10
    skip = 0
    projects_list = []

    while has_more:
        projects = client.get_projects(limit=items_limit, skip=skip)
        if not projects:
            has_more = False
        else:
            for item in projects:
                projects_list.append(item)
            skip += items_limit
            break
    return projects_list

def get_project_issues(project):
    issue = Issue(client, project)
    has_more = True
    items_limit = 10
    skip = 0
    issues_list = []

    while has_more:
        issues = issue.get_issues(limit=items_limit, skip=skip)
        if not issues:
            has_more = False
        else:
            for item in issues:
                issues_list.append(item)
            skip += items_limit
            break
    return issues_list

def get_work_items(project):
    issue = Issue(client, project)
    has_more = True
    items_limit = 10
    skip = 0
    issues_list = []
    
    while has_more:
        issues = issue.get_work_items(limit=items_limit, skip=skip)
        if not issues:
            has_more = False
        else:
            for item in issues:
                issues_list.append(item)
            skip += items_limit
            break
    return issues_list
