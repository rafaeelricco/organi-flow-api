import logging
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import engine, Employee, Base
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

logging.basicConfig(level=logging.DEBUG) 
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from sqlalchemy import select

    db = SessionLocal()
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    
        if not db.scalar(select(Employee.id)):
            from seed_data import sample_data
            unique_data = {item['id']: item for item in sample_data}.values()
            db.bulk_insert_mappings(Employee, unique_data)
            db.commit()
        yield
    finally:
        db.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

class UpdateManagerRequest(BaseModel):
    employee_id: int
    manager_id: Optional[int] = None
    position: Optional[int] = None

class EmployeeResponse(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int]
    position: Optional[int]
    subordinates: list["EmployeeResponse"] = Field(default_factory=list)

    class Config:
        from_attributes = True

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
    position: Optional[int] = None

class BatchUpdateRequest(BaseModel):
    employees: list[EmployeeUpdateItem]

def serialize_employee(emp, seen=None):
    """
    Converte um objeto Employee em EmployeeResponse,
    evitando entrar em loop se houver ciclos na hierarquia.
    """
    if seen is None:
        seen = set()

    if emp.id in seen:
        # Se esse empregado já foi visitado, interrompe a recursão retornando
        # os dados básicos sem subordinates para evitar ciclos.
        return EmployeeResponse(
            id=emp.id,
            name=emp.name,
            title=emp.title,
            manager_id=emp.manager_id,
            position=emp.position,
            subordinates=[]
        )
    
    novo_seen = seen.union({emp.id})
    # Converte recursivamente cada subordinate
    subs = [serialize_employee(sub, novo_seen) for sub in emp.subordinates]
    
    return EmployeeResponse(
        id=emp.id,
        name=emp.name,
        title=emp.title,
        manager_id=emp.manager_id,
        position=emp.position,
        subordinates=subs
    )

@app.get("/employees", response_model=list[EmployeeResponse])
async def get_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        return [serialize_employee(emp) for emp in employees]
    except Exception as e:
        logger.error(f"Error in get_employees: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/update-manager")
async def update_manager(req: UpdateManagerRequest, db: Session = Depends(get_db)):
    """
    Atualiza o gerente de um funcionário. Garante validações como:
    - Evitar que um funcionário seja subordinado a ele mesmo.
    - Evitar ciclos hierárquicos.
    """
    try:
        # Busca o funcionário pelo ID
        emp: Employee = db.query(Employee).get(req.employee_id)
        if not emp:
            return JSONResponse(
                status_code=404,
                content={"detail": "Employee not found", "code": 404}
            )
        
        # Valida se o funcionário está tentando se gerenciar
        if req.employee_id == req.manager_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Um funcionário não pode ser seu próprio gerente", "code": 400}
            )
        
        # Função para verificar ciclos hierárquicos
        def has_cycles(current_id, manager_id):
            """
            Checa se a nova hierarquia criaria ciclos.
            """
            seen = set()
            while manager_id:
                if manager_id in seen:
                    return True  # Ciclo detectado
                seen.add(manager_id)
                manager = db.query(Employee).get(manager_id)
                if not manager:
                    break
                manager_id = manager.manager_id
            return False
        
        # Verifica se a alteração criaria um ciclo na hierarquia
        if has_cycles(req.employee_id, req.manager_id):
            return JSONResponse(
                status_code=400,
                content={"detail": "A hierarquia não pode conter ciclos", "code": 400}
            )

        # Atualiza os dados do funcionário
        emp.manager_id = req.manager_id
        if req.position is not None:
            emp.position = req.position
        
        db.commit()  # Salva as alterações no banco
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Manager updated successfully"}
        )
        
    except HTTPException as he:
        raise he  # Repassa qualquer exceção HTTP
    except Exception as e:
        db.rollback()  # Reverte alterações em caso de erro
        return JSONResponse(
            status_code=500,
            content={"detail": "Update failed", "code": 500, "message": str(e)}
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
