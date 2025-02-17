import logging
import json
from typing import Optional
from pathlib import Path
from fastapi import HTTPException
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

def find_employee_in_tree(node: dict, target_id: int) -> Optional[dict]:
    """
    Recursively searches for an employee in the organizational tree by their ID.
    
    Args:
        node (dict): The current node in the tree to search
        target_id (int): The ID of the employee to find
        
    Returns:
        Optional[dict]: The found employee node or None if not found
        
    Note:
        This function traverses the tree recursively, checking each node and its children
    """
    if node["attributes"]["id"] == target_id:
        return node
    for child in node["children"]:
        result = find_employee_in_tree(child, target_id)
        if result:
            return result
    return None

def find_and_remove_employee(tree: dict, target_id: int) -> Optional[dict]:
    """
    Locates and removes an employee from the organizational tree.
    
    Args:
        tree (dict): The organizational tree structure
        target_id (int): The ID of the employee to remove
        
    Returns:
        Optional[dict]: The removed employee node or None if not found
        
    Note:
        Uses breadth-first search to find and remove the employee while preserving
        the tree structure
    """
    if tree["attributes"]["id"] == target_id:
        return None
    
    queue = [tree]
    while queue:
        current = queue.pop(0)
        for i, child in enumerate(current["children"]):
            if child["attributes"]["id"] == target_id:
                removed_node = current["children"].pop(i)
                return removed_node
            queue.append(child)
    return None

def is_descendant(parent_node: dict, target_id: int) -> bool:
    """
    Checks if a given employee ID exists in the descendant hierarchy of a node.
    
    Args:
        parent_node (dict): The node to check descendants from
        target_id (int): The employee ID to search for
        
    Returns:
        bool: True if target_id is found in descendants, False otherwise
        
    Note:
        Used to prevent circular reporting relationships in the organizational structure
    """
    if parent_node["attributes"]["id"] == target_id:
        return True
    for child in parent_node["children"]:
        if is_descendant(child, target_id):
            return True
    return False

def add_employee_to_manager(tree: dict, manager_id: int, employee_node: dict):
    """
    Adds an employee node under a specified manager in the organizational tree.
    
    Args:
        tree (dict): The organizational tree structure
        manager_id (int): The ID of the manager to add the employee under
        employee_node (dict): The employee node to be added
        
    Raises:
        ValueError: If the specified manager is not found in the tree
        
    Note:
        This function modifies the tree structure in-place
    """
    manager_node = find_employee_in_tree(tree, manager_id)
    if manager_node:
        manager_node["children"].append(employee_node)
    else:
        raise ValueError("Manager not found")

def load_tree():
    """
    Loads the organizational tree structure from a JSON file.
    
    Returns:
        dict: The loaded tree structure or a new empty tree if file doesn't exist
        
    Raises:
        HTTPException: 500 status code if there's a permission error accessing the file
        
    Note:
        Creates a default empty tree if no existing structure is found
        Sets appropriate file permissions (0o644) for security
    """
    try:
        tree_path = Path("tree.json")
        if tree_path.exists():
            tree_path.chmod(0o644)
        with open(tree_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "Root", "attributes": {}, "children": []}
    except PermissionError as e:
        logger.error(f"Permission error reading tree.json: {e}")
        raise HTTPException(status_code=500, detail="Permission error accessing data")

def save_tree(data: dict):
    """
    Saves the organizational tree structure to a JSON file.
    
    Args:
        data (dict): The tree structure to save
        
    Raises:
        HTTPException: 500 status code if there's a permission error saving the file
        
    Note:
        Sets appropriate file permissions:
        - Directory: 0o755
        - File: 0o644
        Formats JSON with indentation for readability
    """
    try:
        tree_path = Path("tree.json")
        tree_path.parent.chmod(0o755)
        with open(tree_path, "w") as f:
            json.dump(data, f, indent=2)
        tree_path.chmod(0o644)
    except PermissionError as e:
        logger.error(f"Permission error saving tree.json: {e}")
        raise HTTPException(status_code=500, detail="Permission error saving data")
