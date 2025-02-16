from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import engine, Employee
from sqlalchemy.orm import sessionmaker
from typing import Optional
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

Session = sessionmaker(bind=engine)
db = Session()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    from database import Employee
    from sqlalchemy import select
    
    if not db.scalar(select(Employee.id)):
        from seed_data import sample_data
        db.bulk_insert_mappings(Employee, sample_data)
        db.commit()
    yield
    # Shutdown code (optional)
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

class EmployeeResponse(BaseModel):
    id: int
    name: str
    title: str
    manager_id: Optional[int]
    subordinates: list = Field(default_factory=list)

    class Config:
        from_attributes = True

# Modelo para as informações da API (ApiInfo)
class ApiInfo(BaseModel):
    api: str
    version: str
    date_created: str
    database: Optional[str] = None

    class Config:
        from_attributes = True

@app.get("/employees", response_model=list[EmployeeResponse])
async def get_hierarchy():
    try:
        # Get all employees and let SQLAlchemy handle the relationships
        employees = db.query(Employee).filter(Employee.manager_id.is_(None)).all()
        
        # Ensure subordinates is always a list
        result = []
        for emp in employees:
            emp_dict = {
                "id": emp.id,
                "name": emp.name,
                "title": emp.title,
                "manager_id": emp.manager_id,
                "subordinates": emp.subordinates or []  # Garante que seja uma lista vazia se for None
            }
            result.append(emp_dict)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update-manager")
async def update_manager(req: UpdateManagerRequest):
    try:
        emp = db.query(Employee).get(req.employee_id)
        if not emp:
            return JSONResponse(
                status_code=404,
                content={"detail": "Employee not found", "code": 404}
            )
        
        emp.manager_id = req.manager_id
        db.commit()
        return JSONResponse(
            status_code=200,
            content={"status": "success", "code": 200, "message": "Manager updated successfully"}
        )
        
    except HTTPException as he:
        raise he
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"detail": "Update failed", "code": 500, "message": str(e)}
        )

# Novo endpoint raiz para verificação de status da API
@app.get("/", response_model=ApiInfo)
async def root():
    api_info = ApiInfo(
        api="organi-flow-api",
        version="1.0.0", 
        date_created=datetime.now(timezone.utc).strftime("%d-%m-%Y"),
        database="sqlite"
    )
    return api_info
