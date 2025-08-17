from langchain.tools import tool
from utils import youtrack_get, youtrack_set

@tool
def list_active_projects() -> str:
    """Get active projects where user is a team member"""
    # Get all projects with specific fields
    projects = youtrack_get.get_projects("id,name,archived")
    active_projects = []
    for project in projects:
        # Filter: archived=false and team contains paolo.latella
        if not project.get('archived', True):  # Not archived
            active_projects.append({
                'id': project.get('id'),
                'name': project.get('name')
            })
    return active_projects


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
    """Create a work item in a YouTrack issue. Duration should be in minutes."""
    try:
        if duration < 24 and duration > 0:
            duration_minutes = duration * 60
        else:
            duration_minutes = duration
        result = youtrack_set.set_work_item(issue_id, duration_minutes, date, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

