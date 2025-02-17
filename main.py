import logging

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from pathlib import Path

from classes import TreeNode, ApiInfo, EmployeeManagerUpdate
from functions import find_employee_in_tree, find_and_remove_employee, is_descendant, add_employee_to_manager, load_tree, save_tree

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    api_info = ApiInfo(
        api="organi-flow-api",
        version="1.0.0", 
        date_created=datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        database="sqlite"
    )
    return api_info

@app.get("/employees", response_model=TreeNode)
async def get_employees():
    try:
        return load_tree()
    except Exception as e:
        logger.error(f"Error in get_employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-manager")
async def update_tree(tree_data: TreeNode):
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
    try:
        tree = load_tree()
        
        new_manager_node = find_employee_in_tree(tree, update_data.new_manager_id)
        if not new_manager_node:
            raise HTTPException(status_code=404, detail="New manager not found")
        
        if update_data.id == update_data.new_manager_id:
            raise HTTPException(status_code=400, detail="An employee cannot be their own manager")
        
        employee_node_in_tree = find_employee_in_tree(tree, update_data.id)
        if not employee_node_in_tree:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        if is_descendant(employee_node_in_tree, update_data.new_manager_id):
            raise HTTPException(status_code=400, detail="Hierarchical loop creation not allowed")
        
        employee_node = find_and_remove_employee(tree, update_data.id)
        if not employee_node:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        employee_node["attributes"]["manager_id"] = update_data.new_manager_id
        
        add_employee_to_manager(tree, update_data.new_manager_id, employee_node)
        
        save_tree(tree)
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Manager updated and structure modified"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in update_employee_manager: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Update failed", "code": 500, "message": str(e)}
        )
