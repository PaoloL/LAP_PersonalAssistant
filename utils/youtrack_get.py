from youtrack_lap import Issue, Project
from .youtrack_auth import yt_client

def get_projects():
    return yt_client.get_projects()

def get_issues(project_id):
    project = Project(yt_client, project_id)
    return project.get_issues()

def get_work_items(issue_id):
    issue = Issue(yt_client, issue_id)
    return issue.get_work_items()
