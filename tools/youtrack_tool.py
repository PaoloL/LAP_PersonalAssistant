from langchain.tools import tool
from utils import youtrack_get, youtrack_set
from youtrack_lap import Connection, ProjectsCollection, ProjectsResource, IssueResource, IssueCollection

LIMIT=1000
@tool
def list_active_projects_name():
    """Get all active YouTrack project names.
    
    Returns a list of active (non-archived) project names from YouTrack.
    Use this when you need to see what projects are available for work logging.
    
    Returns:
        List of dictionaries with 'name' key containing project names
    """
    try:
        # Get all projects with specific fields
        projects = youtrack_get.list_projects(LIMIT)
        active_projects = []
        for project in projects:
            # Get only the not archived project
            if not project.get('archived', True):
                active_projects.append({'name': project.get('name')})
        return active_projects
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_issue_names_by_projectName(project_name: str):
    """Get all issue names/summaries from a specific YouTrack project.
    
    Args:
        project_name (str): The exact name of the YouTrack project
        
    Returns:
        List of issue names (summaries) from the specified project.
        Use this to see what issues are available in a project for work logging.
    """
    try:
        issues = youtrack_get.list_issues_from_projectName(project_name, LIMIT)
        issue_names = []
        for issue in issues:
            if issue.get('summary'):
                issue_names.append(issue.get('summary'))
            else:
                issue_names.append(issue.get('id'))
        return issue_names
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_project_id_from_project_name(project_name):
    """Convert a YouTrack project name to its internal project ID.
    
    Args:
        project_name (str): The exact name of the YouTrack project
        
    Returns:
        String containing the project ID (e.g., "0-1", "0-2")
        Use this ID for API calls that require project identification.
    """
    try:
        projects = youtrack_get.list_projects(LIMIT)
        for project in projects:
            if project.get('name') == project_name:
                return project.get('id')
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def get_issue_id_from_issue_name(issue_name):
    """Convert a YouTrack issue name/summary to its internal issue ID.
    
    Args:
        issue_name (str): The exact summary/title of the YouTrack issue
        
    Returns:
        String containing the issue ID (e.g., "2-575", "2-2994")
        Use this ID for API calls that require issue identification.
    """
    try:
        issues_list = youtrack_get.convert_issueName_to_issueId(issue_name, LIMIT)
        if issues_list and len(issues_list) > 0:
            return issues_list[0].get('id')
            
        else:
            return "AI-121"
    except Exception as e:
        print("ERROR")
        print(f"IF {issue_name}")
        print(issues_list)
        return f"Error: {str(e)}"
        # give more detaisl on errror


@tool
def create_work_item_by_issue_name(issue_name: str, duration: int, date: str, description: str = "") -> str:
    """Create a work item (time entry) in YouTrack by searching for issue name.
    
    Args:
        issue_name (str): The exact summary/title of the YouTrack issue
        duration (int): Work duration in minutes (e.g., 60 for 1 hour)
        date (str): Date in format dd/mm/yyyy (e.g., "25/05/2025")
        description (str): Optional description of the work performed
        
    Returns:
        Success/failure message from YouTrack API
        
    Note: This searches through all projects to find the issue by name.
    """
    try:
        # Get all projects with specific fields
        projects = youtrack_get.get_projects("id, name")
        for project in projects:
            issues = youtrack_get.get_issues(project.get('id'))
            for issue in issues:
                if issue.get('summary') == issue_name:
                    result = youtrack_set.set_work_item(issue.get('id'), duration, date, description)
                    return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@tool
def create_work_item_by_issue_id(issue_id: str, duration: int, date: str, description: str = "") -> str:
    """Create a work item (time entry) in YouTrack using the issue ID directly.
    
    Args:
        issue_id (str): The YouTrack issue ID (e.g., "2-575", "2-2994")
        duration (int): Work duration in minutes (e.g., 60 for 1 hour, 480 for 8 hours)
        date (str): Date in format yyyy/mm/dd (e.g., "2025/05/25")
        description (str): Optional description of the work performed
        
    Returns:
        Success/failure message from YouTrack API
        
    Note: This is more efficient than searching by name. Use get_issue_id_from_issue_name first.
    """
    try:
        result = youtrack_set.add_work_item(issue_id, duration, date, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"
