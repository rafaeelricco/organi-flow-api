"""
            _                      
   _____   (_)  _____  _____  ____ 
  / ___/  / /  / ___/ / ___/ / __ \
 / /     / /  / /__  / /__  / /_/ /
/_/     /_/   \___/  \___/  \____/ 
                                   
© r1cco.com

FastAPI Application Module

This module implements a REST API for managing organizational hierarchies. It provides
endpoints for viewing and modifying employee-manager relationships while maintaining
the integrity of the organizational structure.

Key Features:
1. Tree-based organization structure management
2. Employee-manager relationship updates
3. Hierarchical loop prevention
4. Data persistence using JSON storage
5. CORS support for cross-origin requests

The API ensures data consistency and prevents invalid organizational structures
such as self-management or circular reporting relationships.
"""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from pathlib import Path

from classes import TreeNode, ApiInfo, EmployeeManagerUpdate
from functions import find_employee_in_tree, is_descendant, load_tree, save_tree

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    
    Initializes the application by creating a default organizational structure
    if no existing tree.json file is found.
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None
        
    Note:
        Creates a default CEO node if no existing structure is found
    """
    try:
        if not Path("tree.json").exists():
            save_tree({
                "name": "John Smith",
                "attributes": {"id": 1, "title": "CEO", "manager_id": 0},
                "children": []
            })
        yield
    finally:
        pass

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/", response_model=ApiInfo)
async def root():
    """
    Provides basic API information and health check endpoint.
    
    Returns:
        ApiInfo: Object containing API metadata including:
            - api name
            - version
            - creation date
            - database type
    """
    api_info = ApiInfo(
        api="organi-flow-api",
        version="1.0.0", 
        date_created=datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        database="json"
    )
    return api_info

@app.get("/employees", response_model=TreeNode)
async def get_employees():
    """
    Retrieves the complete organizational structure.
    
    Returns:
        TreeNode: The complete organizational tree structure
        
    Raises:
        HTTPException: 500 status code if there's an error loading the tree
    """
    try:
        return load_tree()
    except Exception as e:
        logger.error(f"Error in get_employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-manager")
async def update_tree(tree_data: TreeNode):
    """
    Updates the entire organizational tree structure.
    
    Args:
        tree_data (TreeNode): The complete new tree structure to save
        
    Returns:
        JSONResponse: Success or failure message with appropriate status code
        
    Note:
        This endpoint replaces the entire existing tree with the new structure
    """
    try:
        save_tree(tree_data.model_dump())
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Tree updated successfully"}
        )
    except Exception as e:
        logger.error(f"Error in update_manager: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Update failed", "code": 500, "message": str(e)}
        )

@app.post("/update-employee-manager")
async def update_employee_manager(update_data: EmployeeManagerUpdate):
    """
    Versão que atualiza apenas os manager_ids sem remover os nós
    """
    try:
        tree = load_tree()
        
        # Encontrar os funcionários sem remover
        employee_a = find_employee_in_tree(tree, update_data.employee_id)
        employee_b = find_employee_in_tree(tree, update_data.target_id)
        
        if not employee_a or not employee_b:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
            
        # Manter cópia dos managers originais
        original_manager_a = employee_a["attributes"]["manager_id"]
        original_manager_b = employee_b["attributes"]["manager_id"]
        
        # Verificar hierarquia circular
        if is_descendant(employee_a, employee_b["attributes"]["id"]) or is_descendant(employee_b, employee_a["attributes"]["id"]):
            raise HTTPException(status_code=400, detail="Relação hierárquica inválida")
        
        # Atualizar manager_ids diretamente
        employee_a["attributes"]["manager_id"] = original_manager_b
        employee_b["attributes"]["manager_id"] = original_manager_a
        
        # Encontrar e atualizar os nós pais
        manager_a_node = find_employee_in_tree(tree, original_manager_a)
        manager_b_node = find_employee_in_tree(tree, original_manager_b)
        
        if manager_a_node and manager_b_node:
            # Remover das listas de filhos originais
            manager_a_node["children"] = [c for c in manager_a_node["children"] if c["attributes"]["id"] != employee_a["attributes"]["id"]]
            manager_b_node["children"] = [c for c in manager_b_node["children"] if c["attributes"]["id"] != employee_b["attributes"]["id"]]
            
            # Adicionar aos novos managers
            manager_b_node["children"].append(employee_a)
            manager_a_node["children"].append(employee_b)
        
        save_tree(tree)
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Relação atualizada com sucesso"}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erro grave: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "code": 500, "message": "Falha crítica na operação"}
        )
