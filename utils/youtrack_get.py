from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection
from .youtrack_auth import get_session


yt_client = get_session()

def list_projects(limit):
    collection = ProjectsCollection(yt_client)
    projects_list = collection.list_projects(fields="id,name,archived,team(name)", top=limit, skip=0)
    return projects_list

def list_issues_from_projectName(project_name, limit):
    query = f"project: {{{project_name}}}" 
    collection = IssueCollection(yt_client)
    issues_list = collection.list_issues(fields="id,summary", top=limit, skip=0, query=query )
    return issues_list

def list_issues_from_projectId(project_id, limit):
    query = f"project: {{{project_id}}}" 
    collection = IssueCollection(yt_client)
    issues_list = collection.list_issues(fields="id,summary", top=limit, skip=0, query=query )
    return issues_list

def convert_issueName_to_issueId(summary,limit):
    query = f"summary: {{{summary}}}"
    collection = IssueCollection(yt_client)
    issues_list = collection.list_issues(fields="id,summary", top=limit, skip=0, query=query )
    return issues_list

def list_work_items_from_issueId(issue_id, limit):
    query = f"issue: {{{issue_id}}}"
    resource = IssueCollection(yt_client)
    issues_list = resource.list_issues(fields="id, summary", top=limit, skip=0, query=query)
    return issues_list
