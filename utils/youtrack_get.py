from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection
from .youtrack_auth import get_session

yt_client = get_session()

def get_projects(fields):
    
    has_more = True
    limit = 10
    skip = 0
    projects_list = []
    prj_collection = ProjectsCollection(yt_client)    
    
    while has_more:
        list_of_project = prj_collection.list_projects(fields="id,name,archived,team(name)",top=limit, skip=skip)
        if not list_of_project:
            has_more = False
        else:
            for item in list_of_project:
                projects_list.append(item)
            skip += limit
            break
    return list_of_project
    
def get_issues(project_id):
    project = ProjectsResource(yt_client, project_id)
    list_of_issues = project.list_issues()
    return list_of_issues

def get_work_items(issue_id):
    issue_resource = IssueResource(yt_client, issue_id)
    list_of_work_items = issue_resource.list_work_items()
    return list_of_work_items
