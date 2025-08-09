from langchain.tools import tool
from utils import youtrack_get, youtrack_set

@tool
def list_projects() -> str:
    """List all YouTrack projects"""
    try:
        projects = youtrack_get.get_projects()
        return str(projects)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def list_issues_from_project(project_id: str) -> str:
    """List all YouTrack issues in a project"""
    try:
        issues = youtrack_get.get_issues(project_id)
        return str(issues)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def list_work_items_from_issue(issue_id: str) -> str:
    """List all YouTrack work items in an issue"""
    try:
        work_items = youtrack_get.get_work_items(issue_id)
        return str(work_items)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def create_work_item(issue_id: str, duration: int, date: str, description: str = "") -> str:
    """Create a work item in a YouTrack issue"""
    try:
        result = youtrack_set.set_work_item(issue_id, duration, date, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"