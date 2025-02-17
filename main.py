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
