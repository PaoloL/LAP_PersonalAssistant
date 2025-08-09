from fastmcp import FastMCP
from utils import youtrack_get, youtrack_set
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

mcp = FastMCP("youtrack_server")

@mcp.tool()
def list_projects() -> str:
    """List all YouTrack projects"""
    try:
        projects = youtrack_get.get_projects()
        return str(projects)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_issues_from_project(project_id: str) -> str:
    """List all YouTrack issues in a project"""
    try:
        issues = youtrack_get.get_issues(project_id)
        return str(issues)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def list_work_items_from_issue(issue_id: str) -> str:
    """List all YouTrack work items in an issue"""
    try:
        work_items = youtrack_get.get_work_items(issue_id)
        return str(work_items)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_project(project_id: str, name: str, description: str = "") -> str:
    """Create a new YouTrack project"""
    try:
        result = youtrack_set.set_project(project_id, name, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_issue(project_id: str, summary: str, description: str = "") -> str:
    """Create a new issue in a YouTrack project"""
    try:
        result = youtrack_set.set_issue(project_id, summary, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def create_work_item(issue_id: str, duration: int, date: str, description: str = "") -> str:
    """Create a work item in a YouTrack issue"""
    try:
        result = youtrack_set.set_work_item(issue_id, duration, date, description)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"