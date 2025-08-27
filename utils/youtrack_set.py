from datetime import datetime
from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection
from .youtrack_auth import get_session

yt_client = get_session()

def create_project(name, description):
    collection = ProjectsCollection(yt_client)
    project_data = {
        "description": description,
        "name": name
    }
    return collection.create_project(project_data)

def create_issue(project_id, summary, description):
    collection = IssueCollection(yt_client)
    issue_data = {
        "summary": summary,
        "description": description,
        "project": {
            "id": project_id
        }
    }
    return collection.create_issue(issue_data)

def add_work_item(issue_id, duration, date, description=""):
    issue = IssueResource(yt_client, issue_id)
    date_obj = datetime.strptime(date, '%Y/%m/%d')
    date_timestamp = int(date_obj.timestamp() * 1000)
    data = {
            "duration": {
                "minutes": int(duration)
            },
            "date": date_timestamp,
            "text": description
        }
    return issue.add_work_item(data)