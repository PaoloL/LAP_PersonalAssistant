from youtrack_lap import Issue, Project
from .youtrack_auth import yt_client

def set_project(project_id, name, description=""):
    return yt_client.create_project(project_id, name, description)

def set_issue(project_id, summary, description=""):
    project = Project(yt_client, project_id)
    return project.create_issue(summary, description)

def set_work_item(issue_id, duration, date, description=""):
    issue = Issue(yt_client, issue_id)
    return issue.add_work_item(duration, date=date, description=description)