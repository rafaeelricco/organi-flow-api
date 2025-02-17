import logging
import json
from typing import Optional
from pathlib import Path
from fastapi import HTTPException
logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

def find_employee_in_tree(node: dict, target_id: int) -> Optional[dict]:
    if node["attributes"]["id"] == target_id:
        return node
    for child in node["children"]:
        result = find_employee_in_tree(child, target_id)
        if result:
            return result
    return None

def find_and_remove_employee(tree: dict, target_id: int) -> Optional[dict]:
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
    if parent_node["attributes"]["id"] == target_id:
        return True
    for child in parent_node["children"]:
        if is_descendant(child, target_id):
            return True
    return False

def add_employee_to_manager(tree: dict, manager_id: int, employee_node: dict):
    manager_node = find_employee_in_tree(tree, manager_id)
    if manager_node:
        manager_node["children"].append(employee_node)
    else:
        raise ValueError("Manager não encontrado")

def load_tree():
    try:
        tree_path = Path("tree.json")
        if tree_path.exists():
            tree_path.chmod(0o644)
        with open(tree_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "Root", "attributes": {}, "children": []}
    except PermissionError as e:
        logger.error(f"Erro de permissão ao ler tree.json: {e}")
        raise HTTPException(status_code=500, detail="Erro de permissão ao acessar dados")

def save_tree(data: dict):
    try:
        tree_path = Path("tree.json")
        tree_path.parent.chmod(0o755)
        with open(tree_path, "w") as f:
            json.dump(data, f, indent=2)
        tree_path.chmod(0o644)
    except PermissionError as e:
        logger.error(f"Erro de permissão ao salvar tree.json: {e}")
        raise HTTPException(status_code=500, detail="Erro de permissão ao salvar dados")
