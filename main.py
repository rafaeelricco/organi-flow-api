import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import json
from pathlib import Path

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

# Funções para carregar/salvar tree.json
def load_tree():
    try:
        with open(Path("tree.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"name": "Root", "attributes": {}, "children": []}

def save_tree(data: dict):
    with open(Path("tree.json"), "w") as f:
        json.dump(data, f, indent=2)

# Atualiza o lifespan para usar tree.json
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

# Cria a aplicação após definir o lifespan
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class TreeNode(BaseModel):
    name: str
    attributes: dict
    children: list["TreeNode"]

class ApiInfo(BaseModel):
    api: str
    version: str
    date_created: str
    database: Optional[str] = None

    class Config:
        from_attributes = True

class SwapPositionsRequest(BaseModel):
    employee1_id: int
    employee2_id: int
    new_manager1_id: Optional[int]
    new_manager2_id: Optional[int]

class EmployeeUpdateItem(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int] = None

class BatchUpdateRequest(BaseModel):
    employees: list[EmployeeUpdateItem]

class EmployeeManagerUpdate(BaseModel):
    id: int = Field(..., alias="id")
    new_manager_id: int = Field(..., alias="new_manager_id")

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
            content={"status": "success", "code": 200, "message": "Árvore atualizada com sucesso"}
        )
    except Exception as e:
        logger.error(f"Error in update_manager: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Falha na atualização", "code": 500, "message": str(e)}
        )

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
        return None  # Não podemos remover a raiz
    
    queue = [tree]
    while queue:
        current = queue.pop(0)
        for i, child in enumerate(current["children"]):
            if child["attributes"]["id"] == target_id:
                # Remove o nó da lista de filhos atual
                removed_node = current["children"].pop(i)
                return removed_node
            queue.append(child)
    return None

def is_descendant(parent_node: dict, target_id: int) -> bool:
    """Verifica se o target_id existe na subárvore do parent_node"""
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

@app.post("/update-employee-manager")
async def update_employee_manager(update_data: EmployeeManagerUpdate):
    try:
        tree = load_tree()
        
        # Validação: Novo manager deve existir
        new_manager_node = find_employee_in_tree(tree, update_data.new_manager_id)
        if not new_manager_node:
            raise HTTPException(status_code=404, detail="Novo manager não encontrado")
        
        # Validação: Impedir self-manager
        if update_data.id == update_data.new_manager_id:
            raise HTTPException(status_code=400, detail="Um funcionário não pode ser manager de si mesmo")
        
        # Encontrar o nó do funcionário na árvore original para validação
        employee_node_in_tree = find_employee_in_tree(tree, update_data.id)
        if not employee_node_in_tree:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        # Validação: Prevenir loop hierárquico
        if is_descendant(employee_node_in_tree, update_data.new_manager_id):
            raise HTTPException(status_code=400, detail="Criação de loop hierárquico não permitida")
        
        # Encontra e remove o funcionário da posição atual
        employee_node = find_and_remove_employee(tree, update_data.id)
        if not employee_node:
            raise HTTPException(status_code=404, detail="Funcionário não encontrado")
        
        # Atualiza o manager_id no nó do funcionário
        employee_node["attributes"]["manager_id"] = update_data.new_manager_id
        
        # Adiciona o funcionário ao novo manager
        add_employee_to_manager(tree, update_data.new_manager_id, employee_node)
        
        save_tree(tree)
        
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Manager atualizado e estrutura modificada"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in update_employee_manager: {e}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Falha na atualização", "code": 500, "message": str(e)}
        )
