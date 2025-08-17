from datetime import datetime
from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection
from .youtrack_auth import get_session

yt_client = get_session()

def set_project(project_id, name, description=""):
    project = ProjectsResource(yt_client, project_id)
    return project.create_project(name, description)

def set_issue(project_id, summary, description=""):
    issue = IssueCollection(yt_client, project_id)
    return issue.create_issue(summary, description)

def set_work_item(issue_id, duration, date, description=""):
    issue = IssueResource(yt_client, issue_id)
    date_obj = datetime.strptime(date, '%m/%d/%Y')
    date_timestamp = int(date_obj.timestamp() * 1000)
    data = {
            "duration": {
                "minutes": int(duration)
            },
            "date": date_timestamp,
            "text": description
        }
    return issue.add_work_item(data)