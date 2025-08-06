
from youtrack_lap.Connection import Connection
from youtrack_lap.Issue import Issue
from youtrack_lap.Project import Project
from datetime import datetime

def set_work_items(project, duration, date, description):
    issue = Issue(client, project)
    issue.add_work_item(duration,date=date,description=description)